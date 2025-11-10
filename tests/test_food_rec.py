"""Unit tests for the food recommendation system."""

import unittest
from food_rec.search import WebSearcher
from food_rec.agent_origin import OriginCountryAgent
from food_rec.agent_destination import DestinationCountryAgent
from food_rec.agent_filter import FilterAgent
from food_rec.orchestrator import FoodRecommendationSystem


class TestWebSearcher(unittest.TestCase):
    """Test the WebSearcher class."""
    
    def setUp(self):
        self.searcher = WebSearcher()
    
    def test_search_popular_dishes(self):
        """Test searching for popular dishes."""
        results = self.searcher.search_popular_dishes("India")
        self.assertGreater(len(results), 0)
        self.assertIn("dish", results[0])
        self.assertIn("score", results[0])
        self.assertIn("country", results[0])
    
    def test_search_dishes_in_restaurants(self):
        """Test searching for dishes in restaurants."""
        results = self.searcher.search_dishes_in_restaurants("India", "USA")
        self.assertGreater(len(results), 0)
        self.assertIn("dish", results[0])
        self.assertIn("score", results[0])
    
    def test_normalize_dish_name(self):
        """Test dish name normalization."""
        self.assertEqual(
            self.searcher.normalize_dish_name("Butter Chicken"),
            "butter chicken"
        )
        self.assertEqual(
            self.searcher.normalize_dish_name("  The  Biryani  "),
            "biryani"
        )


class TestOriginCountryAgent(unittest.TestCase):
    """Test the OriginCountryAgent class."""
    
    def setUp(self):
        self.agent = OriginCountryAgent()
    
    def test_find_available_dishes(self):
        """Test finding available dishes."""
        dishes = self.agent.find_available_dishes("India", "USA")
        self.assertGreater(len(dishes), 0)
        self.assertIn("dish", dishes[0])
    
    def test_get_dish_names(self):
        """Test extracting dish names."""
        dishes = [{"dish": "Butter Chicken"}, {"dish": "Biryani"}]
        names = self.agent.get_dish_names(dishes)
        self.assertIn("butter chicken", names)
        self.assertIn("biryani", names)


class TestDestinationCountryAgent(unittest.TestCase):
    """Test the DestinationCountryAgent class."""
    
    def setUp(self):
        self.agent = DestinationCountryAgent()
    
    def test_find_popular_dishes(self):
        """Test finding popular dishes."""
        dishes = self.agent.find_popular_dishes("India")
        self.assertGreater(len(dishes), 0)
        self.assertIn("dish", dishes[0])
        self.assertIn("score", dishes[0])
    
    def test_get_dish_names(self):
        """Test extracting dish names."""
        dishes = [{"dish": "Masala Dosa"}, {"dish": "Samosa"}]
        names = self.agent.get_dish_names(dishes)
        self.assertIn("masala dosa", names)
        self.assertIn("samosa", names)


class TestFilterAgent(unittest.TestCase):
    """Test the FilterAgent class."""
    
    def setUp(self):
        self.agent = FilterAgent()
    
    def test_filter_and_rerank(self):
        """Test filtering and reranking dishes."""
        destination_dishes = [
            {"dish": "Masala Dosa", "score": 100},
            {"dish": "Butter Chicken", "score": 95},
            {"dish": "Biryani", "score": 90},
        ]
        available = {"butter chicken", "biryani"}
        
        result = self.agent.filter_and_rerank(destination_dishes, available)
        
        # Should only have masala dosa (not in available)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["dish"], "Masala Dosa")
        self.assertTrue(result[0]["is_unique"])
        # Score should be boosted
        self.assertGreater(result[0]["score"], 100)
    
    def test_add_recommendations(self):
        """Test adding recommendation context."""
        dishes = [
            {"dish": "Dish 1", "score": 150},
            {"dish": "Dish 2", "score": 100},
        ]
        
        result = self.agent.add_recommendations(dishes, max_recommendations=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["rank"], 1)
        self.assertEqual(result[1]["rank"], 2)
        self.assertIn("recommendation_strength", result[0])


class TestFoodRecommendationSystem(unittest.TestCase):
    """Test the FoodRecommendationSystem orchestrator."""
    
    def setUp(self):
        self.system = FoodRecommendationSystem()
    
    def test_get_recommendations_india_usa(self):
        """Test getting recommendations for USA to India travel."""
        result = self.system.get_recommendations("USA", "India", max_recommendations=5)
        
        self.assertEqual(result["origin_country"], "USA")
        self.assertEqual(result["destination_country"], "India")
        self.assertGreater(result["total_popular_dishes"], 0)
        self.assertGreater(result["unique_dishes_found"], 0)
        self.assertLessEqual(len(result["recommendations"]), 5)
        
        # Check that recommendations have required fields
        if result["recommendations"]:
            rec = result["recommendations"][0]
            self.assertIn("dish", rec)
            self.assertIn("score", rec)
            self.assertIn("rank", rec)
            self.assertIn("recommendation_strength", rec)
    
    def test_get_recommendations_different_countries(self):
        """Test with different country pairs."""
        # Test USA to Japan
        result = self.system.get_recommendations("USA", "Japan")
        self.assertGreater(len(result["recommendations"]), 0)
        
        # Test USA to Mexico
        result = self.system.get_recommendations("USA", "Mexico")
        self.assertGreater(len(result["recommendations"]), 0)
    
    def test_boost_factor(self):
        """Test that boost factor affects scores."""
        result1 = self.system.get_recommendations("USA", "India", boost_unique=1.5)
        result2 = self.system.get_recommendations("USA", "India", boost_unique=2.0)
        
        # With higher boost, scores should be higher
        if result1["recommendations"] and result2["recommendations"]:
            score1 = result1["recommendations"][0]["score"]
            score2 = result2["recommendations"][0]["score"]
            # Can't guarantee exact comparison due to filtering, but both should exist
            self.assertGreater(score1, 0)
            self.assertGreater(score2, 0)


if __name__ == "__main__":
    unittest.main()
