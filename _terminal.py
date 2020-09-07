from dragonfly import (Grammar, CompoundRule, Text, MappingRule, Dictation, Function, Choice)
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
    upstream_text = ""
    if set_up_stream:
        upstream_text = " -u"

    branch_name = format_branch_name(branch_name)
    Text("git push%s %s" % (upstream_text, branch_name)).execute()


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


build_target_name_choice_map = {
    "linux": "linux",
    "windows": "windows",
    "free BSD": "freebsd",
    "Mac OS": "macos",
    "OS x": "macos",
    "OS ten": "macos",
}


def build_target_name_choice(name="build_target_name"):
    return Choice(name, build_target_name_choice_map)


def output_zig_build(build_target_name=None, gnu=False, optimization=None):
    libc_spec = ""
    if gnu:
        libc_spec = "-gnu"

    command_output = "zig build"
    if build_target_name is not None:
        command_output = "zig build -Dtarget=native-%s%s" % (build_target_name, libc_spec)
    elif gnu:
        command_output = "zig build -Dtarget=native-native-gnu"

    if optimization is not None:
        command_output += " %s" % optimization

    Text(command_output).execute()


optimization_choice_map = {
    "release": "-Drelease-fast=true",
    "fast": "-Drelease-fast=true",
    "release fast": "-Drelease-fast=true",
    "safe": "-Drelease-safe=true",
    "release safe": "-Drelease-safe=true",
    "small": "-Drelease-small=true",
    "release small": "-Drelease-small=true",
}


def optimization_choice(name="optimization"):
    return Choice(name, optimization_choice_map)


class TerminalUtilities(MappingRule):
    mapping = {
        "get [<git_command>]": Function(output_git_command),
        "get pull [<branch_name>]": Function(output_git_pull),
        "get push upstream [<branch_name>]": Function(output_git_push, set_up_stream=True),
        "get push [<branch_name>]": Function(output_git_push),
        "zig build [<optimization>] [for <build_target_name>]": Function(output_zig_build,
                                                                         gnu=False),
        "zig build [<optimization>] [for <build_target_name>] with Stallman":
            Function(output_zig_build, gnu=True),
        "<directory_command> directory [<format_type>] [<directory_name>]":
            Function(output_directory_command),
        "zig cash been": Text("zig-cache/bin"),
        "been": Text("bin"),
        "source": Text("src"),
    }

    extras = [
        Dictation("branch_name", default=""),
        Dictation("directory_name", default=""),
        git_command_choice("git_command"),
        formatting_choice("format_type"),
        directory_command_choice("directory_command"),
        build_target_name_choice("build_target_name"),
        optimization_choice("optimization"),
    ]


# The main Terminal grammar rules are activated here
terminal_bootstrap = Grammar("terminal bootstrap")
terminal_bootstrap.add_rule(TerminalEnabler())
terminal_bootstrap.load()

terminal_grammar = Grammar("terminal grammar")
terminal_grammar.add_rule(TerminalUtilities())
terminal_grammar.add_rule(TerminalDisabler())
terminal_grammar.load()
terminal_grammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global terminal_grammar
    if terminal_grammar:
        terminal_grammar.unload()
    terminal_grammar = None
