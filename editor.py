#!/usr/bin/env python3

# 19 June
# Editor by Bear

import sys
import tty, termios

ESC = '\x1b'
CSI = '\x1b\x5b'
STM = '\x1b\x5c'
OSC = '\x1b\x5d'

UP  = CSI, 'A'      # UP
DN  = CSI, 'B'      # DOWN
RT  = CSI, 'C'      # RIGHT
LT  = CSI, 'D'      # LEFT
NL  = CSI, 'E'      # NEXT LINE
PL  = CSI, 'F'      # PREVIOUS LINE
ROW = CSI, 'd'      # ROW     POSITION
COL = CSI, 'G'      # COLUMN  ""
SET = CSI, 'H'      # SET     ""
SAV = ESC,  7       # SAVE    ""
RST = ESC,  8       # RESTORE ""
REP = CSI, 'n', 6   # REPORT  ""
EDA = CSI, 'J', 0   # ERASE DISPLAY AFTER
EDB = CSI, 'J', 1   # ""    ""      BEFORE
EDC = CSI, 'J', 2   # ""    ""      COMPLETE
EBF = CSI, 'J', 3   # ERASE BUFFER
ELA = CSI, 'K', 0   # ERASE LINE    AFTER
ELB = CSI, 'K', 1   # ""    ""      BEFORE
ELC = CSI, 'K', 2   # ""    ""      COMPLETE
ECA = CSI, 'X'      # ERASE CHAR    AFTER
DCA = CSI, 'P'      # DEL   ""      ""
SCP = CSI, '?25h'   # SHOW CURSOR POSITION
HCP = CSI, '?25l'   # HIDE ""     ""
SGR = CSI, 'm'      # SELECT GRAPHIC RENDITION [REC. 416]
FC  = OSC, STM, 10  # FOREGROUND COLOUR
BC  = OSC, STM, 11  # BACKGROUND ""
HC  = OSC, STM, 17  # HIGHLIGHT  ""

TOP = LEFT = 0
CENTRE = 50
BOTTOM = RIGHT = 100

TOPLEFT      = TOP, LEFT
TOPCENTRE    = TOP, CENTRE
TOPRIGHT     = TOP, RIGHT
CENTRELEFT   = CENTRE, LEFT
CENTRECENTRE = CENTRE, CENTRE
CENTRERIGHT  = CENTRE, RIGHT
BOTTOMLEFT   = BOTTOM, LEFT
BOTTOMCENTRE = BOTTOM, CENTRE
BOTTOMRIGHT  = BOTTOM, RIGHT

DOCSIZE = (18, 60)
write = sys.stdout.write

def _encode_cmd (identity, modifier=()):
    start, end, *between = *identity, *modifier
    return start + ";".join(map(str, between)) + str(end)

def encode (*commands):
    code = ""
    for cmd in commands:
        match cmd:
            case [*ident], *modifier: code += _encode_cmd(ident, modifier)
            case [*identity]: code += _encode_cmd(identity)
            case str(other): code += other
            case _: raise ValueError
    return code

def draw_box (size, colour, rrp=TOPLEFT, /, *, offset=(0,0), content=None):

    document_size = DOCSIZE
    box_size = size
    relative_reference_points = rrp

    d_r, d_c = document_size
    b_r, b_c = box_size
    r_v, r_h = relative_reference_points

    draw_procedure_start_row = d_r * r_v // 100 - b_r * r_v // 100
    draw_procedure_start_column = d_c * r_h // 100 - b_c * r_h // 100

    # print(d_r, d_c)
    # print(b_r, b_c)
    # print(r_v, r_h)

    # print(f"{draw_procedure_start_row=}")
    # print(f"{draw_procedure_start_column=}")

    r_vc, r_hc = CENTRECENTRE

    direction_to_centre_row = 2 * ((r_vc - r_v) >> 6) + 1
    direction_to_centre_column = 2 * ((r_hc - r_h) >> 6) + 1

    # print(f"{direction_to_centre_row=}")
    # print(f"{direction_to_centre_column=}")

    o_r, o_c = offset

    draw_procedure_start_row += direction_to_centre_row * o_r + 1
    draw_procedure_start_column += direction_to_centre_column * o_c + 1

    # print(f"{draw_procedure_start_row=}")
    # print(f"{draw_procedure_start_column=}")

    content = content or [" " * b_c] * b_r

    write(encode((SET, draw_procedure_start_row, draw_procedure_start_column)))
    write(encode((SGR, 48, 5, colour)))

    move_to_next_row = encode(NL, (COL, draw_procedure_start_column))

    for row in content:
        write(row)
        write(move_to_next_row)

def compose_box_content (size, colour, rrp=TOPLEFT, /, *, margin=(0,0), words):
    ...


terminal_attributes = termios.tcgetattr(sys.stdin.fileno())

clear_display = encode((SGR, 39, 49), (SET, 1, 1), EDA, EBF)
write(clear_display)

try:
    tty.setcbreak(sys.stdin.fileno(), termios.TCSAFLUSH)

    # TEST PATTERN FOR DRAW_BOX() AND COMPOSE_BOX_CONTENT()

    draw_box((18, 60), 255)

    draw_box((5, 17), 240, TOPLEFT,      offset = (1, 2))
    draw_box((5, 18), 241, TOPCENTRE,    offset = (1, 0))
    draw_box((5, 17), 242, TOPRIGHT,     offset = (1, 2))
    draw_box((4, 17), 243, CENTRELEFT,   offset = (0, 2))
    draw_box((4, 18), 244, CENTRECENTRE, offset = (0, 0))
    draw_box((4, 17), 245, CENTRERIGHT,  offset = (0, 2))
    draw_box((5, 17), 246, BOTTOMLEFT,   offset = (1, 2))
    draw_box((5, 18), 247, BOTTOMCENTRE, offset = (1, 0))
    draw_box((5, 17), 248, BOTTOMRIGHT,  offset = (1, 2))

    sys.stdout.write(encode((SGR, 39, 49), (SET, 2, 3), HCP))
    sys.stdout.flush()
    sys.stdin.read(1)

finally:
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, terminal_attributes)
    write(encode((SET, DOCSIZE[0], 1), SCP))
