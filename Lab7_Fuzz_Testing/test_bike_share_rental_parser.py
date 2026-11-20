# Lab 7: Fuzzing for Input Validation Bugs
# Name: Pramay Dubey
# SRN: PES2UG24CS361

from hypothesis import given, strategies as st
from bike_share_rental_parser import parse_ride_duration, format_station_code, parse_ride_log

@given(st.text() | st.none())
def test_parse_ride_duration_no_crash(s):
    try:
        result = parse_ride_duration(s)
    except Exception as e:
        assert False, f"parse_ride_duration crashed on {s!r} with: {type(e).__name__}: {e}"
    # Valid input gives a whole number of minutes; anything invalid gives None.
    assert result is None or (isinstance(result, int) and result >= 0)

@given(st.text() | st.none())
def test_format_station_code_no_crash(s):
    try:
        result = format_station_code(s)
    except Exception as e:
        assert False, f"format_station_code crashed on {s!r} with: {type(e).__name__}: {e}"
    # Valid input gives a 'ZONE-NUMBER' string; anything invalid gives None.
    assert result is None or (isinstance(result, str) and '-' in result)

@given(st.text() | st.none())
def test_parse_ride_log_no_crash(s):
    try:
        result = parse_ride_log(s)
    except Exception as e:
        assert False, f"parse_ride_log crashed on {s!r} with: {type(e).__name__}: {e}"
    # Valid input gives a (bike_type, minutes, subscriber) tuple; anything invalid gives None.
    assert result is None or (
        isinstance(result, tuple)
        and len(result) == 3
        and isinstance(result[0], str)
        and isinstance(result[1], int)
        and isinstance(result[2], bool)
    )
