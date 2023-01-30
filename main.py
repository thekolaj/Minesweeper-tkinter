"""Game of Minesweeper"""

import random
from tkinter import *

WIDTH = 9
HEIGHT = 9
CELL_SIZE = 80
MINES = 10


class Game:
    """Make a game"""

    active_game = None
    # Create main window
    root = Tk()
    root.title("Minesweeper")

    # Bind escape to exit
    root.bind("<Escape>", lambda e: Game.root.destroy())

    # Create frames for scoreboard and game field
    top_bar = Frame(root, bd=6, relief="groove")
    minefield = Frame(root, bd=6, relief="groove")
    top_bar.grid(column=0, row=0, sticky="EWNS")
    minefield.grid(column=0, row=1, sticky="EWNS")

    def __init__(self):
        Game.active_game = self
        Cell.left_click = Cell.first_move
        Cell.right_click = Cell.flag
        self.cell_grid = []
        self.all_mines = []
        self.not_mines = []
        self.graphics()
        self.scoreboard()
        self.generate_cells()
        self.generate_mines()
        self.root.mainloop()

    @classmethod
    def graphics(cls):
        """Configure graphics based on options"""
        # Reset window size
        cls.root.geometry(f"{CELL_SIZE * WIDTH}x{CELL_SIZE * (HEIGHT + 1)}")

        # Make frames resizeable depending on height
        cls.root.grid_rowconfigure(0, weight=1)
        cls.root.grid_rowconfigure(1, weight=HEIGHT)
        cls.root.grid_columnconfigure(0, weight=1)

        # Make scoreboard resizeable
        cls.top_bar.grid_rowconfigure(0, weight=1)
        cls.top_bar.grid_columnconfigure(0, weight=1)
        cls.top_bar.grid_columnconfigure(1, weight=1)
        cls.top_bar.grid_columnconfigure(2, weight=1)

        # Make Buttons resizeable
        for i in range(HEIGHT):
            cls.minefield.grid_rowconfigure(i, weight=1)
        for j in range(WIDTH):
            cls.minefield.grid_columnconfigure(j, weight=1)

    def scoreboard(self):
        """Generate scoreboard"""
        reset_button = Button(
            self.top_bar,
            text="Reset",
            font=("", 36),
            width=1,
            height=1,
            command=self.__init__,
        )
        reset_button.grid(column=1, row=0, sticky="EWNS")

    def generate_cells(self):
        """Generate the playing field"""
        for x in range(WIDTH):
            column = []
            for y in range(HEIGHT):
                new_cell = Cell(self.minefield, (x, y))
                new_cell.button.grid(column=x, row=y, sticky="EWNS")
                column.append(new_cell)
                self.not_mines.append(new_cell)
            self.cell_grid.append(column)

    def generate_mines(self):
        """Make cells into mines and save them to lists"""
        self.all_mines = random.sample(self.not_mines, MINES)
        for mine in self.all_mines:
            mine.is_mine = True

        # Remove mines from list
        self.not_mines = [cell for cell in self.not_mines if not cell.is_mine]

    def find_neighbors(self, cell):
        """Return list of cell's neighbors"""
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
            if 0 <= i < WIDTH and 0 <= j < HEIGHT
        ]

    def cell_value(self):
        """Calculate how many mines are in surrounding cells"""
        for cell in self.not_mines:
            neighbors = self.find_neighbors(cell)
            value = 0
            for neighbor in neighbors:
                if neighbor.is_mine:
                    value += 1
                cell.value = value

    def game_over(self):
        """Game over. Reveal all mines, disable buttons."""
        for mine in self.all_mines:
            if not mine.flagged:
                mine.button.configure(text="🕸", state='disabled')
        for not_mine in self.not_mines:
            # Highlight falsely flagged mines, they are already disabled from Flag
            if not_mine.flagged:
                not_mine.button.configure(bg='#ffbdb3')
            # Disable unrevealed buttons
            elif not not_mine.revealed:
                not_mine.button.configure(state='disabled')

        Cell.left_click = Cell.disabled
        Cell.right_click = Cell.disabled


class Cell:
    """Make a cell"""

    # Cell control variable. Go from 'first_move' > 'reveal' > 'disabled'
    left_click = None
    right_click = None

    def __init__(self, location, coordinates):
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
            font=("Cooper Black", 36),
            width=1,
            height=1,
        )
        self.button.bind("<Button-1>", lambda e: self.left_click())
        self.button.bind("<Button-3>", lambda e: self.right_click())

    def __repr__(self):
        return f"{self.coordinates}, {self.value}, {self.is_mine}"

    def first_move(self):
        """Is executed once during the game and then replaced with 'reveal'"""
        if self.is_mine:
            # Remove mine from first clicked cell
            self.is_mine = False

            # Make random cell a new mine
            replacement_mine = random.choice(Game.active_game.not_mines)
            replacement_mine.is_mine = True

            # Update lists
            Game.active_game.all_mines.remove(self)
            Game.active_game.not_mines.append(self)
            Game.active_game.not_mines.remove(replacement_mine)
            Game.active_game.all_mines.append(replacement_mine)
        Game.active_game.cell_value()
        self.reveal()
        Cell.left_click = Cell.reveal

    def reveal(self):
        """Left click action on an unrevealed cell"""
        # Every button gets sunken and disable after click
        self.button.configure(state="disabled", relief="sunken")
        if self.is_mine:
            self.button.configure(bg="#f20000", disabledforeground="gray")
            Game.active_game.game_over()
        else:
            self.revealed = True
            if self.value == 0:
                for neighbor in Game.active_game.find_neighbors(self):
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

    def flag(self):
        """Set or remove flag that indicates a potential mine"""
        if self.flagged:
            self.button.configure(
                text="", disabledforeground="black", state='normal'
            )
            self.flagged = False
            # Delete instance variable disabling cell
            del self.left_click
        else:
            self.button.configure(
                text="🏴", disabledforeground="#ab0000", state="disabled"
            )
            self.flagged = True
            # Disable control in instance variable
            self.left_click = self.disabled

    @staticmethod
    def disabled(*args):
        """Do nothing. Use this to disable controls on buttons as needed"""
        pass


if __name__ == "__main__":
    Game()
