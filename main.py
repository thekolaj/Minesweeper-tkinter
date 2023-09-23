"""Game of Minesweeper

Includes customizable difficulty, timer, 'mines left' counter.
First move is always safe, the mine gets transported to a random cell.
Settings are saved between games in a config.ini file,
you can also customize said file to change fonts and difficulty
"""

import random
import sys
from tkinter import *
from timer_ import Timer
from config import Config
from flagged_counter import FlaggedCounter


class Game:
    """Holds the main game logic, and appearance. Brings everything else together"""
    def __init__(self):
        # Main window is not recreated to keep window size between resets
        self.root = Tk()
        self.settings = Config(self)

        # Modify main game window with prepared settings
        self.root_settings_varied()
        self.root_settings_basic()
        

    def start(self):
        # Everything below gets recreated during restart
        Cell.left_click = Cell.first_move
        Cell.right_click = Cell.flag
        self.cell_grid = []
        self.all_mines = []
        self.not_mines = []
        self.unrevealed_cell_count = self.settings.unrevealed_cell_count()
        self.top_bar = self.create_top_bar()
        self.flagged_counter = FlaggedCounter(
            self.top_bar,
            self.settings.mines,
            (self.settings.scoreboard_font, self.settings.font_size)
            )
        self.timer = Timer(self.top_bar, (self.settings.scoreboard_font, self.settings.font_size))
        self.reset_button = self.create_reset_button()
        self.minefield = self.create_minefield()
        self.generate_cells()
        self.generate_mines()

    def root_settings_basic(self):
        """Basic settings for root window, only executed at launch"""
        # Increase recursion limit for those huge games with not that many mines
        sys.setrecursionlimit(2000)

        self.root.title("Minesweeper")

        # Creating menu bar after icon for some reason reduces initial resolution by 20px
        # Be wary of moving it anywhere later in code
        self.create_difficulty_menubar()

        self.root.iconbitmap('mine.ico')

        # Bind escape and 'X' button to make game save settings on exit
        self.root.bind("<Escape>", self.save_and_exit)
        self.root.protocol("WM_DELETE_WINDOW", self.save_and_exit)

        # Make scoreboard frame resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


    def root_settings_varied(self):
        """Settings that change with game difficulty"""
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
        top_bar = Frame(self.root, bd=6, relief="groove")

        # Make top bar resizable
        top_bar.grid(column=0, row=0, sticky="EWNS")
        top_bar.grid_rowconfigure(0, weight=1)
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=1)
        top_bar.grid_columnconfigure(2, weight=1)

        return top_bar

    def create_minefield(self):
        """Field where the main portion of the game takes place"""
        minefield = Frame(self.root, bd=6, relief="groove")
        minefield.grid(column=0, row=1, sticky="EWNS")

        # Make Buttons resizable
        for i in range(self.settings.cell_height):
            minefield.grid_rowconfigure(i, weight=1)
        for j in range(self.settings.cell_width):
            minefield.grid_columnconfigure(j, weight=1)
        return minefield

    def create_reset_button(self):
        """Create button that resets the game without changing window size"""
        reset_button = Button(
            self.top_bar,
            text="RESET",
            font=(self.settings.scoreboard_font, self.settings.font_size),
            command=self.reset
        )
        reset_button.grid(column=1, row=0, sticky="EWNS")
        return reset_button

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

        # Remove mines from list
        self.not_mines = [cell for cell in self.not_mines if not cell.is_mine]

    def find_neighbors(self, cell):
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
        return [
            self.cell_grid[i][j]
            for i, j in neighbors
            if 0 <= i < self.settings.cell_width and 0 <= j < self.settings.cell_height
        ]

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


