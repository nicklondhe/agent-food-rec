# Example Usage

Here's a simple example of using the food recommendation system:

```python
from food_rec.orchestrator import FoodRecommendationSystem

# Create the system
system = FoodRecommendationSystem()

# Get recommendations
result = system.get_recommendations(
    origin_country="USA",
    destination_country="India"
)

# Print results
system.print_recommendations(result)
```

## Command Line Examples

```bash
# Basic usage
food-rec --from USA --to India

# More recommendations
food-rec --from USA --to Japan --max 15

# Higher boost for unique dishes
food-rec --from USA --to Mexico --boost 2.0
```
