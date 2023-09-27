import pytest
import time
import tkinter as tk
from tkinter import Label, Frame
from classes import Timer

@pytest.fixture
def timer_instance():
    root = tk.Tk()
    location = Frame(root)
    font = ('Arial', 12)
    timer = Timer(location, font)
    yield timer
    root.destroy()

def test_initialization(timer_instance: Timer):
    assert timer_instance.counter == 0
    assert timer_instance.updating is None
    assert isinstance(timer_instance.clock, Label)

def test_start(timer_instance: Timer):
    timer_instance.start()
    assert timer_instance.updating is not None
    assert timer_instance.clock['text'] == "⏱0000"
    assert timer_instance.counter == 1
