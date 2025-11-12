"""Output formatters for food recommendations."""

import json

from food_rec.models import Dish


def format_quick_summary(dishes: list[Dish]) -> str:
    """Format as quick summary: dish name + score."""
    return "\n".join(dish.to_summary_line(i) for i, dish in enumerate(dishes, 1))


def format_detailed_text(
    dishes: list[Dish], origin: str, destination: str
) -> str:
    """Format as detailed text output (for display)."""
    lines = [
        f"\n{'='*70}",
        f"🍽️  FOOD RECOMMENDATIONS: {origin} → {destination}",
        f"{'='*70}\n",
    ]

    for i, dish in enumerate(dishes, 1):
        lines.extend(dish.to_detailed_lines(i, origin, destination))

    return "\n".join(lines)


def format_json(dishes: list[Dish], origin: str, destination: str) -> str:
    """Format as JSON (for API/server use)."""
    data = {
        "origin": origin,
        "destination": destination,
        "count": len(dishes),
        "dishes": [dish.to_dict() for dish in dishes],
    }
    return json.dumps(data, indent=2)


def format_compact_json(dishes: list[Dish]) -> str:
    """Format as compact JSON (minimal, for quick lookup)."""
    return json.dumps([dish.to_compact_dict() for dish in dishes], indent=2)
