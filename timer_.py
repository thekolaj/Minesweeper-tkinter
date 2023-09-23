from tkinter import Label, Frame

class Timer:
    """Keeps track of time elapsed.
    Starts with first move and stops if you win/lose
    """
    def __init__(self, location: Frame, font: tuple[str, int]):
        self.counter = 0
        self.updating = None
        self.clock = Label(
            location,
            text='⏱0000',
            font=font,
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