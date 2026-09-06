
# 5 September
# rwd: Read-Write Direct &
#      assorted other functions (bad)

import os

STDIN = 0
STDOUT = 1

def i (max):
    return os.read(STDIN, max).decode()

def o (message):
    return os.write(STDOUT, message.encode())
