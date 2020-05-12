#!/usr/bin/env python3

import argparse
import curses
import json
import re
import subprocess

SHOW_MAX = 10

tabs = []

def load_tabs():
    global tabs
    count = int(
        subprocess.run([
            'osascript',
            '-e', 'tell app "Safari"',
            '-e', '  get count of tabs of window 1',
            '-e', 'end tell'
        ], capture_output=True).stdout.decode('utf-8').strip()
    )
    details = str(
        subprocess.run([
            'osascript', '-s', 's',
            '-e', 'tell app "Safari"',
            '-e', 'get {name, URL} of tabs of window 1',
            '-e', 'end tell'
        ], capture_output=True).stdout.decode('utf-8').strip()
    )
    details = re.sub('},\s{', '],[', re.sub('}}$', ']]', re.sub('^{{', '[[', details)))
    details_json = json.loads(details)
    for i in range(len(details_json[0])):
        tabs.append({'name': details_json[0][i], 'url': details_json[1][i]})

def main(s):
    if args.browse or True:
        load_tabs()
        first = 0
        while True:
            s.clear()
            count = len(tabs)
            show = SHOW_MAX if count - first >= SHOW_MAX else count - first
            s.addstr(
                0, 0,
                f"Choose a tab "
                f"[{first + 1}-{first + show} of {count}]:",
                curses.A_STANDOUT
            )
            for row in range(show):
                label = tabs[first + row]['name'][:45].ljust(45)
                url = re.sub('^https?://(www\.)?', '', tabs[first + row]['url'])[:35]
                s.addstr(row + 2, 0, f"{row}. {label} ({url})")
            last = f"-{show - 1}" if show - 1 >= 1 else ""
            s.addstr(13, 0, f"[0{last}] to open, [<] or [>] to page, [q] to quit:")
            s.refresh()
            key = s.getkey(14, 0)
            if key == '<':
                first -= SHOW_MAX
                first = 0 if first < 0 else first
            elif key == '>':
                first = first + SHOW_MAX if first + SHOW_MAX <= count else first
            elif key == 'q':
                break
            else:
                try:
                    index = int(key)
                    subprocess.run(['open', tabs[first + index]['url']])
                except:
                    pass

parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", "--browse",
    action="store_true", help="browse tabs to open"
)
args = parser.parse_args()

curses.wrapper(main)