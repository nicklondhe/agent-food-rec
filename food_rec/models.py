"""Data models for the food recommendation system."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Dish:
    """Represents a dish discovered during search."""

    name: str
    description: str
    category: Optional[str] = None
    neighborhood: Optional[str] = None
    season: Optional[str] = None
    context: str = ""  # Additional context about when/where/how to find it

    # Scoring components
    dest_popularity: float = 0.0  # How popular in destination (0-1)
    global_commonness: float = 0.5  # How common globally (0-1)
    origin_availability: float = 0.0  # How available in origin (0-1)
    authenticity_gap: float = 0.0  # How different from origin version (0-1)

    # Computed scores (set by rank_dishes)
    score: float = 0.0
    uniqueness: float = 0.0

    # Metadata
    tier_discovered: int = 0
    sources: list[str] = field(default_factory=list)

    def __hash__(self):
        """Allow Dish to be used in sets based on name."""
        return hash(self.name.lower())

    def __eq__(self, other):
        """Two dishes are equal if they have the same name (case-insensitive)."""
        if not isinstance(other, Dish):
            return False
        return self.name.lower() == other.name.lower()

    def to_summary_line(self, index: int) -> str:
        """Format as one-line summary with score and uniqueness."""
        return f"{index}. {self.name} - Score: {self.score:.2f} | Uniqueness: {self.uniqueness:.2f}"

    def to_detailed_lines(self, index: int, origin: str, destination: str) -> list[str]:
        """Format as detailed multi-line output for display."""
        lines = [
            f"{index}. {self.name.upper()}",
            f"   Score: {self.score:.2f} | Uniqueness: {self.uniqueness:.2f}",
            f"   Category: {self.category or 'N/A'}",
            f"\n   📝 {self.description}",
            "\n   🎯 Why recommended:",
            f"      • Popularity in {destination}: {self.dest_popularity:.0%}",
            f"      • Global commonness: {self.global_commonness:.0%}",
            f"      • Available in {origin}: {self.origin_availability:.0%}",
        ]

        if self.authenticity_gap > 0:
            lines.append(
                f"      • Authenticity gap: {self.authenticity_gap:.0%} "
                f"(notably different from {origin} version!)"
            )

        if self.context:
            lines.extend([
                "\n   📍 Where/How to find it:",
                f"      {self.context}",
            ])

        lines.append(f"\n   🔍 Discovered in: Tier {self.tier_discovered}")
        lines.append("")

        return lines

    def to_dict(self) -> dict:
        """Convert to full dictionary for JSON output."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "neighborhood": self.neighborhood,
            "season": self.season,
            "context": self.context,
            "score": round(self.score, 3),
            "uniqueness": round(self.uniqueness, 3),
            "metrics": {
                "dest_popularity": self.dest_popularity,
                "global_commonness": self.global_commonness,
                "origin_availability": self.origin_availability,
                "authenticity_gap": self.authenticity_gap,
            },
            "tier_discovered": self.tier_discovered,
            "sources": self.sources,
        }

    def to_compact_dict(self) -> dict:
        """Convert to minimal dictionary for compact JSON output."""
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "category": self.category,
            "description": self.description,
            "context": self.context,
        }


@dataclass
class SearchResult:
    """Results from a tier of searching."""

    dishes: list[Dish]
    queries_used: list[str]
    learnings: dict[str, list[str]]  # Categories, neighborhoods, seasons, etc.
    new_dishes_count: int
    tier: int
