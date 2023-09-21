"""Game of Minesweeper

Includes customizable difficulty, timer, 'mines left' counter.
First move is always safe, the mine gets transported to a random cell.
Settings are saved between games in a config.ini file,
you can also customize said file to change fonts and difficulty
"""
import _tkinter
import random
import sys
from os.path import exists
from tkinter import *
from configparser import ConfigParser


class Game:
    """Holds the main game logic, and appearance. Brings everything else together"""
    # Main window lives in class and is not recreated to keep window size between resets
    root = Tk()

    def __init__(self):
        # Everything below gets recreated during restart
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
        """Basic settings for root window, only executed at launch"""
        # Increase recursion limit for those huge games with not that many mines
        sys.setrecursionlimit(2000)

        cls.root.title("Minesweeper")

        # Creating menu bar after icon for some reason reduces initial resolution by 20px
        # Be wary of moving it anywhere later in code
        cls.create_difficulty_menubar()

        cls.root.iconbitmap('mine.ico')

        # Bind escape and 'X' button to make game save settings on exit
        cls.root.bind("<Escape>", cls.save_and_exit)
        cls.root.protocol("WM_DELETE_WINDOW", cls.save_and_exit)

        # Make scoreboard frame resizable
        cls.root.grid_rowconfigure(0, weight=1)
        cls.root.grid_columnconfigure(0, weight=1)


    @classmethod
    def root_settings_varied(cls):
        """Settings that change with game difficulty"""
        # Reset window size
        cls.root.geometry(settings.resolution)

        # Make minefield frames resizable depending on height
        cls.root.grid_rowconfigure(1, weight=settings.cell_height)

    @classmethod
    def create_difficulty_menubar(cls):
        """Create menubar that lets you select difficulty"""
        menubar = Menu(cls.root)
        menubar.add_command(label='Beginner 9x9',
                            command=lambda: settings.change_difficulty(9, 9, 10))
        menubar.add_command(label='Intermediate 16x16',
                            command=lambda: settings.change_difficulty(16, 16, 40))
        menubar.add_command(label='Expert 30x16',
                            command=lambda: settings.change_difficulty(30, 16, 99))
        menubar.add_command(label='Custom',
                            command=lambda: settings.custom_settings_popup(cls.root))
        cls.root['menu'] = menubar

    @classmethod
    def save_and_exit(cls, event=None):
        """Save settings before exiting game"""
        settings.save_config()
        cls.root.destroy()

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

        # Make Buttons resizeable
        for i in range(settings.cell_height):
            minefield.grid_rowconfigure(i, weight=1)
        for j in range(settings.cell_width):
            minefield.grid_columnconfigure(j, weight=1)
        return minefield

    def create_reset_button(self):
        """Create button that resets the game without changing window size"""
        reset_button = Button(
            self.top_bar,
            text="RESET",
            font=(settings.scoreboard_font, settings.font_size),
            command=self.reset
        )
        reset_button.grid(column=1, row=0, sticky="EWNS")
        return reset_button

    def restart(self):
        """Restarts the game without changing settings"""
        self.top_bar.destroy()
        self.minefield.destroy()
        self.__init__()

    def reset(self):
        """Reset button restarts while adjusting font to new resolution"""
        settings.recalculate_font()
        self.restart()

    def generate_cells(self):
        """Populates play field with Cells that contain buttons and attributes.
        Store them all in a grid shape list to check neighboring mines later.
        And in a basic list for mine generation"""
        for x in range(settings.cell_width):
            column = []
            for y in range(settings.cell_height):
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
        self.all_mines = random.sample(self.not_mines, settings.mines)
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
            if 0 <= i < settings.cell_width and 0 <= j < settings.cell_height
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
    left_click = None
    # Right click is 'flag' or 'disabled'
    right_click = None

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
            font=(settings.cell_font, settings.font_size),
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


class Timer:
    """Keeps track of time elapsed.
    Starts with first move and stops if you win/lose
    """
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
        """Add 1 to the clock every second"""
        self.clock.configure(text=f"⏱{self.counter:04d}")
        self.counter += 1
        self.updating = self.clock.after(1000, self.update)

    def start(self):
        """Start the timer"""
        self.update()

    def stop(self):
        """Stop the timer"""
        self.clock.after_cancel(self.updating)


class FlaggedCounter:
    """Shows how many mines are still unflagged"""
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
        """Update label with new count, counting itself is handled by cell controls"""
        self.unflagged_count.configure(text=f'{self.counter:02d}🕸')


