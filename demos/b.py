#!/usr/bin/env python3

# 4 October
# Demo B - read() & write()

from editor import *

character = read()
write(character.hex("-"))

while True:
    more_characters_in_queue = select.select([STDIN], [], [], 0.04)[0]
    if not more_characters_in_queue:
        break
    write(f' {read().hex("-")}')
write("\n")
