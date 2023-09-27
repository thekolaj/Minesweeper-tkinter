import pytest
import tkinter as tk
from tkinter import Label, Frame
from classes import FlaggedCounter

@pytest.fixture
def flagged_counter_instance():
    root = tk.Tk()
    location = Frame(root)
    mines = 10
    font = ('Arial', 12)
    flagged_counter = FlaggedCounter(location, mines, font)
    yield flagged_counter
    root.destroy()

def test_initialization(flagged_counter_instance: FlaggedCounter):
    assert flagged_counter_instance.counter == 10
    assert isinstance(flagged_counter_instance.unflagged_count, Label)
    assert flagged_counter_instance.unflagged_count['text'] == "10🕸"

def test_update(flagged_counter_instance: FlaggedCounter):
    flagged_counter_instance.counter = 5
    flagged_counter_instance.update()
    assert flagged_counter_instance.unflagged_count['text'] == "05🕸"