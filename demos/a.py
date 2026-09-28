#!/usr/bin/env python3

# 28 June [E. 5 September]
# Demo A - draw_box() & conform()

from editor import *

write(encode((POS, 1, 1), (SGR, 39, 49), EDA, EBF))
draw_box(DOCSIZE, (RGB, 247, 245, 242))

r  = (1, 2)
m  = ("AB", "012345")

c1 = conform((5, 17), (IDX, 251), TOP,    LEFT,   margin = r, message = m)
c2 = conform((5, 18), (IDX, 251), TOP,    CENTRE, margin = r, message = m)
c3 = conform((5, 17), (IDX, 251), TOP,    RIGHT,  margin = r, message = m)
c4 = conform((4, 17), (IDX, 253), CENTRE, LEFT,   margin = r, message = m)
c5 = conform((4, 18), (IDX, 253), CENTRE, CENTRE, margin = r, message = m)
c6 = conform((4, 17), (IDX, 253), CENTRE, RIGHT,  margin = r, message = m)
c7 = conform((5, 17), (IDX, 255), BOTTOM, LEFT,   margin = r, message = m)
c8 = conform((5, 18), (IDX, 255), BOTTOM, CENTRE, margin = r, message = m)
c9 = conform((5, 17), (IDX, 255), BOTTOM, RIGHT,  margin = r, message = m)

draw_box((5, 17), (IDX, 235), TOPLEFT,      offset = (1, 2), content = c1)
draw_box((5, 18), (IDX, 236), TOPCENTRE,    offset = (1, 0), content = c2)
draw_box((5, 17), (IDX, 237), TOPRIGHT,     offset = (1, 2), content = c3)
draw_box((4, 17), (IDX, 238), CENTRELEFT,   offset = (0, 2), content = c4)
draw_box((4, 18), (IDX, 239), CENTRECENTRE, offset = (0, 0), content = c5)
draw_box((4, 17), (IDX, 240), CENTRERIGHT,  offset = (0, 2), content = c6)
draw_box((5, 17), (IDX, 241), BOTTOMLEFT,   offset = (1, 2), content = c7)
draw_box((5, 18), (IDX, 242), BOTTOMCENTRE, offset = (1, 0), content = c8)
draw_box((5, 17), (IDX, 243), BOTTOMRIGHT,  offset = (1, 2), content = c9)

write(encode((POS, DOCSIZE[0], 1), NL, (SGR, 39, 49)))
