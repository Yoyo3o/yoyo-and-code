"""
Problem 1: Doctest - Ride Fare Calculator
"""

def calculate_trip_fare(distance_km: float, is_rush_hour: bool = False, passenger_type: str = "adult") -> float:
    """
    Calculate the total taxi/ride fare based on distance, rush hour status, and passenger type.

    Pricing Rules:
    1. Base Fare: $3.00 (covers up to the first 2.0 km).
    2. Additional Distance: For distance > 2.0 km, charge $1.50 per additional km.
       (e.g., for 5.0 km, distance fare = 3.00 + (5.0 - 2.0) * 1.50 = $7.50).
    3. Rush Hour Surcharge: If is_rush_hour is True, add a 25% surcharge to the fare
       (i.e., fare * 1.25).
    4. Passenger Discounts:
       - "adult": no discount (full price)
       - "senior": 30% discount (pays 70% of total)
       - "child": 50% discount (pays 50% of total)
    5. Output: Return the final fare rounded to 2 decimal places.
    6. Exceptions:
       - Raise ValueError("distance_km cannot be negative") if distance_km < 0.
       - Raise ValueError("invalid passenger_type: must be 'adult', 'child', or 'senior'")
         if passenger_type is not one of {"adult", "child", "senior"}.

    Examples / Doctests:
    TODO: Add at least 6 comprehensive doctests below covering:
          - Standard normal trip (e.g. 5.0 km adult)
          - Boundary cases (e.g. 0.0 km, exactly 2.0 km)
          - Rush hour surcharge (e.g. 10.0 km during rush hour)
          - Passenger discounts ("child" and "senior")
          - Combination of rush hour and discount
          - Exceptions (negative distance and invalid passenger type)

    >>> calculate_trip_fare(1.5)
    3.0
    >>> # TODO: Add more doctests here
    """
    if distance_km < 0:
        raise ValueError("distance_km cannot be negative")
    
    valid_passenger_types = {"adult", "child", "senior"}
    if passenger_type not in valid_passenger_types:
        raise ValueError("invalid passenger_type: must be 'adult', 'child', or 'senior'")
    
    # Calculate base and distance fare
    if distance_km <= 2.0:
        fare = 3.0
    else:
        fare = 3.0 + (distance_km - 2.0) * 1.50

    # Apply rush hour surcharge
    if is_rush_hour:
        fare *= 1.25

    # Apply passenger discount
    if passenger_type == "child":
        fare *= 0.50
    elif passenger_type == "senior":
        fare *= 0.70

    return round(fare, 2)


if __name__ == "__main__":
    import doctest
    # Run doctests and display verbose results
    doctest.testmod(verbose=True)
