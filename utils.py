import tty
import sys
import termios

class Getch:
    def __init__(self):
        pass

    def __call__(self):
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old_settings)
        return ch

getch = Getch()
