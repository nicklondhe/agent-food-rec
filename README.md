# Food Recommendation System

An intelligent food recommendation system that uses iterative web search and TF-IDF-inspired scoring to find unique dishes when traveling between cities.

## Features

- **Iterative Search**: Progressively searches from broad to hyperlocal across 5 tiers
- **Smart Stopping**: Automatically stops when enough high-uniqueness dishes are found
- **Context Learning**: Each tier learns from previous searches to refine queries
- **TF-IDF Scoring**: Scores dishes based on destination popularity, global rarity, and origin availability
- **Real-time Progress**: Shows search progress as it explores different tiers

## How It Works

### Search Tiers

1. **Tier 1: Broad Search** - Popular local foods, must-try dishes
2. **Tier 2: Category-Structured** - Street food, desserts, breakfast items
3. **Tier 3: Hyperlocal** - Neighborhood specialties, hidden gems
4. **Tier 4: Temporal** - Seasonal dishes, festival foods
5. **Tier 5: Ultra-Specific** - Combined context from all previous learnings

### Scoring Formula

```
score = popularity_in_dest × log(1 / commonness_globally) × (1 - origin_availability)
```

With bonus for authenticity gap (dishes that exist in origin but are notably different in destination).

### Stopping Criteria

The search stops when:
- Found ≥ N dishes with uniqueness > 0.7 AND diversity > 0.8
- Last 2 tiers yielded < 2 new dishes each (diminishing returns)
- All 5 tiers exhausted

## Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install anthropic
```

## Usage

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Run the recommendation system:

```bash
# Basic usage
python main.py --origin "New York" --destination "Tokyo"

# Specify number of recommendations
python main.py -o "Paris" -d "Bangkok" -n 15

# Use custom API key
python main.py -o "London" -d "Mexico City" --api-key "sk-..."
```

### Arguments

- `-o, --origin`: Origin city/country (required)
- `-d, --destination`: Destination city/country (required)
- `-n, --target`: Number of dish recommendations (default: 10)
- `--api-key`: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)

## Example Output

```
🔍 Searching for 10 unique dishes
   Origin: New York
   Destination: Tokyo

============================================================
🎯 TIER 1: Broad Search
============================================================

🔎 Generated 3 queries for this tier:
   1. popular local food in Tokyo
   2. must-try dishes in Tokyo
   3. traditional cuisine Tokyo

   🌐 Searching: popular local food in Tokyo
      Found 5 dishes

...

============================================================
🏆 FINAL RANKING
============================================================

1. MONJAYAKI
   Score: 3.45 | Uniqueness: 0.89
   Category: Street Food

   📝 A runny savory pancake that's a Tokyo specialty...

   🎯 Why recommended:
      • Popularity in Tokyo: 85%
      • Global commonness: 15%
      • Available in New York: 5%

   📍 Where/How to find it:
      Best found in Tsukishima neighborhood, known as Monja Street

   🔍 Discovered in: Tier 3
```

## Architecture

```
food_rec/
├── __init__.py
├── models.py          # Dish and SearchResult data models
├── scorer.py          # TF-IDF-inspired scoring logic
├── criteria.py        # Stopping criteria checker
└── orchestrator.py    # Main iterative search orchestrator

main.py                # CLI interface
```

## Key Components

- **Dish Model**: Stores dish data with scoring components
- **Orchestrator**: Manages tier progression and search execution
- **Scorer**: Calculates uniqueness and diversity scores
- **Criteria Checker**: Determines when to stop searching

## Requirements

- Python 3.12+
- Anthropic API key with Claude Sonnet 4.5 access
- Web search tool access

## License

MIT
