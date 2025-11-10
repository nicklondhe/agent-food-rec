"""
Main orchestrator for the food recommendation system.
Coordinates the three agents to provide unique food recommendations.
"""

from typing import List, Dict, Optional
from .search import WebSearcher
from .agent_origin import OriginCountryAgent
from .agent_destination import DestinationCountryAgent
from .agent_filter import FilterAgent


class FoodRecommendationSystem:
    """Main system that orchestrates all agents for food recommendations."""
    
    def __init__(self, searcher: WebSearcher = None):
        """
        Initialize the food recommendation system.
        
        Args:
            searcher: WebSearcher instance (creates new one if not provided)
        """
        self.searcher = searcher or WebSearcher()
        self.agent_origin = OriginCountryAgent(self.searcher)
        self.agent_destination = DestinationCountryAgent(self.searcher)
        self.agent_filter = FilterAgent(self.searcher)
    
    def get_recommendations(
        self,
        origin_country: str,
        destination_country: str,
        max_recommendations: int = 10,
        boost_unique: float = 1.5
    ) -> Dict[str, any]:
        """
        Get food recommendations for a traveler.
        
        Args:
            origin_country: Country where the user is from
            destination_country: Country the user is traveling to
            max_recommendations: Maximum number of dishes to recommend
            boost_unique: Score multiplier for unique dishes
            
        Returns:
            Dictionary with recommendations and metadata
        """
        print(f"\n{'='*70}")
        print(f"Food Recommendation System")
        print(f"From: {origin_country} → To: {destination_country}")
        print(f"{'='*70}")
        
        # Step 1: Find dishes from destination available in origin
        available_dishes = self.agent_origin.find_available_dishes(
            destination_country=destination_country,
            origin_country=origin_country
        )
        available_names = self.agent_origin.get_dish_names(available_dishes)
        
        # Step 2: Find popular dishes in destination
        popular_dishes = self.agent_destination.find_popular_dishes(
            country=destination_country
        )
        
        # Step 3: Filter and rerank to find unique dishes
        unique_dishes = self.agent_filter.filter_and_rerank(
            destination_dishes=popular_dishes,
            available_in_origin=available_names,
            boost_unique=boost_unique
        )
        
        # Step 4: Get top recommendations with context
        recommendations = self.agent_filter.add_recommendations(
            dishes=unique_dishes,
            max_recommendations=max_recommendations
        )
        
        # Compile results
        result = {
            "origin_country": origin_country,
            "destination_country": destination_country,
            "total_popular_dishes": len(popular_dishes),
            "dishes_available_in_origin": len(available_dishes),
            "unique_dishes_found": len(unique_dishes),
            "recommendations": recommendations,
            "metadata": {
                "boost_factor": boost_unique,
                "max_recommendations": max_recommendations,
                "available_dishes": [d["dish"] for d in available_dishes],
            }
        }
        
        return result
    
    def print_recommendations(self, result: Dict[str, any]) -> None:
        """
        Pretty print the recommendations.
        
        Args:
            result: Result dictionary from get_recommendations
        """
        print(f"\n{'='*70}")
        print(f"RECOMMENDATIONS")
        print(f"{'='*70}")
        print(f"Origin: {result['origin_country']}")
        print(f"Destination: {result['destination_country']}")
        print(f"\nTotal popular dishes in {result['destination_country']}: {result['total_popular_dishes']}")
        print(f"Already available in {result['origin_country']}: {result['dishes_available_in_origin']}")
        print(f"Unique dishes to try: {result['unique_dishes_found']}")
        
        if not result["recommendations"]:
            print(f"\nNo unique dishes found!")
            return
        
        print(f"\n{'='*70}")
        print(f"TOP {len(result['recommendations'])} RECOMMENDATIONS")
        print(f"{'='*70}\n")
        
        for dish in result["recommendations"]:
            print(f"{dish['rank']}. {dish['dish'].upper()}")
            print(f"   Strength: {dish['recommendation_strength']}")
            print(f"   Score: {dish['score']:.1f} (Original: {dish['original_score']:.1f})")
            print(f"   Reason: {dish['reason']}")
            print()
        
        print(f"{'='*70}")
        print(f"These dishes are popular in {result['destination_country']} but")
        print(f"not commonly found in {result['origin_country']} restaurants.")
        print(f"{'='*70}\n")
