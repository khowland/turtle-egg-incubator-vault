def can_retire_bin(active_eggs_count: int) -> bool:
    """Standard §4.D: Blocks bin retirement if active biological subjects remain."""
    return active_eggs_count == 0
