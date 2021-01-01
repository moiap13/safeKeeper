#!/usr/bin/env python3

import curses


def history_input():
    # get the curses screen window
    screen = curses.initscr()

# turn off input echoing
    curses.noecho()

    # respond to keys immediately (don't wait for enter)
    curses.cbreak()

    # map arrow keys to special values
    screen.keypad(True)
    try:
        command = [""]
        index = 0
        while True:
            char = screen.getch()
            if char == ord('q'):
                break
            elif char == curses.KEY_RIGHT:
                pass
                # print doesn't work with curses, use addstr instead
                #screen.addstr(0, 0, 'right')
                #print("right", end="\r")
            elif char == curses.KEY_LEFT:
                pass
                #print("left ", end="\r")
#               screen.addstr(0, 0, 'left ')
            elif char == curses.KEY_UP:
                index -= 1 if index > 0 else 0
                print(command[index], end="\r")

    #            screen.addstr(0, 0, 'up   ')
            elif char == curses.KEY_DOWN:
                index += 1 if index < len(command)-1 else len(command)-1
                print(command[index], end="\r")
    #            screen.addstr(0, 0, 'down ')
            elif char == curses.KEY_ENTER or char == 10 or char == 13: #if enter is pressed
                return command[index]
                index += 1
                command.append("")
            else:
                command[index] += chr(char)
                print(command[index], end="\r")
    finally:
        # shut down cleanly
        curses.nocbreak();
        screen.keypad(0);
        curses.echo()
        curses.endwin()
