import curses



logo = None
with open("gifbox.txt") as fp:
    logo = fp.readlines()



def draw_logo( stdscr ):
    
    k = None

    stdscr.clear()
    height, width = stdscr.getmaxyx()


    lh = len( logo )
    lw = len( logo[0] )

    cy = height/2
    cx = width/2


    oy = cy - lh/2
    ox = cx - lw/2

    for line in logo:
        stdscr.addstr(
            oy,  # y
            ox,  # x
            line
        )
        oy += 1


    caption = "Starting up..."
    stdscr.addstr(
        cy + (lh/2) - 2,
        cx + (lw/2) - len(caption) - 8,
        caption
    )


    # draw a border
    stdscr.border()

    # Refresh the screen
    stdscr.refresh()


    # Wait for next input
    k = stdscr.getch()



def main():
    curses.wrapper( draw_logo )

if __name__ == "__main__":
    main()