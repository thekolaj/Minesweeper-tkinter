import pytest
import random
from main import Game
from classes import Cell


@pytest.fixture
def game_instance():
    random.seed(0)
    active_game = Game()
    active_game.settings.cell_width = 9
    active_game.settings.cell_height = 9
    active_game.settings.mines = 10
    active_game.start()
    yield active_game
    active_game.root.destroy()

def test_lists(game_instance: Game):
    assert len(game_instance.all_mines) == 10
    assert len(game_instance.not_mines) == 71
    assert game_instance.cell_grid[5][0].is_mine
    assert not game_instance.cell_grid[0][0].is_mine

def test_control_flag(game_instance: Game):
    assert game_instance.cell_grid[5][0].button["text"] == ""
    assert game_instance.cell_grid[5][0].button["state"] == "normal"
    game_instance.cell_grid[5][0].flag()
    assert game_instance.cell_grid[5][0].button["text"] == "🏴"
    assert game_instance.cell_grid[5][0].button["state"] == "disabled"
    game_instance.cell_grid[5][0].flag()
    assert game_instance.cell_grid[5][0].button["text"] == ""
    assert game_instance.cell_grid[5][0].button["state"] == "normal"

def test_first_move(game_instance: Game):
    assert game_instance.cell_grid[5][0].is_mine
    assert Cell.left_click == Cell.first_move
    game_instance.cell_grid[5][0].first_move()
    assert not game_instance.cell_grid[5][0].is_mine
    assert Cell.left_click == Cell.regular_move
    assert game_instance.timer.updating is not None
    assert game_instance.cell_grid[4][1].value == 2

def test_game_over_loss(game_instance: Game):
    game_instance.cell_grid[0][0].first_move()
    game_instance.cell_grid[5][0].regular_move()
    assert game_instance.cell_grid[5][0].button["text"] == "🕸"
    assert game_instance.reset_button['text'] == "LOST!"

def test_game_over_victory():
    random.seed(0)
    active_game = Game()
    active_game.settings.cell_width = 9
    active_game.settings.cell_height = 9
    active_game.settings.mines = 1
    active_game.start()
    active_game.cell_grid[0][0].first_move()
    assert active_game.cell_grid[5][4].button["text"] == "🏴"
    assert active_game.reset_button['text'] == "WIN!!"
    active_game.root.destroy()
