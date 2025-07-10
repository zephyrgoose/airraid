import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from bulk_accumulator_functions import (
    chance_of_cracking_10_minutes,
    chance_of_cracking_10_hours,
    chance_of_cracking_10_days,
)

def test_probability_increases_with_time():
    network = {"BSSID": "98:48:27:AA:BB:CC"}
    p1 = chance_of_cracking_10_minutes(network)
    p2 = chance_of_cracking_10_hours(network)
    p3 = chance_of_cracking_10_days(network)
    assert 0 <= p1 <= p2 <= p3 <= 1


def test_unknown_vendor_probability_zero():
    network = {"BSSID": "AA:BB:CC:11:22:33"}
    assert chance_of_cracking_10_minutes(network) == 0.0

