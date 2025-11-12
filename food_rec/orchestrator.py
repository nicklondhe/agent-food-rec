"""Core orchestrator for iterative food search."""

import json
import os
import re
import traceback
from typing import Optional

from anthropic import Anthropic, APIError

from food_rec.criteria import should_stop_searching
from food_rec.models import Dish, SearchResult
from food_rec.scorer import rank_dishes


class FoodRecommendationOrchestrator:
    """Orchestrates the iterative search for food recommendations."""

    def __init__(self, api_key: Optional[str] = None, fast_mode: bool = True):
        """Initialize with Anthropic client."""
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        # Use faster model for extraction if in fast mode
        self.model = "claude-3-5-haiku-20241022" if fast_mode else "claude-sonnet-4-20250514"

    def _normalize_dish_name(self, name: str) -> str:
        """Normalize dish name for comparison."""
        # Convert to lowercase
        name = name.lower()
        # Remove common words like "with"
        name = re.sub(r'\b(with|and|or)\b', '', name)
        # Normalize spacing
        name = ' '.join(name.split())
        # Sort words to catch reorderings
        words = sorted(name.split())
        return ' '.join(words)

    def _are_dishes_similar(self, name1: str, name2: str) -> bool:
        """Check if two dish names are similar (fuzzy match)."""
        # Normalize both names
        norm1 = self._normalize_dish_name(name1)
        norm2 = self._normalize_dish_name(name2)

        # Exact match after normalization
        if norm1 == norm2:
            return True

        # Token-based similarity: check if one is subset of other
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())

        # If 80% of tokens overlap, consider similar
        if tokens1 and tokens2:
            overlap = len(tokens1 & tokens2)
            similarity = overlap / max(len(tokens1), len(tokens2))
            if similarity >= 0.8:
                return True

        # Simple Levenshtein-like check for very similar strings
        # (catches Puchka vs Phuchka)
        if len(norm1) > 3 and len(norm2) > 3:
            # Calculate simple edit distance approximation
            if abs(len(norm1) - len(norm2)) <= 2:
                # Count matching characters in order
                matches = sum(1 for a, b in zip(norm1, norm2) if a == b)
                if matches / max(len(norm1), len(norm2)) >= 0.85:
                    return True

        return False

    def _find_similar_dish(self, dish: Dish, existing_dishes: dict[str, Dish]) -> Optional[str]:
        """Find if a similar dish already exists. Returns the key if found."""
        for key, existing_dish in existing_dishes.items():
            if self._are_dishes_similar(dish.name, existing_dish.name):
                return key
        return None

    def search(
        self, origin: str, destination: str, target_count: int = 10
    ) -> list[Dish]:
        """
        Execute iterative search for food recommendations.

        Args:
            origin: Origin city/country
            destination: Destination city/country
            target_count: Target number of dishes to find

        Returns:
            Ranked list of dishes
        """
        print(f"\n🔍 Searching for {target_count} unique dishes")
        print(f"   Origin: {origin}")
        print(f"   Destination: {destination}\n")

        all_dishes: dict[str, Dish] = {}  # Use dict for deduplication by name
        learnings: dict[str, list[str]] = {
            "categories": [],
            "neighborhoods": [],
            "seasons": [],
            "festivals": [],
            "contexts": [],
        }
        recent_tier_results: list[int] = []

        for tier in range(1, 6):  # Tiers 1-5
            print(f"\n{'='*60}")
            print(f"🎯 TIER {tier}: {self._get_tier_name(tier)}")
            print(f"{'='*60}")

            # Generate and execute searches for this tier
            result = self._execute_tier_search(
                tier, origin, destination, learnings, all_dishes
            )

            # Update dishes and learnings (with fuzzy deduplication)
            new_dishes = 0
            for dish in result.dishes:
                # Check if similar dish already exists
                similar_key = self._find_similar_dish(dish, all_dishes)

                if similar_key is None:
                    # New unique dish
                    dish_key = dish.name.lower()
                    all_dishes[dish_key] = dish
                    new_dishes += 1
                else:
                    # Similar dish exists - keep the one with higher score
                    existing = all_dishes[similar_key]
                    if dish.dest_popularity > existing.dest_popularity:
                        # Replace with better version
                        all_dishes[similar_key] = dish

            # Merge learnings
            for key, values in result.learnings.items():
                if key in learnings:
                    learnings[key].extend(values)
                    learnings[key] = list(set(learnings[key]))  # Deduplicate

            recent_tier_results.append(new_dishes)

            print(f"\n📊 Tier {tier} Summary:")
            print(f"   - New dishes found: {new_dishes}")
            print(f"   - Total dishes: {len(all_dishes)}")
            print(f"   - Queries used: {len(result.queries_used)}")

            # Check stopping criteria
            should_stop, reason = should_stop_searching(
                list(all_dishes.values()),
                target_count,
                recent_tier_results,
                tier,
            )

            if should_stop:
                print(f"\n✅ Stopping: {reason}")
                break

            if tier < 5:
                print("\n➡️  Continuing to next tier...")

        # Final ranking
        print(f"\n\n{'='*60}")
        print("🏆 FINAL RANKING")
        print(f"{'='*60}")

        ranked_dishes = rank_dishes(list(all_dishes.values()))
        return ranked_dishes[:target_count]

    def _get_tier_name(self, tier: int) -> str:
        """Get descriptive name for tier."""
        names = {
            1: "Broad Search",
            2: "Category-Structured Search",
            3: "Hyperlocal & Neighborhood Search",
            4: "Temporal & Event-Based Search",
            5: "Ultra-Specific Combined Search",
        }
        return names.get(tier, f"Tier {tier}")

    def _execute_tier_search(
        self,
        tier: int,
        origin: str,
        destination: str,
        learnings: dict[str, list[str]],
        existing_dishes: dict[str, Dish],
    ) -> SearchResult:
        """Execute search for a specific tier."""
        # Generate queries based on tier and learnings
        queries = self._generate_tier_queries(tier, destination, learnings)

        print(f"\n🔎 Generated {len(queries)} queries for this tier:")
        for i, query in enumerate(queries, 1):
            print(f"   {i}. {query}")

        # Execute searches and extract dishes
        all_dishes: list[Dish] = []
        new_learnings: dict[str, list[str]] = {
            "categories": [],
            "neighborhoods": [],
            "seasons": [],
            "festivals": [],
            "contexts": [],
        }

        for query in queries:
            print(f"\n   🌐 Searching: {query}")
            dishes, query_learnings = self._search_and_extract(
                query, origin, destination, tier
            )

            print(f"      Found {len(dishes)} dishes")
            all_dishes.extend(dishes)

            # Merge learnings
            for key, values in query_learnings.items():
                if key in new_learnings:
                    new_learnings[key].extend(values)

        # Deduplicate learnings
        for key in new_learnings:
            new_learnings[key] = list(set(new_learnings[key]))

        return SearchResult(
            dishes=all_dishes,
            queries_used=queries,
            learnings=new_learnings,
            new_dishes_count=len(
                [d for d in all_dishes if d.name.lower() not in existing_dishes]
            ),
            tier=tier,
        )

    def _clean_learning_term(self, term: str) -> str:
        """Clean a learning term by removing brackets and extra context."""
        # Remove anything in parentheses
        term = re.sub(r'\s*\([^)]*\)', '', term)
        # Remove extra whitespace
        term = ' '.join(term.split())
        return term.strip()

    def _cleanup_queries(self, queries: list[str]) -> list[str]:
        """Clean up and deduplicate queries."""
        cleaned = []
        seen = set()

        for query in queries:
            # Remove duplicate words
            words = query.lower().split()
            seen_words = set()
            unique_words = []
            for word in words:
                if word not in seen_words:
                    unique_words.append(word)
                    seen_words.add(word)

            # Reconstruct query
            cleaned_query = ' '.join(unique_words)

            # Deduplicate (case-insensitive)
            if cleaned_query not in seen:
                cleaned.append(cleaned_query)
                seen.add(cleaned_query)

        return cleaned

    def _generate_tier_queries(
        self, tier: int, destination: str, learnings: dict[str, list[str]]
    ) -> list[str]:
        """Generate search queries based on tier and learnings (optimized for speed)."""
        queries = []

        if tier == 1:
            # Broad search - just 2 queries
            queries = [
                f"popular local food must-try dishes {destination}",
                f"traditional street food {destination}",
            ]

        elif tier == 2:
            # Category-based (use learnings from tier 1 if available)
            categories = [self._clean_learning_term(c) for c in learnings.get("categories", [])[:2]]
            if categories:
                queries = [f"{cat} specialties in {destination}" for cat in categories]
            else:
                queries = [
                    f"street food desserts {destination}",
                    f"local breakfast dishes {destination}",
                ]

        elif tier == 3:
            # Hyperlocal & neighborhoods - max 2 queries
            neighborhoods = [
                self._clean_learning_term(n)
                for n in learnings.get("neighborhoods", [])[:2]
            ]
            if neighborhoods:
                queries = [
                    f"food specialties {neighborhood} {destination}"
                    for neighborhood in neighborhoods
                ]
            else:
                queries = [f"neighborhood food specialties hidden gems {destination}"]

        elif tier == 4:
            # Temporal & events - max 2 queries
            seasons = [
                self._clean_learning_term(s)
                for s in learnings.get("seasons", [])[:1]
            ]
            festivals = [
                self._clean_learning_term(f)
                for f in learnings.get("festivals", [])[:1]
            ]

            if seasons:
                queries.append(f"{seasons[0]} seasonal dishes {destination}")
            if festivals:
                queries.append(f"{festivals[0]} festival food {destination}")

            if not queries:
                queries = [f"seasonal festival food {destination}"]

        else:  # tier == 5
            # Ultra-specific: combine learnings - max 2 queries
            categories = [
                self._clean_learning_term(c)
                for c in learnings.get("categories", [])[:1]
            ]
            neighborhoods = [
                self._clean_learning_term(n)
                for n in learnings.get("neighborhoods", [])[:1]
            ]

            if categories and neighborhoods:
                queries = [f"{categories[0]} {neighborhoods[0]} {destination}"]
            else:
                queries = [f"unique rare food experiences {destination}"]

        # Clean up and deduplicate
        return self._cleanup_queries(queries)

    def _search_and_extract(
        self, query: str, origin: str, destination: str, tier: int
    ) -> tuple[list[Dish], dict[str, list[str]]]:
        """
        Execute web search and extract dishes using Claude.

        Returns:
            (dishes, learnings) tuple
        """
        # Create prompt for Claude to search and extract
        prompt = f"""Find unique food recommendations for someone traveling from {origin} to \
{destination}.

Search Query: {query}

Use web_search to find information, then extract dishes and learnings.

CRITICAL: Return ONLY a valid JSON object. Do NOT include any explanatory text, \
markdown formatting, or commentary before or after the JSON. Your entire response must be \
ONLY the JSON object starting with {{ and ending with }}.

Required JSON structure:
{{
    "dishes": [
        {{
            "name": "Dish Name",
            "description": "Brief description (1-2 sentences)",
            "category": "street food|dessert|breakfast|etc",
            "context": "where/when to find it",
            "dest_popularity": 0.8,
            "global_commonness": 0.3,
            "origin_availability": 0.1,
            "authenticity_gap": 0.0
        }}
    ],
    "learnings": {{
        "categories": ["category1", "category2"],
        "neighborhoods": ["area1", "area2"],
        "seasons": ["season1"],
        "festivals": ["festival1"],
        "contexts": ["context1"]
    }}
}}

Estimation guidelines:
- dest_popularity: How popular/mentioned in {destination} (0-1)
- global_commonness: How common globally (0-1)
- origin_availability: Available in {origin}? (0-1)
- authenticity_gap: If in {origin}, how different in {destination}? (0-1)

Focus on dishes specific to {destination}, different from {origin}, and actually findable."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                    }
                ],
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract JSON from response
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text

            if not response_text.strip():
                print("      ⚠️  No text response from Claude")
                return [], {}

            # Parse JSON (try to extract from markdown code blocks if present)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                # Find JSON object in text (look for first { and last })
                json_str = response_text.strip()
                if "{" in json_str and "}" in json_str:
                    start_idx = json_str.find("{")
                    end_idx = json_str.rfind("}") + 1
                    json_str = json_str[start_idx:end_idx]

            if not json_str:
                print("      ⚠️  No JSON found in response")
                return [], {}

            data = json.loads(json_str)

            # Convert to Dish objects
            dishes = []
            for dish_data in data.get("dishes", []):
                dish = Dish(
                    name=dish_data["name"],
                    description=dish_data.get("description", ""),
                    category=dish_data.get("category"),
                    context=dish_data.get("context", ""),
                    dest_popularity=dish_data.get("dest_popularity", 0.5),
                    global_commonness=dish_data.get("global_commonness", 0.5),
                    origin_availability=dish_data.get("origin_availability", 0.0),
                    authenticity_gap=dish_data.get("authenticity_gap", 0.0),
                    tier_discovered=tier,
                    sources=[query],
                )
                dishes.append(dish)

            learnings = data.get("learnings", {})

            return dishes, learnings

        except json.JSONDecodeError as e:
            print(f"      ⚠️  JSON parsing error: {e}")
            if 'response_text' in locals():
                preview = (
                    response_text[:500] if len(response_text) > 500
                    else response_text
                )
                print(f"      Response preview: {preview}")
            return [], {}
        except APIError as e:
            print(f"      ⚠️  API error: {e}")
            return [], {}
        except (KeyError, AttributeError, ValueError, TypeError) as e:
            print(f"      ⚠️  Data processing error: {e}")
            traceback.print_exc()
            return [], {}
