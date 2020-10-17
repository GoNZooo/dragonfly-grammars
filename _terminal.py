from dragonfly import (Grammar, CompoundRule, Text, MappingRule, Dictation, Function, Choice)
from dragonfly.windows.clipboard import (Clipboard)
from vim.rules.letter import (barbecue, formatting_choice, format_dictation)


class TerminalEnabler(CompoundRule):
    spec = "enable Terminal"

    def _process_recognition(self, node, extras):
        terminal_bootstrap.disable()
        terminal_grammar.enable()
        print "Terminal grammar enabled!"


class TerminalDisabler(CompoundRule):
    spec = "disable Terminal"

    def _process_recognition(self, node, extras):
        terminal_grammar.disable()
        terminal_bootstrap.enable()
        print "Terminal grammar disabled"


git_command_choice_map = {
    "pull from master": "pull origin master",
    "pull from main": "pull origin main",
    "check out": "checkout ",
    "new branch": "checkout -b ",
    "status": "status",
    "stash": "stash",
    "log": "log",
    "in it": "init",
    "initialize": "init",
}


def git_command_choice(name="git_command"):
    return Choice(name, git_command_choice_map)


def output_git_command(git_command=None):
    command_text = "git "
    if git_command is None:
        command = Text(command_text)
    else:
        command = Text(command_text + str(git_command))
    command.execute()


def output_git_pull(branch_name):
    branch_name = format_branch_name(branch_name)
    Text("git pull %s" % branch_name).execute()


def format_branch_name(branch_name):
    return barbecue(str(branch_name))


def output_git_push(branch_name, set_up_stream=False):
    upstream_text = " -u origin" if set_up_stream else ""
    branch_name = format_branch_name(branch_name)
    Text("git push%s %s" % (upstream_text, branch_name)).execute()


def get_clipboard_as_text():
    clipboard_instance = Clipboard()
    clipboard_instance.copy_from_system()

    return clipboard_instance.text


def format_directory_name(directory_name, format_type):
    if format_type is None:
        directory_name = barbecue(str(directory_name))
    else:
        directory_name = format_dictation(directory_name, format_type)

    return directory_name


directory_command_choice_map = {
    "make": "mkdir",
    "change": "cd",
    "remove": "rmdir",
}


def directory_command_choice(name="directory_command"):
    return Choice(name, directory_command_choice_map)


def output_directory_command(directory_name, format_type=None, directory_command=None):
    if directory_command is not None:
        Text(
            "%s %s" % (directory_command, format_directory_name(directory_name, format_type))
        ).execute()


git_clipboard_command_choice_map = {
    "clone": "clone",
    "reset": "reset",
    "revert": "revert",
    "add origin": "remote add origin",
}


def git_clipboard_command_choice(name="git_clipboard_command"):
    return Choice(name, git_clipboard_command_choice_map)


def output_git_clipboard_command(git_clipboard_command=None):
    if git_clipboard_command is not None:
        clipboard_output = get_clipboard_as_text()
        Text("git %s %s" % (git_clipboard_command, clipboard_output)).execute()


class TerminalUtilities(MappingRule):
    mapping = {
        "get [<git_command>]": Function(output_git_command),
        "get pull [<branch_name>]": Function(output_git_pull),
        "get push upstream [<branch_name>]": Function(output_git_push, set_up_stream=True),
        "get push [<branch_name>]": Function(output_git_push),
        "get <git_clipboard_command> from clipboard": Function(output_git_clipboard_command),
        "<directory_command> directory [<format_type>] [<directory_name>]":
            Function(output_directory_command),
        "zig cash been": Text("zig-cache/bin"),
        "code here": Text("code ."),
        "code without accessibility here": Text("code --disable-renderer-accessibility ."),
        "been": Text("bin"),
        "source": Text("src"),
        "neo-vim": Text("nvim"),
        "neo-vim QT": Text("nvim-qt"),
    }

    extras = [
        Dictation("branch_name", default=""),
        Dictation("repository_name", default=""),
        Dictation("directory_name", default=""),
        git_command_choice("git_command"),
        formatting_choice("format_type"),
        directory_command_choice("directory_command"),
        git_clipboard_command_choice("git_clipboard_command"),
    ]


# The main Terminal grammar rules are activated here
terminal_bootstrap = Grammar("terminal bootstrap")
terminal_bootstrap.add_rule(TerminalEnabler())
terminal_bootstrap.load()

terminal_grammar = Grammar("terminal grammar")
terminal_grammar.add_rule(TerminalUtilities())
terminal_grammar.add_rule(TerminalDisabler())
terminal_grammar.load()
terminal_grammar.enable()

# Unload function which will be called by natlink at unload time.


def unload():
    global terminal_grammar
    if terminal_grammar:
        terminal_grammar.unload()
    terminal_grammar = None
