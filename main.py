"""Game of Minesweeper

Includes customizable difficulty, timer, 'mines left' counter.
First move is always safe, the mine gets transported to a random cell.
Settings are saved between games in a config.ini file,
you can also customize said file to change fonts and difficulty
"""

import random
import sys
from tkinter import Tk, Frame, Button, Menu
from classes import Cell, Timer, Config, FlaggedCounter

def main():
    """Simple steps to run the game"""
    # Create main game window with settings.
    active_game = Game()

    # Initialise the game.
    active_game.start()

    # Mainloop must be outside of .start(), as otherwise it will be recreated during
    # restart and leak memory.
    active_game.root.mainloop()


class Game:
    """Holds the main game logic"""

    def __init__(self):
        # Main window is not recreated to keep window size between resets
        self.root = Tk()

        # Allows other classes to interact with main game.
        self.settings = Config(self)
        Cell.active_game = self

        # Modify main game window with prepared settings
        self.root_settings_varied()
        self.root_settings_basic()

        # Declare future variables
        self.cell_grid: list[list[Cell]]
        self.all_mines: list[Cell]
        self.not_mines: list[Cell]

        self.top_bar: Frame
        self.minefield: Frame

        self.reset_button: Button
        self.flagged_counter: FlaggedCounter
        self.timer: Timer

        # End game condition. Hitting 0 ends the game.
        self.unrevealed_cell_count: int

    def start(self):
        """ Start or restart the game.
        Creates everything unique per game.
        Sets Cell behavior to starting value. 
        """
        Cell.left_click = Cell.first_move
        Cell.right_click = Cell.flag

        # Top Bar Creation and population
        self.unrevealed_cell_count = self.settings.unrevealed_cell_count()
        self.create_top_bar()
        self.flagged_counter = FlaggedCounter(
            self.top_bar,
            self.settings.mines,
            (self.settings.scoreboard_font, self.settings.font_size)
        )
        self.timer = Timer(
            self.top_bar, (self.settings.scoreboard_font, self.settings.font_size))
        self.create_reset_button()

        # Minefield creation and population
        self.create_minefield()
        self.generate_cells()
        self.generate_mines()

    def root_settings_basic(self):
        """Basic settings for root window, only executed at launch"""
        # Increase recursion limit for those huge games with not that many mines
        sys.setrecursionlimit(2000)

        self.root.title("Minesweeper")

        # Creating menu bar before icon. 
        # For some reason reduces initial resolution by 20px if placed incorrectly.
        # Be wary of moving it anywhere later in code
        self.create_difficulty_menubar()

        self.root.iconbitmap(Config.icon_file)

        # Bind escape and 'X' button to make game save settings on exit
        self.root.bind("<Escape>", self.save_and_exit)
        self.root.protocol("WM_DELETE_WINDOW", self.save_and_exit)

        # Make scoreboard frame resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def root_settings_varied(self):
        """Settings that change with game size"""
        # Reset window size
        self.root.geometry(self.settings.resolution)

        # Make minefield frames resizable depending on height
        self.root.grid_rowconfigure(1, weight=self.settings.cell_height)

    def create_difficulty_menubar(self):
        """Create menubar that lets you select difficulty"""
        menubar = Menu(self.root)
        menubar.add_command(label='Beginner 9x9',
                            command=lambda: self.settings.change_difficulty(9, 9, 10))
        menubar.add_command(label='Intermediate 16x16',
                            command=lambda: self.settings.change_difficulty(16, 16, 40))
        menubar.add_command(label='Expert 30x16',
                            command=lambda: self.settings.change_difficulty(30, 16, 99))
        menubar.add_command(label='Custom',
                            command=lambda: self.settings.custom_settings_popup(self.root))
        self.root['menu'] = menubar

    def save_and_exit(self, event=None):
        """Save settings before exiting game"""
        self.settings.save_config()
        self.root.destroy()

    def create_top_bar(self):
        """Creates top bar that holds mines left counter, restart button and timer"""
        self.top_bar = Frame(self.root, bd=6, relief="groove")

        # Make top bar resizable
        self.top_bar.grid(column=0, row=0, sticky="EWNS")
        self.top_bar.grid_rowconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_columnconfigure(2, weight=1)

    def create_minefield(self):
        """Field where the main portion of the game takes place"""
        self.minefield = Frame(self.root, bd=6, relief="groove")
        self.minefield.grid(column=0, row=1, sticky="EWNS")

        # Make Buttons resizable
        for i in range(self.settings.cell_height):
            self.minefield.grid_rowconfigure(i, weight=1)
        for j in range(self.settings.cell_width):
            self.minefield.grid_columnconfigure(j, weight=1)

    def create_reset_button(self):
        """Create button that resets the game without changing window size"""
        self.reset_button = Button(
            self.top_bar,
            text="RESET",
            font=(self.settings.scoreboard_font, self.settings.font_size),
            command=self.reset
        )
        self.reset_button.grid(column=1, row=0, sticky="EWNS")

    def restart(self):
        """Restarts the game without changing settings"""
        self.top_bar.destroy()
        self.minefield.destroy()
        self.start()

    def reset(self):
        """Reset button restarts while adjusting font to new resolution"""
        self.settings.recalculate_font()
        self.restart()

    def generate_cells(self):
        """Populates play field with Cells that contain buttons and attributes.
        Store them all in a grid shape list to check neighboring mines later.
        And in a basic list for mine generation"""
        self.cell_grid = []
        self.not_mines = []

        for x in range(self.settings.cell_width):
            column = []
            for y in range(self.settings.cell_height):
                new_cell = Cell(self.minefield, (x, y))
                new_cell.button.grid(column=x, row=y, sticky="EWNS")
                column.append(new_cell)
                self.not_mines.append(new_cell)
            self.cell_grid.append(column)

    def generate_mines(self):
        """Make cells into mines and save them to a lists. Mine list will be used during
        win/loss to highlight unrevealed and unmarked mines.
        Recreate list of not mines to calculate their values and move a mine on first move.
        """
        self.all_mines = random.sample(self.not_mines, self.settings.mines)
        for mine in self.all_mines:
            mine.is_mine = True

        # Remove created mines from list
        self.not_mines = [cell for cell in self.not_mines if not cell.is_mine]

    def find_neighbors(self, cell: Cell):
        """Return list of cell's neighbors while filtering out cells beyond the edge"""
        x, y = cell.coordinates
        neighbors = (
            (x - 1, y - 1),
            (x - 1, y),
            (x - 1, y + 1),
            (x, y - 1),
            (x, y + 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
        )
        return (
            self.cell_grid[i][j]
            for i, j in neighbors
            if 0 <= i < self.settings.cell_width and 0 <= j < self.settings.cell_height
        )

    def cell_value(self):
        """For every cell that is not a mine, calculate how many mines are in
        the surrounding cells. Save it in that cell's attribute"""
        for cell in self.not_mines:
            neighbors = self.find_neighbors(cell)
            value = 0
            for neighbor in neighbors:
                if neighbor.is_mine:
                    value += 1
                cell.value = value

    def victory(self):
        """You win the game when all non mine cells have been revealed"""
        for mine in self.all_mines:
            # Flag all mines not flagged by the player
            if not mine.flagged:
                mine.button.configure(
                    text="🏴", disabledforeground="#ab0000", state='disabled'
                )
        self.flagged_counter.counter = 0
        self.flagged_counter.update()
        self.reset_button.configure(text="WIN!!")
        self.game_over()

    def loss(self):
        """You lose the game when you try to reveal a mine"""
        for mine in self.all_mines:
            # Reveal un-flagged mines
            if not mine.flagged:
                mine.button.configure(text="🕸", state='disabled')
        for not_mine in self.not_mines:
            # Highlight falsely flagged mines, they are already disabled from Flag
            if not_mine.flagged:
                not_mine.button.configure(bg='#ffbdb3')
            # Disable unrevealed buttons
            elif not not_mine.revealed:
                not_mine.button.configure(state='disabled')
        self.reset_button.configure(text="LOST!")
        self.game_over()

    def game_over(self):
        """Game over general tasks. Stop the timer, disable controls"""
        self.timer.stop()
        Cell.left_click = Cell.disabled
        Cell.right_click = Cell.disabled


if __name__ == "__main__":
    main()
