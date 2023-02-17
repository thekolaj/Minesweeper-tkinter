"""Game of Minesweeper"""

import random
from tkinter import *
from configparser import ConfigParser


class Game:
    """Make a game"""
    # Main window lives in class and is not recreated to keep window size between resets
    root = Tk()

    def __init__(self):
        Cell.left_click = Cell.first_move
        Cell.right_click = Cell.flag
        self.cell_grid = []
        self.all_mines = []
        self.not_mines = []
        self.unrevealed_cell_count = settings.unrevealed_cell_count()
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
        cls.root.iconbitmap('mine.ico')

        # Bind escape to exit
        cls.root.bind("<Escape>", lambda e: cls.root.destroy())

        # Make scoreboard frame resizable
        cls.root.grid_rowconfigure(0, weight=1)
        cls.root.grid_columnconfigure(0, weight=1)

        # Disable tear-off menus
        cls.root.option_add('*tearOff', FALSE)

    @classmethod
    def root_settings_varied(cls):
        """Settings that change with game difficulty"""
        # Reset window size
        cls.root.geometry(settings.resolution)

        # Make minefield frames resizeable depending on height
        cls.root.grid_rowconfigure(1, weight=settings.cell_height)

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
        for i in range(settings.cell_height):
            minefield.grid_rowconfigure(i, weight=1)
        for j in range(settings.cell_width):
            minefield.grid_columnconfigure(j, weight=1)
        return minefield

    def create_reset_button(self):
        """Create, place, and return reset button"""
        reset_button = Button(
            self.top_bar,
            text="RESET",
            font=(settings.scoreboard_font, settings.font_size),
            command=self.reset
        )
        reset_button.grid(column=1, row=0, sticky="EWNS")
        return reset_button

    def reset(self):
        """Restarts the game without changing settings"""
        self.top_bar.destroy()
        self.minefield.destroy()
        settings.recalculate_font()
        self.__init__()

    def generate_cells(self):
        """Generate the playing field"""
        for x in range(settings.cell_width):
            column = []
            for y in range(settings.cell_height):
                new_cell = Cell(self.minefield, (x, y))
                new_cell.button.grid(column=x, row=y, sticky="EWNS")
                column.append(new_cell)
                self.not_mines.append(new_cell)
            self.cell_grid.append(column)

    def generate_mines(self):
        """Make cells into mines and save them to lists"""
        self.all_mines = random.sample(self.not_mines, settings.mines)
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
            if 0 <= i < settings.cell_width and 0 <= j < settings.cell_height
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
        self.flagged_counter.counter = 0
        self.flagged_counter.update()
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
            font=(settings.cell_font, settings.font_size),
            width=1,
            height=1
        )
        self.button.bind("<Button-1>", lambda e: self.left_click())
        self.button.bind("<Button-3>", lambda e: self.right_click())

    def first_move(self):
        """Is executed once during the game and then replaced with 'regular_move'"""
        if self.is_mine:
            # Remove mine from first clicked cell
            self.is_mine = False

            # Make random cell a new mine
            replacement_mine = random.choice(active_game.not_mines)
            replacement_mine.is_mine = True

            # Update lists
            active_game.all_mines.remove(self)
            active_game.not_mines.append(self)
            active_game.not_mines.remove(replacement_mine)
            active_game.all_mines.append(replacement_mine)
        active_game.cell_value()
        active_game.timer.start()
        self.reveal()
        active_game.flagged_counter.update()
        Cell.left_click = Cell.regular_move

    def regular_move(self):
        """Left click action on an unrevealed cell"""
        if self.is_mine:
            self.button.configure(
                bg="#f20000",
                disabledforeground="gray",
                relief="sunken"
            )
            active_game.loss()
        else:
            self.reveal()
            active_game.flagged_counter.update()

    def reveal(self):
        """Show cell that is not a mine"""
        # Check for falsely flagged mines
        if self.flagged:
            self.button.configure(text="")
            self.flagged = False
            active_game.flagged_counter.counter += 1

        # Change buttons to represent revealed cell
        self.button.configure(state="disabled", relief="sunken")
        self.revealed = True
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
            # Delete instance variable disabling cell
            del self.left_click
            active_game.flagged_counter.counter += 1
        else:
            self.button.configure(
                text="🏴", disabledforeground="#ab0000", state="disabled"
            )
            self.flagged = True
            # Disable control in instance variable
            self.left_click = self.disabled
            active_game.flagged_counter.counter -= 1
        active_game.flagged_counter.update()

    @staticmethod
    def disabled(*args):
        """Do nothing. Use this to disable controls on buttons as needed"""
        pass


class DifficultyMenu:
    """Changes difficulty of the game"""
    def __init__(self, location):
        pass




class Timer:
    """Keeps track of time elapsed"""
    def __init__(self, location):
        self.counter = 0
        self.updating = None
        self.clock = Label(
            location,
            text='⏱0000',
            font=(settings.scoreboard_font, settings.font_size),
            bd=6,
            padx=20,
            pady=10,
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
        self.counter = settings.mines
        self.unflagged_count = Label(
            location,
            text=f'{self.counter:02d}🕸',
            font=(settings.scoreboard_font, settings.font_size),
            bd=6,
            padx=20,
            pady=10,
            relief='ridge',
            fg='green',
            bg='black'
        )
        self.unflagged_count.grid(column=0, row=0)

    def update(self):
        """Update label with new count"""
        self.unflagged_count.configure(text=f'{self.counter:02d}🕸')


class Config:
    """Generates, stores and recalculates all of games settings"""
    def __init__(self):
        self.cell_width = 9
        self.cell_height = 9
        self.mines = 10
        self.cell_size = 40
        self.font_modifier = 0.5
        self.resolution = self.calculate_resolution()
        self.font_size = int(self.cell_size * self.font_modifier)
        self.cell_font = "Cooper Black"
        self.scoreboard_font = "Fixedsys"

    def calculate_resolution(self):
        """Resolution adjusts to game size"""
        return f"{self.cell_size*self.cell_width}x{self.cell_size*(self.cell_height+1)}"

    def recalculate_font(self):
        """Adjust font to better suit potentially resized window"""
        self.font_size = int(
            Game.root.winfo_height() / (self.cell_height+1) * self.font_modifier)

    def unrevealed_cell_count(self):
        """How many cells need to be revealed to win the game"""
        return self.cell_width * self.cell_height - self.mines

    def change_difficulty(self, x, y, m):
        """Sets new difficulty settings and resets the game

        :param int x: new cell width
        :param int y: new cell height
        :param int m: new number of mines
        """
        self.cell_width = x
        self.cell_height = y
        self.mines = m
        self.resolution = self.calculate_resolution()
        Game.root_settings_varied()
        active_game.reset()


if __name__ == "__main__":
    settings = Config()
    Game.root_settings_basic()
    Game.root_settings_varied()
    active_game = Game()
    Game.root.mainloop()
