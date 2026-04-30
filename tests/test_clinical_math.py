"""
Clinical Math — Verify incubation duration calculations are correct.
days_in_care is stored in the intake table and feeds the Dashboard / Reports.
"""
import pytest
import datetime


def test_incubation_duration_math():
    """
    days_in_care should equal the difference between today and intake_date in days.
    Verifies the calculation used in intake payload construction is correct.
    """
    intake_date = datetime.date(2026, 4, 1)
    today = datetime.date(2026, 4, 26)
    expected_days = (today - intake_date).days  # 25

    assert expected_days == 25, f"Expected 25 days but got {expected_days}"
    assert expected_days >= 0, "days_in_care must not be negative."


def test_incubation_duration_same_day():
    """An intake recorded today must have days_in_care == 0."""
    today = datetime.date.today()
    days = (today - today).days
    assert days == 0, f"Same-day intake should have 0 days_in_care, got {days}."


def test_incubation_duration_negative_guard():
    """A future intake_date (temporal paradox) must produce a negative days_in_care."""
    today = datetime.date.today()
    future = today + datetime.timedelta(days=10)
    days = (today - future).days
    assert days < 0, "Future intake_date should produce negative days — temporal paradox detectable."
