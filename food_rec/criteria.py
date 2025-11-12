"""Stopping criteria for iterative search."""

from typing import Collection

from food_rec.models import Dish
from food_rec.scorer import calculate_diversity_score


def should_stop_searching(
    dishes: Collection[Dish],
    target_count: int,
    recent_tier_results: list[int],
    current_tier: int,
    max_tiers: int = 5,
) -> tuple[bool, str]:
    """
    Determine if we should stop searching.

    Args:
        dishes: All dishes discovered so far
        target_count: Target number of dishes
        recent_tier_results: New dishes found in recent tiers (for diminishing returns)
        current_tier: Current tier number
        max_tiers: Maximum number of tiers (cannot exceed 5)

    Returns:
        (should_stop, reason) tuple

    Raises:
        ValueError: If max_tiers exceeds 5
    """
    # Validate max_tiers
    if max_tiers > 5:
        raise ValueError(f"max_tiers cannot exceed 5 (got {max_tiers})")

    stop_reason = ""

    # Check 1: Have we exhausted all tiers?
    if current_tier >= max_tiers:
        stop_reason = f"Exhausted all {max_tiers} tiers"

    # Early exit optimization: don't stop before we have at least the target count
    if not stop_reason and len(dishes) < target_count:
        return False, ""

    # Check 2: If we have 1.5x target, we have plenty
    if not stop_reason and len(dishes) >= target_count * 1.5:
        stop_reason = f"Found {len(dishes)} dishes (1.5x target of {target_count})"

    # Check 3: Good stopping point - enough unique dishes with decent diversity
    if not stop_reason:
        high_uniqueness_dishes = [d for d in dishes if d.uniqueness > 0.6]
        diversity = calculate_diversity_score(dishes)

        if len(high_uniqueness_dishes) >= target_count and diversity > 0.7:
            stop_reason = (
                f"Found {len(high_uniqueness_dishes)} high-uniqueness dishes "
                f"with diversity {diversity:.2f}"
            )

    # Check 4: Stop if we're past target and last tier had low yield
    if not stop_reason and len(dishes) >= target_count and recent_tier_results:
        if recent_tier_results[-1] < 3:
            stop_reason = (
                f"Reached target with low yield last tier "
                f"({recent_tier_results[-1]} new dishes)"
            )

    # Check 5: Diminishing returns (last 2 tiers yielded < 3 new dishes each)
    if not stop_reason and len(recent_tier_results) >= 2:
        if all(count < 3 for count in recent_tier_results[-2:]):
            stop_reason = (
                f"Diminishing returns: last 2 tiers yielded "
                f"{recent_tier_results[-2:]} new dishes"
            )

    # Single return point
    return (bool(stop_reason), stop_reason)
