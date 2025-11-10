"""
Agent 3: Filters and reranks dishes to find unique destination dishes.
This agent removes dishes available in origin country and reweighs results.
"""

from typing import List, Dict, Set
from .search import WebSearcher


class FilterAgent:
    """Agent that filters and reranks dishes based on uniqueness."""
    
    def __init__(self, searcher: WebSearcher = None):
        """
        Initialize the agent.
        
        Args:
            searcher: WebSearcher instance (creates new one if not provided)
        """
        self.searcher = searcher or WebSearcher()
    
    def filter_and_rerank(
        self,
        destination_dishes: List[Dict[str, any]],
        available_in_origin: Set[str],
        boost_unique: float = 1.5
    ) -> List[Dict[str, any]]:
        """
        Filter out dishes available in origin and rerank remaining dishes.
        
        Args:
            destination_dishes: Popular dishes from destination country
            available_in_origin: Set of normalized dish names available in origin
            boost_unique: Multiplier to boost scores of unique dishes
            
        Returns:
            Filtered and reranked list of dishes
        """
        print(f"\n[Agent 3] Filtering and reranking dishes...")
        print(f"[Agent 3] Dishes to filter out: {len(available_in_origin)}")
        
        filtered_dishes = []
        removed_dishes = []
        
        for dish in destination_dishes:
            normalized_name = self.searcher.normalize_dish_name(dish["dish"])
            
            if normalized_name not in available_in_origin:
                # This dish is unique to the destination
                new_dish = dish.copy()
                # Boost the score for unique dishes
                new_dish["original_score"] = dish["score"]
                new_dish["score"] = dish["score"] * boost_unique
                new_dish["is_unique"] = True
                new_dish["reason"] = "Not commonly found in origin country"
                filtered_dishes.append(new_dish)
            else:
                removed_dishes.append(dish["dish"])
        
        # Sort by reweighed score (descending)
        filtered_dishes.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"[Agent 3] Removed {len(removed_dishes)} dishes: {', '.join(removed_dishes[:5])}")
        if len(removed_dishes) > 5:
            print(f"[Agent 3]   ... and {len(removed_dishes) - 5} more")
        print(f"[Agent 3] Kept {len(filtered_dishes)} unique dishes")
        
        return filtered_dishes
    
    def add_recommendations(
        self,
        dishes: List[Dict[str, any]],
        max_recommendations: int = 10
    ) -> List[Dict[str, any]]:
        """
        Add recommendation context to top dishes.
        
        Args:
            dishes: Filtered dishes list
            max_recommendations: Maximum number of dishes to recommend
            
        Returns:
            List of top recommended dishes with additional context
        """
        top_dishes = dishes[:max_recommendations]
        
        for i, dish in enumerate(top_dishes, 1):
            dish["rank"] = i
            dish["recommendation_strength"] = self._calculate_strength(
                dish["score"], 
                len(dishes)
            )
        
        return top_dishes
    
    def _calculate_strength(self, score: float, total_dishes: int) -> str:
        """
        Calculate recommendation strength based on score.
        
        Args:
            score: Dish score
            total_dishes: Total number of dishes in filtered list
            
        Returns:
            Recommendation strength label
        """
        if score >= 140:
            return "Highly Recommended"
        elif score >= 120:
            return "Recommended"
        elif score >= 100:
            return "Worth Trying"
        else:
            return "Consider"
