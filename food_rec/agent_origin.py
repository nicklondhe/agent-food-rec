"""
Agent 1: Finds dishes from destination country available in origin country restaurants.
This agent searches for dishes that a traveler can already find in their home country.
"""

from typing import List, Dict
from .search import WebSearcher


class OriginCountryAgent:
    """Agent that finds destination country dishes available in origin country."""
    
    def __init__(self, searcher: WebSearcher = None):
        """
        Initialize the agent.
        
        Args:
            searcher: WebSearcher instance (creates new one if not provided)
        """
        self.searcher = searcher or WebSearcher()
    
    def find_available_dishes(
        self, 
        destination_country: str, 
        origin_country: str
    ) -> List[Dict[str, any]]:
        """
        Find dishes from destination country that are available in origin country.
        
        Args:
            destination_country: Country the user is traveling to
            origin_country: Country where the user is from
            
        Returns:
            List of dishes with availability information
        """
        print(f"\n[Agent 1] Searching for {destination_country} dishes in {origin_country} restaurants...")
        
        results = self.searcher.search_dishes_in_restaurants(
            destination_country=destination_country,
            origin_country=origin_country
        )
        
        print(f"[Agent 1] Found {len(results)} {destination_country} dishes available in {origin_country}")
        
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
