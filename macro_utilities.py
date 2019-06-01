from dragonfly import (Key, Text, Pause)


def sleep_exit(sleep):
    return Key("escape") + Pause(str(sleep))


def replace_percentage(sleep):
    return sleep_exit(25) + Text("F%%s")
