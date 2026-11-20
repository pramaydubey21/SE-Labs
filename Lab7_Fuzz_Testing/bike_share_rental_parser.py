# Lab 7: Fuzzing for Input Validation Bugs
# Name: Pramay Dubey
# SRN: PES2UG24CS361

import re

# Only plain ASCII digits are accepted. int() on its own also accepts things like
# '+5', ' 5', '1_0' and non-ASCII digits such as '٥', which are not valid input here.
# The length cap stops int() from failing on very long digit strings: Python refuses
# to convert more than 4300 digits.
_DIGITS = re.compile(r'[0-9]{1,6}')
_STATION_CODE = re.compile(r'[A-Za-z][0-9]{1,6}')


def _to_int(text):
    """Returns text as an int if it is 1-6 ASCII digits, otherwise None."""
    if _DIGITS.fullmatch(text):
        return int(text)
    return None


def parse_ride_duration(text):
    """
    Converts a ride duration written as HH:MM into minutes.
    Returns None if text is not a string of the form HH:MM, where HH and MM are
    ASCII digits and MM is between 00 and 59.
    """
    if not isinstance(text, str):
        return None
    parts = text.strip().split(':')
    if len(parts) != 2:
        return None
    hours, minutes = _to_int(parts[0]), _to_int(parts[1])
    if hours is None or minutes is None or minutes > 59:
        return None
    return hours * 60 + minutes


def format_station_code(code):
    """
    Formats a station code as ZONE-NUMBER, e.g. 'a12' -> 'A-12'.
    Returns None unless code is one ASCII letter followed by ASCII digits
    (leading and trailing spaces are ignored).
    """
    if not isinstance(code, str):
        return None
    code = code.strip()
    # Check before calling upper(): upper() can change the length of some
    # characters ('ß' -> 'SS') or map non-ASCII letters to ASCII ones ('ı' -> 'I').
    if not _STATION_CODE.fullmatch(code):
        return None
    code = code.upper()
    return code[0] + '-' + code[1:]


def parse_ride_log(line):
    """
    Parses 'bike_type,minutes,subscriber' into a tuple (bike_type, minutes, subscriber).
    Returns None unless the line has exactly three fields, bike_type is not empty,
    minutes is ASCII digits and subscriber is 'yes' or 'no' (any case).
    """
    if not isinstance(line, str):
        return None
    parts = line.split(',')
    if len(parts) != 3:
        return None
    bike_type = parts[0].strip()
    minutes = _to_int(parts[1].strip())
    subscriber = parts[2].strip().lower()
    if not bike_type or minutes is None or subscriber not in ('yes', 'no'):
        return None
    return bike_type, minutes, subscriber == 'yes'


def _ask(prompt):
    """Reads a line from the user, returning None if input ends (Ctrl+D / Ctrl+C)."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def main():
    print("==== Running parse_ride_duration ====")
    value = _ask("Enter a ride duration as HH:MM (e.g. 01:15): ")
    result = parse_ride_duration(value)
    if result is None:
        print("Invalid ride duration:", repr(value), "- expected HH:MM, e.g. 01:15")
    else:
        print("Duration in minutes:", result)

    print("\n==== Running format_station_code ====")
    value = _ask("Enter a station code (e.g. a12): ")
    result = format_station_code(value)
    if result is None:
        print("Invalid station code:", repr(value), "- expected a letter followed by digits, e.g. a12")
    else:
        print("Formatted station code:", result)

    print("\n==== Running parse_ride_log ====")
    value = _ask("Enter a ride log line as type,minutes,subscriber (e.g. electric,45,yes): ")
    result = parse_ride_log(value)
    if result is None:
        print("Invalid ride log line:", repr(value), "- expected type,minutes,yes/no, e.g. electric,45,yes")
    else:
        print("Parsed ride log:", result)

if __name__ == "__main__":
    main()
