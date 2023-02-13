"""Game of Minesweeper"""

import random
from tkinter import *

WIDTH = 9
HEIGHT = 9
CELL_SIZE = 70
MINES = 10
FONT_SIZE = int(CELL_SIZE / 2.2)
CELL_FONT = "Cooper Black"
SCOREBOARD_FONT = "Fixedsys"


class Game:
    """Make a game"""
    # Create main window
    root = Tk()
    active_game = None

    def __init__(self):
        Game.active_game = self
        Cell.left_click = Cell.first_move
        Cell.right_click = Cell.flag
        self.cell_grid = []
        self.all_mines = []
        self.not_mines = []
        self.unrevealed_cell_count = WIDTH * HEIGHT - MINES
        self.top_bar = self.create_top_bar()
        self.flagged_counter = FlaggedCounter(self.top_bar)
        self.timer = Timer(self.top_bar)
        self.reset_button = self.create_reset_button()
        self.minefield = self.create_minefield()
        self.generate_cells()
        self.generate_mines()

    @classmethod
    def root_settings_basic(cls):
        """Basic settings for root window"""
        cls.root.title("Minesweeper")

        # Bind escape to exit
        cls.root.bind("<Escape>", lambda e: cls.root.destroy())

        # Make scoreboard frame resizable
        cls.root.grid_rowconfigure(0, weight=1)
        cls.root.grid_columnconfigure(0, weight=1)

    @classmethod
    def root_settings_varied(cls):
        """Settings that change with game difficulty"""
        # Reset window size
        cls.root.geometry(f"{CELL_SIZE * WIDTH}x{CELL_SIZE * (HEIGHT + 1)}")

        # Make minefield frames resizeable depending on height
        cls.root.grid_rowconfigure(1, weight=HEIGHT)

    def create_top_bar(self):
        """Creates top bar"""
        top_bar = Frame(self.root, bd=6, relief="groove")

        # Make top bar resizeable
        top_bar.grid(column=0, row=0, sticky="EWNS")
        top_bar.grid_rowconfigure(0, weight=1)
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=1)
        top_bar.grid_columnconfigure(2, weight=1)

        return top_bar

    def create_minefield(self):
        """Minefield where main portion of the game takes place"""
        minefield = Frame(self.root, bd=6, relief="groove")
        minefield.grid(column=0, row=1, sticky="EWNS")

        # Make Buttons resizeable
        for i in range(HEIGHT):
            minefield.grid_rowconfigure(i, weight=1)
        for j in range(WIDTH):
            minefield.grid_columnconfigure(j, weight=1)
        return minefield

    def create_reset_button(self):
        """Create, place, and return reset button"""
        reset_button = Button(
            self.top_bar,
            text="RESET",
            font=(SCOREBOARD_FONT, FONT_SIZE),
            command=self.reset
        )
        reset_button.grid(column=1, row=0, sticky="EWNS")
        return reset_button

    def reset(self):
        """Restarts the game without changing settings"""
        self.top_bar.destroy()
        self.minefield.destroy()
        global FONT_SIZE
        FONT_SIZE = int(self.root.winfo_height() / ((HEIGHT+1)*2.2))
        self.__init__()

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

    def victory(self):
        """You win the game"""
        for mine in self.all_mines:
            # Flag all mines
            if not mine.flagged:
                mine.button.configure(
                    text="🏴", disabledforeground="#ab0000", state='disabled'
                )
        Game.active_game.flagged_counter.counter = 0
        Game.active_game.flagged_counter.update()
        self.reset_button.configure(text="WIN!!")
        self.game_over()

    def loss(self):
        """You lose the game"""
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
        """Game over general tasks"""
        self.timer.stop()
        Cell.left_click = Cell.disabled
        Cell.right_click = Cell.disabled


class Cell:
    """Make a cell"""

    # Cell control variable. Go from 'first_move' > 'regular_move' > 'disabled'
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
            font=(CELL_FONT, FONT_SIZE),
            width=1,
            height=1
        )
        self.button.bind("<Button-1>", lambda e: self.left_click())
        self.button.bind("<Button-3>", lambda e: self.right_click())

    def __repr__(self):
        return f"{self.coordinates}, {self.value}, {self.is_mine}"

    def first_move(self):
        """Is executed once during the game and then replaced with 'regular_move'"""
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
        Game.active_game.timer.start()
        self.reveal()
        Game.active_game.flagged_counter.update()
        Cell.left_click = Cell.regular_move

    def regular_move(self):
        """Left click action on an unrevealed cell"""
        if self.is_mine:
            self.button.configure(
                bg="#f20000",
                disabledforeground="gray",
                state="disabled",
                relief="sunken"
            )
            Game.active_game.loss()
        else:
            self.reveal()
            Game.active_game.flagged_counter.update()

    def reveal(self):
        """Show cell that is not a mine"""
        # Check for falsely flagged mines
        if self.flagged:
            self.button.configure(text="")
            self.flagged = False
            Game.active_game.flagged_counter.counter += 1

        # Change buttons to represent revealed cell
        self.button.configure(state="disabled", relief="sunken")
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

        Game.active_game.unrevealed_cell_count -= 1
        if Game.active_game.unrevealed_cell_count == 0:
            Game.active_game.victory()

    def flag(self):
        """Set or remove flag that indicates a potential mine"""
        if self.flagged:
            self.button.configure(
                text="", disabledforeground="black", state='normal'
            )
            self.flagged = False
            # Delete instance variable disabling cell
            del self.left_click
            Game.active_game.flagged_counter.counter += 1
        else:
            self.button.configure(
                text="🏴", disabledforeground="#ab0000", state="disabled"
            )
            self.flagged = True
            # Disable control in instance variable
            self.left_click = self.disabled
            Game.active_game.flagged_counter.counter -= 1
        Game.active_game.flagged_counter.update()

    @staticmethod
    def disabled(*args):
        """Do nothing. Use this to disable controls on buttons as needed"""
        pass


class Timer:
    """Keeps track of time elapsed"""
    def __init__(self, location):
        self.counter = 0
        self.updating = None
        self.clock = Label(
            location,
            text='⏱0000',
            font=(SCOREBOARD_FONT, FONT_SIZE),
            bd=6,
            padx=20,
            relief='ridge',
            fg='green',
            bg='black'
        )
        self.clock.grid(column=2, row=0)

    def update(self):
        """Add a second to clock every second"""
        self.clock.configure(text=f"⏱{self.counter:04d}")
        self.counter += 1
        self.updating = self.clock.after(1000, self.update)

    def start(self):
        self.update()

    def stop(self):
        self.clock.after_cancel(self.updating)


class FlaggedCounter:
    """Shows how many mines are still un-flagged"""
    def __init__(self, location):
        self.counter = MINES
        self.unflagged_count = Label(
            location,
            text=f'{self.counter:02d}🕸',
            font=(SCOREBOARD_FONT, FONT_SIZE),
            bd=6,
            padx=20,
            relief='ridge',
            fg='green',
            bg='black'
        )
        self.unflagged_count.grid(column=0, row=0)

    def update(self):
        """Update label with new count"""
        self.unflagged_count.configure(text=f'{self.counter:02d}🕸')


if __name__ == "__main__":
    Game.root_settings_basic()
    Game.root_settings_varied()
    Game()
    Game.root.mainloop()
