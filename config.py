from tkinter import Toplevel, IntVar, Label, Entry, Button, Tk
from configparser import ConfigParser
from os.path import exists
from typing import TYPE_CHECKING
import _tkinter
if TYPE_CHECKING:
    from main import Game


class Config:
    """Generates, stores and recalculates all of games settings"""
    min_cell_count = 3
    max_cell_count = 40
    min_cell_size = 20
    max_cell_size = 200



    def __init__(self, game: "Game"):
        self.active_game = game
        # ConfigParser stores settings in between games and lets the player change them.
        self.config = ConfigParser()
        # Check if config file exist in the root directory of the game.
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

    def calculate_resolution(self) -> str:
        """Adjust resolution to cell number and cell size
        :return str: String of two ints divided by an 'x'
        """
        return f"{self.cell_size*self.cell_width}x{self.cell_size*(self.cell_height+1)+20}"

    def recalculate_font(self):
        """Adjust font to better suit potentially resized window"""
        self.font_size = int(
            (self.active_game.root.winfo_height()-20) / (self.cell_height+1) * self.font_modifier)

    def unrevealed_cell_count(self) -> int:
        """How many cells need to be revealed to win the game"""
        return self.cell_width * self.cell_height - self.mines

    def change_difficulty(self, x: int, y: int , m: int):
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
        self.active_game.root_settings_varied()
        self.active_game.restart()

    def custom_settings_popup(self, location: Tk):
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
            valid_size = verify_entry(cell_size, self.min_cell_size, self.max_cell_size)

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

        def verify_entry(value: IntVar,
                         minimum: int = self.min_cell_count,
                         maximum: int = self.max_cell_count
                         ) -> bool:
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
            return minimum <= x <= maximum

        def highlight_input_error(valid: bool, entry: Entry):
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
        Label(top, 
              text=f"Cell width ({self.min_cell_count} to {self.max_cell_count}):"
              ).grid(column=0, row=0)
        cell_width_entry = Entry(top, width=5, justify='right', textvariable=cell_width)
        cell_width_entry.grid(column=1, row=0)

        Label(top, 
              text=f"Cell height ({self.min_cell_count} to {self.max_cell_count}):"
              ).grid(column=0, row=1)
        cell_height_entry = Entry(top, width=5, justify='right', textvariable=cell_height)
        cell_height_entry.grid(column=1, row=1)

        Label(top, text="Mine count \n(1 to (Number of cells-1)):").grid(column=0, row=2)
        mines_entry = Entry(top, width=5, justify='right', textvariable=mines)
        mines_entry.grid(column=1, row=2)

        Label(top,
              text=f"Cell size in px.:\n(Default=50) ({self.min_cell_size} to {self.max_cell_size})"
              ).grid(column=0, row=3)
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
