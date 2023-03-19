# Basic utilities for plotting and manipulating data

from typing import TypeVar, Dict

T = TypeVar('T')
def normalizeTo(values: Dict[T, float], total: float) -> Dict[T, float]:
    """
    Normalizes the given values to the given total. Takes in a dictionary of anything corresponding to a float,
    and returns a new dictionary with the same keys and the values normalized to the given total.
    
    Parameters:
    values: The values to normalize
    total: The total to normalize to
    
    Returns:
    The normalized values dictionary
    """
    current_total = sum(values.values())
    return {key : value * total / current_total for key, value in values.items()}
