from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from logic_utils import check_guess, get_range_for_difficulty, parse_guess

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")

SUBMIT = 0
NEW_GAME = 1


# ---------------------------------------------------------------------------
# check_guess: outcomes
# ---------------------------------------------------------------------------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# Bug: hint messages were swapped
# ---------------------------------------------------------------------------

def test_too_high_tells_player_to_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_tells_player_to_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


# ---------------------------------------------------------------------------
# Bug: secret became a string on even attempts, so guesses were compared
# alphabetically ("9" > "50", "100" < "50") instead of numerically
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "guess, secret, expected",
    [
        (9, 50, "Too Low"),     # "9" > "50" alphabetically
        (100, 50, "Too High"),  # "100" < "50" alphabetically
        (100, 9, "Too High"),   # "100" < "9" alphabetically
        (5, 10, "Too Low"),     # "5" > "10" alphabetically
    ],
)
def test_guesses_compared_numerically_not_alphabetically(guess, secret, expected):
    outcome, _ = check_guess(guess, secret)
    assert outcome == expected


def test_same_guess_gives_same_hint_on_every_attempt():
    at = AppTest.from_file(APP_PATH).run()
    at.session_state.secret = 50

    hints = []
    for _ in range(4):  # covers both odd and even attempts
        at.text_input[0].input("9")
        at.button[SUBMIT].click()
        at.run()
        hints.append(at.warning[0].value)

    assert all("HIGHER" in hint for hint in hints)


# ---------------------------------------------------------------------------
# Bug: no range validation (and the first range check crashed on text input)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["0", "101", "150", "-5"])
def test_out_of_range_guess_rejected(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok
    assert value is None
    assert err == "Guess must be between 1 and 100."


@pytest.mark.parametrize("raw, expected", [("1", 1), ("50", 50), ("100", 100)])
def test_in_range_guess_accepted(raw, expected):
    assert parse_guess(raw, 1, 100) == (True, expected, None)


def test_non_number_rejected_without_crashing():
    ok, _, err = parse_guess("abc", 1, 100)
    assert not ok
    assert err == "That is not a number."


# ---------------------------------------------------------------------------
# Bug: difficulty range ignored (secret, validation and UI all used 1-100)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, high",
    [("Easy", 20), ("Normal", 100), ("Hard", 50)],
)
def test_parse_guess_uses_difficulty_range(difficulty, high):
    low, range_high = get_range_for_difficulty(difficulty)
    assert range_high == high

    assert parse_guess(str(high), low, range_high)[0]
    ok, _, err = parse_guess(str(high + 1), low, range_high)
    assert not ok
    assert err == f"Guess must be between 1 and {high}."


@pytest.mark.parametrize("difficulty, high", [("Easy", 20), ("Hard", 50)])
def test_changing_difficulty_picks_secret_in_new_range(difficulty, high):
    at = AppTest.from_file(APP_PATH).run()
    for _ in range(20):  # secret is random, so check several new games
        at.sidebar.selectbox[0].select(difficulty).run()
        at.button[NEW_GAME].click().run()
        assert 1 <= at.session_state.secret <= high


@pytest.mark.parametrize("difficulty, high", [("Easy", 20), ("Hard", 50)])
def test_info_text_shows_difficulty_range(difficulty, high):
    at = AppTest.from_file(APP_PATH).run()
    at.sidebar.selectbox[0].select(difficulty).run()
    assert f"between 1 and {high}" in at.info[0].value


def test_new_game_uses_current_difficulty_range():
    at = AppTest.from_file(APP_PATH).run()
    at.sidebar.selectbox[0].select("Easy").run()
    for _ in range(20):
        at.button[NEW_GAME].click().run()
        assert 1 <= at.session_state.secret <= 20


# ---------------------------------------------------------------------------
# Bug: attempts left was one below the limit
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, limit",
    [("Easy", 6), ("Normal", 8), ("Hard", 5)],
)
def test_fresh_game_shows_full_attempts(difficulty, limit):
    at = AppTest.from_file(APP_PATH).run()
    at.sidebar.selectbox[0].select(difficulty).run()
    assert at.session_state.attempts == 0
    assert f"Attempts left: {limit}" in at.info[0].value


def test_attempts_left_updates_right_after_a_guess():
    at = AppTest.from_file(APP_PATH).run()
    at.session_state.secret = 50
    at.text_input[0].input("10")
    at.button[SUBMIT].click().run()
    assert "Attempts left: 7" in at.info[0].value


# ---------------------------------------------------------------------------
# Bug: invalid / out-of-range guesses used up an attempt
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["500", "0", "abc"])
def test_invalid_guess_does_not_use_an_attempt(raw):
    at = AppTest.from_file(APP_PATH).run()
    at.text_input[0].input(raw)
    at.button[SUBMIT].click().run()
    assert at.session_state.attempts == 0
    assert at.session_state.history == []
    assert "Attempts left: 8" in at.info[0].value


# ---------------------------------------------------------------------------
# Bug: after winning, New Game didn't let you guess again
# ---------------------------------------------------------------------------

def test_new_game_after_win_allows_guessing():
    at = AppTest.from_file(APP_PATH).run()
    at.session_state.secret = 50
    at.text_input[0].input("50")
    at.button[SUBMIT].click().run()
    assert at.session_state.status == "won"

    at.button[NEW_GAME].click().run()
    assert at.session_state.status == "playing"
    assert at.session_state.attempts == 0
    assert at.session_state.history == []

    at.session_state.secret = 50
    at.text_input[0].input("10")
    at.button[SUBMIT].click().run()
    assert at.session_state.attempts == 1
    assert "HIGHER" in at.warning[0].value


def test_new_game_after_loss_allows_guessing():
    at = AppTest.from_file(APP_PATH).run()
    at.sidebar.selectbox[0].select("Hard").run()
    at.session_state.secret = 50
    for _ in range(5):
        at.text_input[0].input("10")
        at.button[SUBMIT].click().run()
    assert at.session_state.status == "lost"

    at.button[NEW_GAME].click().run()
    assert at.session_state.status == "playing"
    assert "Attempts left: 5" in at.info[0].value
