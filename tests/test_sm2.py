import pytest
from datetime import datetime
from modules.db import Flashcard, update_sm2

def test_sm2_blackout():
    card = Flashcard(interval=6, repetitions=2, ease_factor=2.5)
    update_sm2(card, 0) # blackout
    assert card.interval == 1
    assert card.repetitions == 0
    assert card.ease_factor < 2.5 # Should decrease

def test_sm2_perfect():
    card = Flashcard(interval=6, repetitions=2, ease_factor=2.5)
    update_sm2(card, 5) # perfect
    assert card.interval > 6
    assert card.repetitions == 3
    assert card.ease_factor >= 2.5
