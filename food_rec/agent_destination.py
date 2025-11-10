"""
Agent 2: Finds most popular dishes in the destination country.
This agent searches for authentic popular dishes in the destination.
"""

from typing import List, Dict
from .search import WebSearcher


class DestinationCountryAgent:
    """Agent that finds popular dishes in destination country."""
    
    def __init__(self, searcher: WebSearcher = None):
        """
        Initialize the agent.
        
        Args:
            searcher: WebSearcher instance (creates new one if not provided)
        """
        self.searcher = searcher or WebSearcher()
    
    def find_popular_dishes(self, country: str) -> List[Dict[str, any]]:
        """
        Find popular dishes in the given country.
        
        Args:
            country: Country to search dishes for
            
        Returns:
            List of popular dishes with relevance scores
        """
        print(f"\n[Agent 2] Searching for popular dishes in {country}...")
        
        results = self.searcher.search_popular_dishes(country=country)
        
        print(f"[Agent 2] Found {len(results)} popular dishes in {country}")
        
        return results
    
    def get_dish_names(self, dishes: List[Dict[str, any]]) -> set:
        """
        Extract normalized dish names from results.
        
        Args:
            dishes: List of dish dictionaries
            
        Returns:
            Set of normalized dish names
        """
        return {
            self.searcher.normalize_dish_name(dish["dish"]) 
            for dish in dishes
        }
