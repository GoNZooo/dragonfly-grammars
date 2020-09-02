from dragonfly import (Key, Text)


def sleep_exit(sleep):
    return Key("escape/%d" % sleep)


def replace_percentage(sleep):
    return sleep_exit(sleep) + Text("F%%s")


def replace_in_text(text, character="$", sleep=15):
    return Text(text) + sleep_exit(sleep) + Text("F%ss" % character)
