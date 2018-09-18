import curses

def main(stdscr):
    # Clear screen
    stdscr.clear()

    stdscr.addstr(0, 0, "a test")

    stdscr.refresh()
    stdscr.getkey()

curses.filter()
curses.wrapper(main)