"""Unit tests for rules-based mood classification."""

from music_observatory.classify import classify_track


def test_heartbreak_in_title_is_going_thru_it():
    assert classify_track("Heartbreak Hotel", 200_000) == "going_thru_it"


def test_party_in_title_is_hype():
    assert classify_track("Party Anthem", 200_000) == "hype"


def test_short_track_without_keywords_is_locked_in():
    assert classify_track("Partition", 160_000) == "locked_in"


def test_long_track_without_keywords_is_chill():
    assert classify_track("Partition", 300_000) == "chill"


def test_mid_length_without_keywords_is_unclassified():
    assert classify_track("drivers license", 242_000) == "unclassified"


def test_keyword_beats_duration():
    assert classify_track("Heartbreak", 120_000) == "going_thru_it"