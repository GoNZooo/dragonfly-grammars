from dragonfly import (Key, Text)


def sleep_exit(sleep):
    return Key("escape/%d" % sleep)


def replace_percentage(sleep):
    return sleep_exit(sleep) + Text("F%%s")
