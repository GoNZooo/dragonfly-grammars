from dragonfly import (Key, Text, Choice)


def sleep_exit(sleep):
    return Key("escape/%d" % sleep)


def replace_percentage(sleep):
    return sleep_exit(sleep) + Text("F%%s")


def replace_in_text(text, character="$", sleep=15):
    return Text(text) + sleep_exit(sleep) + Text("F%ss" % character)


comment_choice_map = {
    "to do": "@TODO:",
    "worn": "@WARN:",
    "research": "@RESEARCH:",
    "note": "@NOTE:",
}


def comment_choice(name="comment_type"):
    return Choice(name, comment_choice_map)
