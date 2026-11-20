"""
Lab 6 - Code (line) coverage tests for bike_share_rental.py
SRN: PES2UG24CS361

Goal: execute every statement in the module at least once (>= 90% line coverage).
Each test below is aimed at one or more lines that the starter tests never reached.
"""
import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# ---------------------------------------------------------------- ride_cost

def test_standard_ride():
    # 45 min -> 2 blocks of 30 min at 20 each
    assert ride_cost("standard", 45, False, False) == 40


def test_unknown_bike_type_raises():
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost("scooter", 30, False, False)


def test_invalid_duration_raises():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", 0, False, False)


def test_subscriber_first_block_free():
    # 30 min -> 1 block, subscriber gets 1 free block -> 0
    assert ride_cost("electric", 30, True, False) == 0


def test_peak_surcharge_and_long_ride_fee():
    # 200 min -> 7 blocks * 20 = 140, +15 peak, +100 over 180 min
    assert ride_cost("standard", 200, False, True) == 255


# -------------------------------------------------------------- dock_status

def test_dock_available():
    assert dock_status(5, 10) == "available"


def test_invalid_capacity_raises():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, 0)


def test_invalid_bike_count_raises():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(11, 10)


def test_dock_empty():
    assert dock_status(0, 10) == "empty"


def test_dock_full():
    assert dock_status(10, 10) == "full"


def test_dock_few_bikes():
    assert dock_status(2, 10) == "few bikes"


def test_dock_few_slots():
    assert dock_status(8, 10) == "few slots"


# --------------------------------------------------------------- can_unlock

def test_cannot_unlock_with_active_ride():
    assert can_unlock(500, True, 25) is False


def test_cannot_unlock_under_16():
    assert can_unlock(500, False, 15) is False


def test_teen_with_enough_balance():
    assert can_unlock(100, False, 17) is True


def test_adult_with_enough_balance():
    assert can_unlock(50, False, 30) is True
