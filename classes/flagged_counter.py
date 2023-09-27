from tkinter import Label, Frame

class FlaggedCounter:
    """Shows how many mines are left unflagged"""

    def __init__(self, location: Frame, mines: int, font: tuple[str, int]):
        self.counter = mines
        self.unflagged_count = Label(
            location,
            text=f'{self.counter:02d}🕸',
            font=font,
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
