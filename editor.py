#!/usr/bin/env python3

# 4 August
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
SAP = CSI, '?25h'   # SHOW ACTIVE POSITION
HAP = CSI, '?25l'   # HIDE ""     ""
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

# ----- #

def draw_box (size, colour, rrp=TOPLEFT, /, *, offset=(0,0), content=None):

    document_size = DOCSIZE
    box_size = size
    relative_reference_points = rrp

    d_r, d_c = document_size
    b_r, b_c = box_size
    r_v, r_h = relative_reference_points

    draw_procedure_start_row = d_r * r_v // 100 - b_r * r_v // 100
    draw_procedure_start_column = d_c * r_h // 100 - b_c * r_h // 100

    r_vc, r_hc = CENTRECENTRE

    direction_to_centre_row = 2 * ((r_vc - r_v) >> 6) + 1
    direction_to_centre_column = 2 * ((r_hc - r_h) >> 6) + 1

    o_r, o_c = offset

    draw_procedure_start_row += direction_to_centre_row * o_r + 1
    draw_procedure_start_column += direction_to_centre_column * o_c + 1

    content = content or [" " * b_c] * b_r

    write(encode((SET, draw_procedure_start_row, draw_procedure_start_column)))
    write(encode((SGR, 48, 5, colour)))

    move_to_next_row = encode(NL, (COL, draw_procedure_start_column))

    for row in content:
        write(row)
        write(move_to_next_row)

def bx_compose (size, colour, rrv=TOP, h=LEFT, /, *, margin=(0,0), message):

    box_size = size
    box_margins = margin

    b_r, b_c = box_size
    m_r, m_c = box_margins

    inner_region_size = b_r - 2 * m_r, b_c - 2 * m_c

    norm_message = [message] if isinstance(message, str) else message
    message_region_rows = len(norm_message)

    ir_r, ir_c = inner_region_size
    mr_r, mr_c = message_region_rows, ir_c

    message_start_row = ir_r * rrv // 100 - mr_r * rrv // 100
    message_start_row += m_r

    content = [" " * b_c] * b_r

    align = {0: "<", 50: "^", 100: ">"}[h]

    for i in range(mr_r):
        row_message = f"{'':{m_c}}{norm_message[i]:{align}{mr_c}}{'':{m_c}}"
        content[message_start_row + i] = row_message

    content[0] = encode((SGR, 38, 5, colour)) + content[0]

    return content

# ----- #

clear_display = encode((SGR, 39, 49), (SET, 1, 1), EDA, EBF)
write(clear_display)

fd = sys.stdin.fileno()
terminal_attributes = termios.tcgetattr(fd)

try:
    tty.setcbreak(fd, termios.TCSAFLUSH)

    # TEST PATTERN FOR DRAW_BOX() AND BX_COMPOSE()

    draw_box((18, 60), 255)

    w  = ("AB", "012345")
    m  = (1, 2)
    c1 = bx_compose((5, 17), 251, TOP,    LEFT,   margin = m, message = w)
    c2 = bx_compose((5, 18), 251, TOP,    CENTRE, margin = m, message = w)
    c3 = bx_compose((5, 17), 251, TOP,    RIGHT,  margin = m, message = w)
    c4 = bx_compose((4, 17), 253, CENTRE, LEFT,   margin = m, message = w)
    c5 = bx_compose((4, 18), 253, CENTRE, CENTRE, margin = m, message = w)
    c6 = bx_compose((4, 17), 253, CENTRE, RIGHT,  margin = m, message = w)
    c7 = bx_compose((5, 17), 255, BOTTOM, LEFT,   margin = m, message = w)
    c8 = bx_compose((5, 18), 255, BOTTOM, CENTRE, margin = m, message = w)
    c9 = bx_compose((5, 17), 255, BOTTOM, RIGHT,  margin = m, message = w)

    draw_box((5, 17), 235, TOPLEFT,      offset = (1, 2), content = c1)
    draw_box((5, 18), 236, TOPCENTRE,    offset = (1, 0), content = c2)
    draw_box((5, 17), 237, TOPRIGHT,     offset = (1, 2), content = c3)
    draw_box((4, 17), 238, CENTRELEFT,   offset = (0, 2), content = c4)
    draw_box((4, 18), 239, CENTRECENTRE, offset = (0, 0), content = c5)
    draw_box((4, 17), 240, CENTRERIGHT,  offset = (0, 2), content = c6)
    draw_box((5, 17), 241, BOTTOMLEFT,   offset = (1, 2), content = c7)
    draw_box((5, 18), 242, BOTTOMCENTRE, offset = (1, 0), content = c8)
    draw_box((5, 17), 243, BOTTOMRIGHT,  offset = (1, 2), content = c9)

    sys.stdout.write(encode((SET, 1, 1), (SGR, 39, 49), HAP))
    sys.stdout.flush()
    sys.stdin.read(1)

finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, terminal_attributes)
    write(encode((SET, DOCSIZE[0], 1), NL, SAP))
