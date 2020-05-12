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
            '-e', '  get {name, URL} of tabs of window 1',
            '-e', 'end tell'
        ], capture_output=True).stdout.decode('utf-8').strip()
    )
    details = re.sub('},\s{', '],[', re.sub('}}$', ']]', re.sub('^{{', '[[', details)))
    details_json = json.loads(details)
    for i in range(len(details_json[0])):
        tabs.append({'name': details_json[0][i], 'url': details_json[1][i]})

def paint_urls(s, tabs, first):
    x = s.getmaxyx()[1]
    count = len(tabs)
    show = SHOW_MAX if count - first >= SHOW_MAX else count - first
    s.addstr(
        0, 0,
        f"Choose a tab "
        f"[{first + 1}-{first + show} of {count}]:".ljust(x),
        curses.A_STANDOUT
    )
    label_length = 35
    url_length = x - label_length - 4
    for clear_row in range(SHOW_MAX):
        s.hline(clear_row + 2, 0, ' ', x)
    for row in range(show):
        label = tabs[first + row]['name']
        label = label[:label_length].ljust(label_length)
        url = tabs[first + row]['url']
        url = re.sub('^https?://(www\.)?', '', url)
        url = url[:url_length].ljust(url_length)
        s.addstr(row + 2, 0, f"{row}. {label} {url}")
    last = f"-{show - 1}" if show - 1 >= 1 else ""
    s.hline(13, 0, ' ', x)
    s.addstr(
        13, 0, f"[0{last}: Open] "
               f"[<: Prev] "
               f"[>: Next] "
               f"[/: Search] "
               f"[q: Quit]".ljust(x),
        curses.A_STANDOUT
    )
    s.refresh()
    return count

def open_url(url):
    subprocess.run(['open', url])

def main(s):
    if args.browse or True:
        load_tabs()
        first = 0
        s.clear()
        while True:
            count = paint_urls(s, tabs, first)
            key = s.getkey(14, 0)
            if key == '<':
                first -= SHOW_MAX
                first = 0 if first < 0 else first
            elif key == '>':
                first = first + SHOW_MAX if first + SHOW_MAX <= count else first
            elif key == 'q':
                break
            elif key == '/':
                old_count = count
                old_first = first
                s.addstr('Search [space to exit]:', curses.A_STANDOUT)
                s.addstr(' ')
                searching = True
                term = ''
                pos = s.getyx()
                while searching:
                    key = s.getkey()
                    if key == 'KEY_BACKSPACE' and len(term) > 0:
                        term = term[0:len(term)-1]
                        s.addstr(pos[0], pos[1] + len(term), ' ')
                        s.move(pos[0], pos[1] + len(term))
                    elif key == ' ':
                        searching = False
                    elif re.match('KEY_', key):
                        pass
                    elif re.match('[a-z0-9/=-_#\.\?]', key):
                        term += key
                        s.addstr(pos[0], pos[1] + len(term) - 1, key)
                    if len(term) > 0:
                        term = term.lower()
                        search_tabs = []
                        for tab in tabs:
                            if tab['name'].lower().find(term) > -1 or re.sub('^https?://(www\.)?', '', tab['url']).lower().find(term) > -1:
                                search_tabs.append(tab)
                        count = paint_urls(s, search_tabs, 0)
                s.hline(14, 0, ' ', s.getmaxyx()[1])
                count = old_count
                first = old_first
            elif re.match('[0-9]', key):
                open_url(tabs[first + int(key)]['url'])

parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", "--browse",
    action="store_true", help="browse tabs to open"
)
args = parser.parse_args()
curses.wrapper(main)