# agent-food-rec

A food recommendation system that uses web searches and set differences to help travelers discover authentic local dishes that are not commonly available in their home country.

## Overview

When traveling to a new country, you want to try dishes that are truly unique to that destination - not the same dishes you can easily find back home. This system uses three specialized agents to:

1. **Agent 1 (Origin Country Agent)**: Finds dishes from the destination country that are already available in your home country's restaurants
2. **Agent 2 (Destination Country Agent)**: Searches for the most popular dishes in the destination country
3. **Agent 3 (Filter Agent)**: Removes dishes found by Agent 1 from Agent 2's list, then reranks and reweighs the results to highlight truly unique dishes

The result is a curated list of dishes that are popular in the destination but hard to find back home.

## Installation

```bash
# Clone the repository
git clone https://github.com/nicklondhe/agent-food-rec.git
cd agent-food-rec

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Basic usage
food-rec --from USA --to India

# Specify maximum number of recommendations
food-rec --from USA --to Japan --max 15

# Adjust the boost factor for unique dishes
food-rec --from USA --to Mexico --boost 2.0

# Quiet mode (only show final recommendations)
food-rec --from USA --to Thailand --quiet
```

### Python API

```python
from food_rec.orchestrator import FoodRecommendationSystem

# Create the system
system = FoodRecommendationSystem()

# Get recommendations
result = system.get_recommendations(
    origin_country="USA",
    destination_country="India",
    max_recommendations=10,
    boost_unique=1.5
)

# Print formatted recommendations
system.print_recommendations(result)

# Access raw data
print(f"Total unique dishes: {result['unique_dishes_found']}")
for dish in result['recommendations']:
    print(f"{dish['rank']}. {dish['dish']} - {dish['recommendation_strength']}")
```

## Examples

### Example 1: USA to India

```bash
$ food-rec --from USA --to India --max 5
```

This will find Indian dishes that are popular in India but not commonly found in US restaurants, such as regional specialties and street food.

### Example 2: USA to Japan

```bash
$ food-rec --from USA --to Japan --max 10
```

Discover authentic Japanese dishes beyond the sushi and ramen commonly available in the US.

### Example 3: Any Country Pair

The system works for any pair of countries in its database:

```bash
$ food-rec --from USA --to Thailand
$ food-rec --from USA --to Mexico
$ food-rec --from USA --to France
$ food-rec --from USA --to China
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Food Recommendation System                     │
└─────────────────────────────────────────────────────────┘
                         │
                         ├──> Agent 1: Origin Country Agent
                         │    └─> Finds destination dishes
                         │        available in origin
                         │
                         ├──> Agent 2: Destination Country Agent
                         │    └─> Finds popular dishes in
                         │        destination
                         │
                         └──> Agent 3: Filter Agent
                              └─> Removes common dishes,
                                  reranks unique ones
```

### Algorithm

1. **Discovery Phase**: Agent 1 searches for dishes from the destination country that are available in the origin country's restaurants
2. **Analysis Phase**: Agent 2 searches for the most popular dishes in the destination country
3. **Filtering Phase**: Agent 3 creates a set difference, removing any dishes from step 2 that appear in step 1
4. **Reranking Phase**: Agent 3 boosts the scores of unique dishes and sorts by the new scores
5. **Recommendation Phase**: The top N dishes are presented with recommendation strength indicators

### Scoring

- Popular dishes start with relevance scores (100-50 range)
- Dishes available in origin are filtered out completely
- Remaining unique dishes get their scores multiplied by the boost factor (default 1.5x)
- Final recommendations are ranked by adjusted scores

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=food_rec

# Run specific test
python -m pytest tests/test_food_rec.py::TestFoodRecommendationSystem
```

## Supported Countries

Currently supported countries (more can be added):
- USA
- India
- Japan
- Mexico
- China
- Italy
- France
- Thailand

## Future Enhancements

- Integration with real web search APIs (Google, Bing)
- Integration with food databases (Yelp, TripAdvisor)
- User preferences and dietary restrictions
- Regional variations within countries
- Historical popularity trends
- User reviews and ratings integration
- Mobile app interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
