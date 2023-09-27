"""See how much time each function takes by running the game through this file
Just execute this file as if it was main.py.
"""
import cProfile
import main

def test():
    pr = cProfile.Profile()
    pr.enable()
    main.main()
    pr.disable()
    pr.print_stats(sort='time')

if __name__ == "__main__":
    test()
