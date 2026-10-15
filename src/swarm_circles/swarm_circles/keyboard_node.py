#!/usr/bin/env python3
import select
import sys
import termios
import tty

import rclpy
from std_msgs.msg import String

HELP = """
Swarm keyboard control
  w / s : cambiar radio  subir / bajar
  d / a : velocidad   subir / bajar
  f     : cambiar dirección
  c     : clear
  r     : default
  n     : siguiente forma
  q     : salir
"""

KEYMAP = {
    "w": "radius+",
    "s": "radius-",
    "d": "speed+",
    "a": "speed-",
    "f": "flip",
    "n": "shape+",
    "c": "clear",
    "r": "reset",
}


def main():
    rclpy.init()
    node = rclpy.create_node("swarm_keyboard")
    pub = node.create_publisher(String, "/swarm/command", 10)
    print(HELP)

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while rclpy.ok():
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1).lower()
                if key == "q" or key == "\x03":
                    break
                if key in KEYMAP:
                    pub.publish(String(data=KEYMAP[key]))
            rclpy.spin_once(node, timeout_sec=0.0)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