class Config:
    """Generates, stores and recalculates all of games settings"""
    def __init__(self):
        # ConfingParser stores settings in between games and lets the player change them.
        self.config = ConfigParser()
        # Check if confing file exist in the root directory of the game.
        if exists('config.ini'):
            self.config.read('config.ini')
        # Otherwise, populate parser with defaults
        else:
            self.create_default_config()

        # Read settings from parser. Fallback protects from deleted kay and values.
        # Does not protect form maliciously changing to incorrect values
        self.cell_width = self.config.getint(
            'difficulty', 'cell_width', fallback=9)
        self.cell_height = self.config.getint(
            'difficulty', 'cell_height', fallback=9)
        self.mines = self.config.getint(
            'difficulty', 'mines', fallback=10)
        self.cell_size = self.config.getint(
            'graphics', 'cell_size', fallback=50)
        self.font_modifier = self.config.getfloat(
            'graphics', 'font_modifier', fallback=0.5)
        self.resolution = self.calculate_resolution()
        self.font_size = int(self.cell_size * self.font_modifier)
        self.cell_font = self.config.get(
            'graphics', 'cell_font', fallback="Cooper Black")
        self.scoreboard_font = self.config.get(
            'graphics', 'scoreboard_font', fallback="Fixedsys")

    def calculate_resolution(self):
        """Adjust resolution to cell number and cell size
        :return str: String of two ints divided by an 'x'
        """
        return f"{self.cell_size*self.cell_width}x{self.cell_size*(self.cell_height+1)+20}"

    def recalculate_font(self):
        """Adjust font to better suit potentially resized window"""
        self.font_size = int(
            (Game.root.winfo_height()-20) / (self.cell_height+1) * self.font_modifier)

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
        self.font_size = int(self.cell_size * self.font_modifier)
        Game.root_settings_varied()
        active_game.restart()

    def custom_settings_popup(self, location):
        """Allows entry of custom game settings.
        Has restrictions on setting range and checks validity of user input.
        :param location: Root window
        """
        def submit_settings(event=None):
            """Submit custom settings entered by user, or highlight errors.
            :param event: Takes in and ignores event if submitted by hitting Enter key
            """
            # Check for validity of all entries
            valid_width = verify_entry(cell_width)
            valid_height = verify_entry(cell_height)
            valid_size = verify_entry(cell_size, 20, 200)

            # Only check mine count if we know width and height.
            # They are used in the calculation
            valid_mines = True
            if valid_width and valid_height:
                mine_max = cell_width.get() * cell_height.get() - 1
                valid_mines = verify_entry(mines, 1, mine_max)

            # Change settings and restart the game if valid
            if valid_width and valid_height and valid_size and valid_mines:
                top.destroy()
                self.cell_size = cell_size.get()
                self.change_difficulty(cell_width.get(), cell_height.get(), mines.get())

            # Highlight errors in entry to the user
            else:
                highlight_input_error(valid_width, cell_width_entry)
                highlight_input_error(valid_height, cell_height_entry)
                highlight_input_error(valid_mines, mines_entry)
                highlight_input_error(valid_size, cell_size_entry)

        def verify_entry(value, minimum=3, maximum=40):
            """Check int input validity
            :return bool: True if value is valid int in range
            :param tkinter.IntVar value: Entry value entered by user
            :param int minimum: Bottom of valid range
            :param int maximum: Top of valid range
            """
            # Check if input is an int
            try:
                x = value.get()
            except _tkinter.TclError:
                return False
            # Check if input is in range
            if minimum <= x <= maximum:
                return True
            else:
                return False

        def highlight_input_error(valid, entry):
            """Change entry background color based on entry validity.
            Red for invalid, White for valid
            :param bool valid: User entry validity
            :param tkinter.Entry entry: Entry widget to change
            """
            if valid:
                entry.configure(bg='white')
            else:
                entry.configure(bg='red')

        # Create new window that pops up above main game
        top = Toplevel(location, takefocus=True, bd=15, relief="ridge")
        top.title("Custom")
        top.iconbitmap('mine.ico')
        top.resizable(False, False)
        top.bind("<Escape>", lambda e: top.destroy())
        top.bind("<Return>", submit_settings)

        # Create variable to store settings
        cell_width = IntVar(top, self.cell_width)
        cell_height = IntVar(top, self.cell_height)
        mines = IntVar(top, self.mines)
        cell_size = IntVar(top, self.cell_size)

        # Create entries and labels for user input
        Label(top, text="Cell width (3 to 40):").grid(column=0, row=0)
        cell_width_entry = Entry(top, width=5, justify='right', textvariable=cell_width)
        cell_width_entry.grid(column=1, row=0)

        Label(top, text="Cell height (3 to 40):").grid(column=0, row=1)
        cell_height_entry = Entry(top, width=5, justify='right', textvariable=cell_height)
        cell_height_entry.grid(column=1, row=1)

        Label(top, text="Mine count \n(1 to (Number of cells-1)):").grid(column=0, row=2)
        mines_entry = Entry(top, width=5, justify='right', textvariable=mines)
        mines_entry.grid(column=1, row=2)

        Label(top, text="Cell size in px.:\n(Default=50) (20 to 200)").grid(column=0, row=3)
        cell_size_entry = Entry(top, width=5, justify='right', textvariable=cell_size)
        cell_size_entry.grid(column=1, row=3)

        Button(top, text='Submit', command=submit_settings).grid(column=1, row=4)

        # Prevent interaction with main window while settings window is open
        top.focus_force()
        top.grab_set()

    def create_default_config(self):
        """Fill in default values into ConfigParser"""
        self.config['difficulty'] = {
            'cell_width': 9,
            'cell_height': 9,
            'mines': 10,
        }
        self.config['graphics'] = {
            'cell_size': 50,
            'font_modifier': 0.5,
            'cell_font': "Cooper Black",
            'scoreboard_font': "Fixedsys",
        }

    def save_config(self):
        """Save current changeable settings to file"""
        # Update values in parser that could have changed with custom settings window
        self.config['difficulty'] = {
            'cell_width': self.cell_width,
            'cell_height': self.cell_height,
            'mines': self.mines,
        }
        self.config['graphics']['cell_size'] = str(self.cell_size)

        # Save settings to external file in root directory
        with open('config.ini', 'w') as f:
            self.config.write(f)


if __name__ == "__main__":
    # Prepare all the settings for the game
    settings = Config()
    # Modify main game window with prepared settings
    Game.root_settings_varied()
    Game.root_settings_basic()
    # Start the game.
    active_game = Game()
    # Mainloop must be outside active game, as otherwise it will be recreated during
    # restart and leak memory.
    Game.root.mainloop()