class Cell:
    """Make a cell that contains a button and some attributes"""
    # Cell control. Change cell behavior without rebinding every individual cell.
    # Left click goes from 'first_move' > 'regular_move' > 'disabled'
    left_click: callable = None
    # Right click is 'flag' or 'disabled'
    right_click: callable = None

    def __init__(self, location, coordinates):
        """
        :param tkinter.Frame location: Minefield frame
        :param (int, int) coordinates: x and y in the grid to look up neighbors
        """
        self.is_mine = False
        self.flagged = False
        self.revealed = False
        self.value = 0
        self.coordinates = coordinates

        # Create tkinter button
        self.button = Button(
            location,
            text="",
            disabledforeground="black",
            bd=4,
            font=(active_game.settings.cell_font, active_game.settings.font_size),
            width=1,
            height=1
        )
        self.button.bind("<Button-1>", lambda e: self.left_click())
        self.button.bind("<Button-3>", lambda e: self.right_click())

    def first_move(self):
        """Executed once at the start of the game and replaced with 'regular_move'.
        Makes first move safe, calculates values, starts timer, reveals cell.
        """
        # Check if the first cell opened is a mine and move it to different cell
        if self.is_mine:
            # Remove mine from first clicked cell
            self.is_mine = False

            # Make random cell a new mine
            replacement_mine = random.choice(active_game.not_mines)
            replacement_mine.is_mine = True

            # Update corresponding lists
            active_game.all_mines.remove(self)
            active_game.not_mines.append(self)
            active_game.not_mines.remove(replacement_mine)
            active_game.all_mines.append(replacement_mine)

        # Fill in value for all none mine cells. Done after all mine placement is finalized
        active_game.cell_value()

        Cell.left_click = Cell.regular_move
        active_game.timer.start()
        self.reveal()

        # Update counter for an edge case where player flagged some random squares
        # at the start of the game and then hit a 0 to reveal some of those flagged cells
        active_game.flagged_counter.update()

    def regular_move(self):
        """Checks if you lost the game by hitting a mine. Otherwise, reveals cell"""
        if self.is_mine:
            self.button.configure(
                bg="#f20000",
                disabledforeground="gray",
                relief="sunken"
            )
            active_game.loss()
        else:
            self.reveal()
            # Update counter in case of hitting 0 to reveal some of falsely flagged cells
            active_game.flagged_counter.update()

    def reveal(self):
        """Show value of a cell that is not a mine
        Calls itself recursively if you hit a 0 (black space)
        """
        # Check for falsely flagged mines, used during recursion call when you hit 0
        if self.flagged:
            self.button.configure(text="")
            self.flagged = False
            active_game.flagged_counter.counter += 1

        # Change buttons to represent revealed cell
        self.button.configure(state="disabled", relief="sunken")
        self.revealed = True
        # If you hit a 0 (black space), reveals cells next to self
        if self.value == 0:
            for neighbor in active_game.find_neighbors(self):
                if not neighbor.revealed:
                    neighbor.reveal()
        elif self.value == 1:
            self.button.configure(text='1', disabledforeground="#261cd9")
        elif self.value == 2:
            self.button.configure(text='2', disabledforeground="#0ea124")
        elif self.value == 3:
            self.button.configure(text='3', disabledforeground="#ed0202")
        elif self.value == 4:
            self.button.configure(text='4', disabledforeground="#140159")
        elif self.value == 5:
            self.button.configure(text='5', disabledforeground="#630104")
        elif self.value == 6:
            self.button.configure(text='6', disabledforeground="#00ced1")
        elif self.value == 7:
            self.button.configure(text='7', disabledforeground="black")
        elif self.value == 8:
            self.button.configure(text='8', disabledforeground="gray")

        # Individually disable buttons for revealed cells in instance variables
        self.left_click = self.disabled
        self.right_click = self.disabled

        # Update the victory condition and check if it was met
        active_game.unrevealed_cell_count -= 1
        if active_game.unrevealed_cell_count == 0:
            active_game.victory()

    def flag(self):
        """Set or remove flag that indicates a potential mine"""
        if self.flagged:
            self.button.configure(
                text="", disabledforeground="black", state='normal'
            )
            self.flagged = False
            # Delete instance attribute that is disabling cell, reactivating it.
            del self.left_click
            active_game.flagged_counter.counter += 1
        else:
            self.button.configure(
                text="🏴", disabledforeground="#ab0000", state="disabled"
            )
            self.flagged = True
            # Disable control in instance attribute. All other cells still use
            # class attribute and thus remain active
            self.left_click = self.disabled
            active_game.flagged_counter.counter -= 1
        active_game.flagged_counter.update()

    @staticmethod
    def disabled(*args):
        """Do nothing. Used to disable controls on buttons as needed"""
        pass

if __name__ == "__main__":
    # Prepare all the settings for the game
    
    # Start the game.
    active_game = Game()

    active_game.start()
    # Mainloop must be outside active game, as otherwise it will be recreated during
    # restart and leak memory.
    active_game.root.mainloop()
