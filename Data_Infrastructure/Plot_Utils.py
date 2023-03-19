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

def distributionToStr(distribution: Dict[int, float]) -> str:
    """
    Converts a distribution dictionary to a string. The distribution dictionary is a dictionary of price levels
    corresponding to the desired distribution of values at that level.
    
    Parameters:
    distribution: The distribution dictionary to convert to a string
    
    Returns:
    A string representation of the distribution dictionary
    """
    
    s: str = "distribution: Dict[int, float] = {\n"
    for price_level in sorted(distribution.keys()):
        s += "\t" + str(price_level) + ": " + str(distribution[price_level]) + ",\n"
    s += "}\n"
    return s
