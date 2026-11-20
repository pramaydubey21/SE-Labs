"""
Lab 6 - Branch coverage tests for bike_share_rental.py
SRN: PES2UG24CS361

Goal: make every decision (if / elif / compound condition) evaluate to BOTH
True and False at least once (>= 90% branch coverage). Tests are grouped by the
decision they exercise, with boundary values on either side of each condition.
"""
import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# =========================================================== ride_cost
# Decisions:
#   D1  bike_type not in RATE_PER_30_MIN
#   D2  minutes <= 0
#   D3  is_subscriber
#   D4    blocks <= 0             (nested inside D3)
#   D5  is_peak and bike_type != "cargo"
#   D6  minutes > 180

# D1 True / False
def test_unknown_bike_type_raises():
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost("tandem", 30, False, False)


@pytest.mark.parametrize("bike_type, expected", [
    ("standard", 20),
    ("electric", 35),
    ("cargo", 50),
])
def test_each_known_bike_type_single_block(bike_type, expected):
    assert ride_cost(bike_type, 30, False, False) == expected


# D2 True (zero and negative) / False (smallest valid duration)
@pytest.mark.parametrize("minutes", [0, -10])
def test_non_positive_duration_raises(minutes):
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", minutes, False, False)


def test_one_minute_ride_is_one_block():
    assert ride_cost("standard", 1, False, False) == 20


# Block rounding at the 30-minute boundary
def test_31_minutes_rounds_up_to_two_blocks():
    assert ride_cost("standard", 31, False, False) == 40


# D3 True + D4 True  -> free ride
def test_subscriber_single_block_is_free():
    assert ride_cost("electric", 30, True, False) == 0


# D3 True + D4 False -> subscriber still pays for remaining blocks
def test_subscriber_pays_for_extra_blocks():
    # 90 min -> 3 blocks, 1 free -> 2 * 35 = 70
    assert ride_cost("electric", 90, True, False) == 70


# D3 False
def test_non_subscriber_pays_all_blocks():
    assert ride_cost("electric", 90, False, False) == 105


# D5 True: peak and not cargo
def test_peak_surcharge_for_standard():
    assert ride_cost("standard", 30, False, True) == 35


# D5 False via second operand: peak but cargo is exempt
def test_peak_no_surcharge_for_cargo():
    assert ride_cost("cargo", 30, False, True) == 50


# D5 False via first operand: off-peak
def test_off_peak_no_surcharge():
    assert ride_cost("electric", 30, False, False) == 35


# D6 boundary: exactly 180 is NOT a long ride, 181 is
def test_exactly_180_minutes_no_long_ride_fee():
    assert ride_cost("standard", 180, False, False) == 120


def test_181_minutes_adds_long_ride_fee():
    # 181 min -> 7 blocks * 20 = 140, +100
    assert ride_cost("standard", 181, False, False) == 240


# All surcharges together with a subscriber
def test_subscriber_peak_long_ride_combined():
    # 200 min -> 7 blocks, 1 free -> 6 * 35 = 210, +15 peak, +100 long
    assert ride_cost("electric", 200, True, True) == 325


# Subscriber whose free block wipes the fare returns before surcharges
def test_subscriber_free_ride_ignores_peak():
    assert ride_cost("standard", 20, True, True) == 0


# ========================================================= dock_status
# Decisions:
#   D1  capacity <= 0
#   D2  bikes_docked < 0 or bikes_docked > capacity
#   D3  bikes_docked == 0
#   D4  free_slots == 0
#   D5  bikes_docked <= 2
#   D6  elif free_slots <= 2

@pytest.mark.parametrize("capacity", [0, -5])
def test_invalid_capacity_raises(capacity):
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, capacity)


# D2 True via first operand (negative count)
def test_negative_bike_count_raises():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(-1, 10)


# D2 True via second operand (more bikes than capacity)
def test_bike_count_over_capacity_raises():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(11, 10)


# D3 True
def test_empty_dock():
    assert dock_status(0, 10) == "empty"


# D4 True
def test_full_dock():
    assert dock_status(10, 10) == "full"


# D5 True (boundaries 1 and 2)
@pytest.mark.parametrize("bikes", [1, 2])
def test_few_bikes(bikes):
    assert dock_status(bikes, 10) == "few bikes"


# D5 False, D6 True (boundaries: 2 free and 1 free slot)
@pytest.mark.parametrize("bikes", [8, 9])
def test_few_slots(bikes):
    assert dock_status(bikes, 10) == "few slots"


# D5 False, D6 False
@pytest.mark.parametrize("bikes", [3, 5, 7])
def test_available(bikes):
    assert dock_status(bikes, 10) == "available"


# Small dock where "few bikes" takes priority over "few slots"
def test_few_bikes_checked_before_few_slots():
    assert dock_status(1, 3) == "few bikes"


# ========================================================== can_unlock
# Decisions:
#   D1  has_active_ride
#   D2  age < 16
#   D3  elif age < 18   -> balance >= 100
#   D4  otherwise       -> balance >= 50

def test_active_ride_blocks_unlock():
    assert can_unlock(1000, True, 30) is False


def test_under_16_blocked_even_with_balance():
    assert can_unlock(1000, False, 15) is False


# D3 True, both outcomes of the balance check (boundary at 100)
def test_age_16_with_exactly_100_can_unlock():
    assert can_unlock(100, False, 16) is True


def test_age_17_with_99_cannot_unlock():
    assert can_unlock(99, False, 17) is False


# D3 False (adult), both outcomes of the balance check (boundary at 50)
def test_age_18_with_exactly_50_can_unlock():
    assert can_unlock(50, False, 18) is True


def test_adult_with_49_cannot_unlock():
    assert can_unlock(49, False, 40) is False
