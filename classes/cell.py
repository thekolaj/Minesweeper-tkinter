import random
from tkinter import Button, Frame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Game


class Cell:
    """A cell that contains a button and some attributes"""
    # Cell control. Change cell behavior without rebinding every individual cell.
    # Left click goes from 'first_move' > 'regular_move' > 'disabled'
    left_click: callable = None
    # Right click is 'flag' or 'disabled'
    right_click: callable = None
    # Some methods depend on main game existing.
    active_game: "Game"

    def __init__(self, location: Frame, coordinates: tuple[int, int]):
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
            font=(self.active_game.settings.cell_font,
                  self.active_game.settings.font_size),
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
            replacement_mine = random.choice(self.active_game.not_mines)
            replacement_mine.is_mine = True

            # Update corresponding lists
            self.active_game.all_mines.remove(self)
            self.active_game.not_mines.append(self)
            self.active_game.not_mines.remove(replacement_mine)
            self.active_game.all_mines.append(replacement_mine)

        # Fill in value for all none mine cells. Done after all mine placement is finalized
        self.active_game.cell_value()

        Cell.left_click = Cell.regular_move
        self.active_game.timer.start()
        self.reveal()

        # Update counter for an edge case where player flagged some random squares
        # at the start of the game and then hit a 0 to reveal some of those flagged cells
        self.active_game.flagged_counter.update()

    def regular_move(self):
        """Checks if you lost the game by hitting a mine. Otherwise, reveals cell"""
        if self.is_mine:
            self.button.configure(
                bg="#f20000",
                disabledforeground="gray",
                relief="sunken"
            )
            self.active_game.loss()
        else:
            self.reveal()
            # Update counter in case of hitting 0 to reveal some of falsely flagged cells
            self.active_game.flagged_counter.update()

    def reveal(self):
        """Show value of a cell that is not a mine
        Calls itself recursively if you hit a 0 (black space)
        """
        # Check for falsely flagged mines, used during recursion call when you hit 0
        if self.flagged:
            self.button.configure(text="")
            self.flagged = False
            self.active_game.flagged_counter.counter += 1

        # Change buttons to represent revealed cell
        self.button.configure(state="disabled", relief="sunken")
        self.revealed = True
        # If you hit a 0 (black space), reveals cells next to self
        if self.value == 0:
            for neighbor in self.active_game.find_neighbors(self):
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
        self.active_game.unrevealed_cell_count -= 1
        if self.active_game.unrevealed_cell_count == 0:
            self.active_game.victory()

    def flag(self):
        """Set or remove flag that indicates a potential mine"""
        if self.flagged:
            self.button.configure(
                text="", disabledforeground="black", state='normal'
            )
            self.flagged = False
            # Delete instance attribute that is disabling cell, reactivating it.
            del self.left_click
            self.active_game.flagged_counter.counter += 1
        else:
            self.button.configure(
                text="🏴", disabledforeground="#ab0000", state="disabled"
            )
            self.flagged = True
            # Disable control in instance attribute. All other cells still use
            # class attribute and thus remain active
            self.left_click = self.disabled
            self.active_game.flagged_counter.counter -= 1
        self.active_game.flagged_counter.update()

    @staticmethod
    def disabled(*args):
        """Do nothing. Used to disable controls on buttons as needed"""
        pass
