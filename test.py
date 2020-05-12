#!/usr/bin/env python3

import argparse
import curses

COUNT = 100
SHOW_MAX = 10

command = None

def main(s):
    global command
    command = args.command
    first = 0
    while True:
        s.clear()
        show = SHOW_MAX if COUNT - first >= SHOW_MAX else COUNT - first + 1
        s.addstr(0, 0, f"Choose a tab "
                       f"[{first}-{first + show - 1} of {COUNT}]:", curses.A_STANDOUT)
        for row in range(show):
            s.addstr(row + 2, 0, f"{row}. {command}")
        last = f"-{show - 1}" if show - 1 >= 1 else ""
        s.addstr(13, 0, f"[0{last}] to open, [<] or [>] to page, [q] to quit:")
        s.refresh()
        key = s.getkey(14, 0)
        if key == '<':
            first -= SHOW_MAX
            first = 0 if first < 0 else first
        elif key == '>':
            first = first + SHOW_MAX if first + SHOW_MAX <= COUNT else first
        elif key == 'q':
            break

parser = argparse.ArgumentParser()
parser.add_argument("command")
args = parser.parse_args()

curses.wrapper(main)