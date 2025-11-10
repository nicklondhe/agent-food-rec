"""
Web search functionality for the food recommendation system.
This module provides a mock search interface for demonstration purposes.
In production, this would integrate with actual search APIs.
"""

from typing import List, Dict
import re


class WebSearcher:
    """Mock web search interface for food-related queries."""
    
    # Mock data for popular dishes by country
    COUNTRY_DISHES = {
        "india": [
            "biryani", "butter chicken", "masala dosa", "samosa", "naan", 
            "tandoori chicken", "palak paneer", "dal makhani", "rogan josh",
            "chole bhature", "pani puri", "vada pav", "idli", "dhokla",
            "hyderabadi biryani", "chicken tikka masala", "aloo gobi",
            "paneer tikka", "korma", "vindaloo"
        ],
        "usa": [
            "hamburger", "hot dog", "pizza", "fried chicken", "mac and cheese",
            "bbq ribs", "buffalo wings", "philly cheesesteak", "burrito",
            "taco", "grilled cheese", "clam chowder", "apple pie", "pancakes",
            "bagel", "donut", "caesar salad", "cobb salad", "blt sandwich"
        ],
        "italy": [
            "pizza margherita", "pasta carbonara", "lasagna", "risotto",
            "osso buco", "tiramisu", "panna cotta", "gnocchi", "ravioli",
            "bruschetta", "caprese salad", "minestrone", "prosciutto",
            "gelato", "focaccia", "arancini", "saltimbocca", "polenta"
        ],
        "japan": [
            "sushi", "ramen", "tempura", "tonkatsu", "yakitori", "udon",
            "soba", "okonomiyaki", "takoyaki", "miso soup", "teriyaki",
            "sukiyaki", "shabu shabu", "gyoza", "onigiri", "katsu curry",
            "tamagoyaki", "donburi", "nabe", "kushikatsu"
        ],
        "mexico": [
            "tacos", "burritos", "quesadillas", "enchiladas", "tamales",
            "pozole", "mole", "chiles rellenos", "ceviche", "guacamole",
            "elote", "tostadas", "fajitas", "nachos", "churros",
            "carnitas", "barbacoa", "chilaquiles", "sopas", "tlayudas"
        ],
        "china": [
            "kung pao chicken", "sweet and sour pork", "dim sum", "dumplings",
            "peking duck", "hot pot", "chow mein", "fried rice", "mapo tofu",
            "spring rolls", "wonton soup", "char siu", "xiaolongbao",
            "congee", "scallion pancakes", "dan dan noodles", "twice cooked pork"
        ],
        "france": [
            "croissant", "baguette", "coq au vin", "bouillabaisse", "ratatouille",
            "crêpes", "quiche lorraine", "beef bourguignon", "escargots",
            "crème brûlée", "macarons", "soufflé", "cassoulet", "tarte tatin",
            "foie gras", "niçoise salad", "profiteroles", "croque monsieur"
        ],
        "thailand": [
            "pad thai", "green curry", "tom yum", "som tam", "massaman curry",
            "pad krapow", "khao soi", "larb", "satay", "spring rolls",
            "tom kha gai", "panang curry", "mango sticky rice", "thai basil chicken"
        ],
    }
    
    # Mock data for dishes available in restaurants in different countries
    DISHES_IN_COUNTRY_RESTAURANTS = {
        ("india", "usa"): [
            "butter chicken", "chicken tikka masala", "naan", "samosa",
            "tandoori chicken", "biryani", "palak paneer", "korma",
            "vindaloo", "dal makhani"
        ],
        ("usa", "india"): [
            "pizza", "hamburger", "fried chicken", "hot dog", "pasta",
            "french fries", "sandwich", "burrito", "taco"
        ],
        ("japan", "usa"): [
            "sushi", "ramen", "tempura", "teriyaki", "gyoza", "udon",
            "miso soup", "yakitori", "tonkatsu"
        ],
        ("italy", "usa"): [
            "pizza margherita", "pasta carbonara", "lasagna", "ravioli",
            "tiramisu", "bruschetta", "caprese salad", "gelato", "risotto"
        ],
        ("mexico", "usa"): [
            "tacos", "burritos", "quesadillas", "enchiladas", "nachos",
            "guacamole", "fajitas", "churros", "salsa"
        ],
        ("china", "usa"): [
            "kung pao chicken", "sweet and sour pork", "dim sum", "dumplings",
            "chow mein", "fried rice", "spring rolls", "wonton soup"
        ],
        ("thailand", "usa"): [
            "pad thai", "green curry", "tom yum", "satay", "spring rolls"
        ],
        ("france", "usa"): [
            "croissant", "baguette", "crêpes", "quiche lorraine",
            "crème brûlée", "macarons", "croque monsieur"
        ],
    }
    
    def search_popular_dishes(self, country: str) -> List[Dict[str, any]]:
        """
        Search for popular dishes in a given country.
        
        Args:
            country: Name of the country (case-insensitive)
            
        Returns:
            List of dishes with relevance scores
        """
        country_lower = country.lower()
        dishes = self.COUNTRY_DISHES.get(country_lower, [])
        
        # Return dishes with mock relevance scores
        results = []
        for i, dish in enumerate(dishes):
            score = 100 - (i * 3)  # Decreasing relevance score
            results.append({
                "dish": dish,
                "score": max(score, 50),  # Minimum score of 50
                "country": country,
                "description": f"Popular {country} dish"
            })
        
        return results
    
    def search_dishes_in_restaurants(
        self, 
        destination_country: str, 
        origin_country: str
    ) -> List[Dict[str, any]]:
        """
        Search for dishes from destination country available in origin country restaurants.
        
        Args:
            destination_country: Country whose cuisine to search for
            origin_country: Country where restaurants are located
            
        Returns:
            List of dishes with availability scores
        """
        key = (destination_country.lower(), origin_country.lower())
        dishes = self.DISHES_IN_COUNTRY_RESTAURANTS.get(key, [])
        
        # Return dishes with mock availability scores
        results = []
        for i, dish in enumerate(dishes):
            score = 95 - (i * 4)  # Decreasing availability score
            results.append({
                "dish": dish,
                "score": max(score, 40),  # Minimum score of 40
                "origin_country": origin_country,
                "destination_country": destination_country,
                "description": f"{destination_country} dish available in {origin_country}"
            })
        
        return results
    
    def normalize_dish_name(self, dish: str) -> str:
        """
        Normalize a dish name for comparison.
        Removes extra whitespace, converts to lowercase, and handles common variations.
        """
        normalized = dish.lower().strip()
        # Remove articles
        normalized = re.sub(r'\b(a|an|the)\b', '', normalized)
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
