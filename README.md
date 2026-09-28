# Mnemonics

```python3
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
```
```python3
def _encode_cmd (identity, modifier=()):
    start, end, *between = *identity, *modifier
    return start + ";".join(map(str, between)) + str(end)

def encode (*commands):
    code = ""
    for cmd in commands:
        match cmd:
            case [*ident], *modifier: code += _encode_cmd(ident, modifier)
            case [*identity]: code += _encode_cmd(identity)
            case _: raise ValueError
    return code.encode("ascii")

>>> encode((RT, 42))
b"\x1b[42C"
```
