"""Scoring logic for dishes using TF-IDF-inspired formula."""

import math
from collections import defaultdict
from typing import Collection

from food_rec.models import Dish


def calculate_diversity_score(dishes: Collection[Dish]) -> float:
    """
    Calculate diversity score based on category distribution using Shannon entropy.
    Returns value 0-1, where 1 is maximum diversity.
    """
    if not dishes:
        return 0.0

    categories = [d.category for d in dishes if d.category]
    if not categories:
        return 0.5  # No category info, assume moderate diversity

    # Count categories using defaultdict
    category_counts = defaultdict(int)
    for cat in categories:
        category_counts[cat] += 1

    total = len(categories)
    unique_categories = len(category_counts)

    # Calculate Shannon entropy
    entropy = 0.0
    for count in category_counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    # Normalize entropy to 0-1 range
    # Maximum entropy occurs when all categories are equally distributed
    max_entropy = math.log2(unique_categories) if unique_categories > 1 else 1.0

    # Normalized entropy (0-1)
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

    # Combine entropy with category count ratio for better diversity measure
    # More unique categories = higher diversity
    category_ratio = min(1.0, unique_categories / max(1, total * 0.7))

    # Weight entropy more heavily (70%), category ratio less (30%)
    diversity = 0.7 * normalized_entropy + 0.3 * category_ratio

    return diversity


def calculate_uniqueness(dish: Dish) -> float:
    """
    Calculate how unique a dish is (for stopping criteria).
    Based on low global commonness and origin availability.

    Note: Authenticity gap is handled in score_dish(), not here.
    Uniqueness is about rarity, not quality differences.
    """
    uniqueness = (1 - dish.global_commonness) * (1 - dish.origin_availability)
    return uniqueness


def score_dish(dish: Dish) -> float:
    """
    Score a dish using TF-IDF-inspired formula:
    score = popularity_in_dest * log(1 / commonness_globally) * (1 - origin_availability)

    Components:
    - dest_popularity: How popular/mentioned in destination (like TF)
    - global_commonness: How common globally (inverse is like IDF)
    - origin_availability: Penalty if available in origin
    - authenticity_gap: Bonus if dish exists in origin but is notably different in dest
    """
    # Ensure all values are in valid ranges
    dest_popularity = max(0.0, min(1.0, dish.dest_popularity))
    global_commonness = max(0.01, min(1.0, dish.global_commonness))  # Avoid log(0)
    origin_availability = max(0.0, min(1.0, dish.origin_availability))
    authenticity_gap = max(0.0, min(1.0, dish.authenticity_gap))

    # Base TF-IDF-inspired score
    idf_component = math.log(1.0 / global_commonness)
    base_score = dest_popularity * idf_component * (1 - origin_availability)

    # If dish exists in origin but there's an authenticity gap, add bonus
    if origin_availability > 0 and authenticity_gap > 0:
        authenticity_bonus = authenticity_gap * 0.5 * dest_popularity
        base_score += authenticity_bonus

    return base_score


def rank_dishes(dishes: list[Dish]) -> list[Dish]:
    """
    Score and rank all dishes, returning sorted list (highest score first).
    Updates the score and uniqueness fields on each dish.
    """
    for dish in dishes:
        dish.score = score_dish(dish)
        dish.uniqueness = calculate_uniqueness(dish)

    return sorted(dishes, key=lambda d: d.score, reverse=True)
