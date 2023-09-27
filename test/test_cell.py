import pytest
import tkinter as tk
from tkinter import Button, Frame
from classes import Cell 

# Mock Game class
class MockGame:
    def __init__(self):
        self.settings = MockSettings()

class MockSettings:
    cell_font = 'Arial'
    font_size = 12

@pytest.fixture
def cell_instance():
    root = tk.Tk()
    location = Frame(root)
    coordinates = (0, 0)
    Cell.active_game = MockGame()
    cell = Cell(location, coordinates)
    yield cell
    root.destroy()

def test_initialization(cell_instance: Cell):    
    assert not cell_instance.is_mine
    assert not cell_instance.flagged
    assert not cell_instance.revealed
    assert cell_instance.value == 0
    assert cell_instance.coordinates == (0, 0)
    assert isinstance(cell_instance.button, Button)


