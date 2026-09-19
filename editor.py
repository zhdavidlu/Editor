#!/usr/bin/env python3

# 19 September
# Editor by Bear

import os
import select
import termios
from contextlib import contextmanager

ESC = '\x1b'       # ESCAPE
CSI = '\x1b\x5b'   # CONTROL SEQUENCE INTRODUCER
OSC = '\x1b\x5d'   # OPERATING SYSTEM COMMAND
STM = '\x1b\x5c'   # STRING TERMINATOR
DEC = '\x1b\x5b?'  # DEC CONTROL SEQUENCE

UP  = CSI, 'A'       # UP
DN  = CSI, 'B'       # DOWN
RT  = CSI, 'C'       # RIGHT
LT  = CSI, 'D'       # LEFT
NL  = CSI, 'E'       # NEXT LINE
PL  = CSI, 'F'       # PREVIOUS LINE
POS = CSI, 'H'       # SET      POSITION
ROW = CSI, 'd'       # ROW      ""
COL = CSI, 'G'       # COLUMN   ""
SAV = ESC,  7        # SAVE     ""
RST = ESC,  8        # RESTORE  ""
REP = CSI, 'n', 6    # REPORT   ""
EBF = CSI, 'J', 3    # ERASE BUFFER
EDA = CSI, 'J', 0    # ERASE DISPLAY AFTER
EDB = CSI, 'J', 1    # ""    ""      BEFORE
EDC = CSI, 'J', 2    # ""    ""      COMPLETE
ELA = CSI, 'K', 0    # ERASE LINE    AFTER
ELB = CSI, 'K', 1    # ""    ""      BEFORE
ELC = CSI, 'K', 2    # ""    ""      COMPLETE
ECA = CSI, 'X'       # ERASE CHAR    AFTER
ECS = CSI, 'P'       # ""    ""      SHIFT
SGR = CSI, 'm'       # SELECT GRAPHIC RENDITION [REC. 416]
CDD = OSC, STM, 10   # COLOUR DEFAULT DISPLAY
CDB = OSC, STM, 11   # ""     ""      BACKGROUND
CDH = OSC, STM, 17   # ""     ""      HIGHLIGHT
CD  = CSI, 'm', 38   #        COLOUR  DISPLAY
CB  = CSI, 'm', 48   #        ""      BACKGROUND
MCS = DEC, 'h', 25   # MODE   CURSOR  SHOW
MCH = DEC, 'l', 25   # ""     ""      HIDE
MBA = DEC, 'h', 1049 # ""     BUFFER  ALTERNATE
MBN = DEC, 'l', 1049 # ""     ""      NORMAL

RGB = 2
IDX = 5

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

IFLAG = 0  # INPUT   MODES
OFLAG = 1  # OUTPUT  ""
CFLAG = 2  # CONTROL ""
LFLAG = 3  # LOCAL   ""
CCHAR = 6  # CONTROL CHARACTERS

STDIN = 0
STDOUT = 1

DOCSIZE = [18, 60]

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

    r_vc, r_hc = CENTRECENTRE

    direction_to_centre_row = 2 * ((r_vc - r_v) >> 6) + 1
    direction_to_centre_column = 2 * ((r_hc - r_h) >> 6) + 1

    o_r, o_c = offset

    draw_procedure_start_row += direction_to_centre_row * o_r + 1
    draw_procedure_start_column += direction_to_centre_column * o_c + 1

    content = content or [" " * b_c] * b_r

    write(encode((POS, draw_procedure_start_row, draw_procedure_start_column)))
    write(encode((CB, *colour)))

    move_to_next_row = encode(NL, (COL, draw_procedure_start_column))

    for row in content:
        write(row)
        write(move_to_next_row)

def conform (size, colour, rrv=TOP, h=LEFT, /, *, margin=(0,0), message):

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

    content[0] = encode((CD, *colour)) + content[0]

    return content

def _ascii (character):

    if ord(character) != 0x1b:
        return character

    more_characters_in_queue = select.select([STDIN], [], [], 0.04)[0]

    if not more_characters_in_queue:
        return character

    next_character = os.read(STDIN, 1)
    characters = bytearray(character + next_character)

    match ord(next_character):
        case 0x5b: # CSI
            for i in range(64):
                characters += os.read(STDIN, 1)
                if 0x40 <= characters[-1] <= 0x7e:
                    return characters
        case 0x50|0x5d: # DCS / OSC
            for i in range(64):
                characters += os.read(STDIN, 1)
                if characters[-2:] == STM.encode("ascii"):
                    return characters
        case intermediate if 0x20 <= intermediate <= 0x2f:
            for i in range(8):
                characters += os.read(STDIN, 1)
                if 0x30 <= characters[-1] <= 0x7e:
                    return characters
        case final if 0x30 <= final <= 0x7e:
            return characters
        case n if n < 0x20 or n == 0x7f:
            raise ValueError

def _unicode (character):

    characters = bytearray(character)

    match ord(character):
        case c2 if 0b110_00010 <= c2 <= 0b110_11111:
            characters += os.read(STDIN, 1)
        case c3 if 0b1110_0000 <= c3 <= 0b1110_1111:
            for i in range(2):
                characters += os.read(STDIN, 1)
        case c4 if 0b11110_000 <= c4 <= 0b11110_100:
            for i in range(3):
                characters += os.read(STDIN, 1)
        case n if n < 0b110_0010 or n > 0b11110_100:
            raise ValueError

    return characters

def read ():
    character = os.read(STDIN, 1)
    if 0x00 <= ord(character) <= 0x7f: return _ascii(character)
    if 0x80 <= ord(character) <= 0xff: return _unicode(character)

def write (message):
    match message:
        case str(sm): n = os.write(STDOUT, sm.encode())
        case bytes()|bytearray()|memoryview() as bm: n = os.write(STDOUT, bm)
        case _: raise TypeError
    return n

@contextmanager
def begin_program ():

    fd = STDIN
    device = termios.tcgetattr(fd)
    save = termios.tcgetattr(fd)

    device[IFLAG] &= ~(termios.IGNCR|termios.ICRNL|termios.INLCR|termios.IXON)
    device[OFLAG] &= ~(termios.OCRNL|termios.ONLCR)
    device[LFLAG] &= ~(termios.ECHO|termios.ICANON|termios.IEXTEN)

    device[CCHAR][termios.VMIN] = 1
    device[CCHAR][termios.VTIME] = 0

    try:

        termios.tcsetattr(fd, termios.TCSAFLUSH, device)

        b = "rgb:13/15/18"
        d = "rgb:75/a4/ae"

        write(encode((CDB, "?"), (CDD, "?")))

        ob = read()
        od = read()

        write(encode(MBA))
        write(encode((POS, 1, 1), (CDB, b), (CDD, d)))

        yield

    finally:

        termios.tcsetattr(fd, termios.TCSAFLUSH, save)

        write(ob + od)
        write(encode(MBN))

if __name__ == "__main__":
    with begin_program():
        for _ in range(20):
            write(read())
