# encoding: utf-8

from dragonfly import (Grammar, CompoundRule, Text, MappingRule, Function, Dictation, Choice)
from macro_utilities import (replace_in_text, execute_with_dictation)
from vim.rules.letter import (proper, snake_case)


class ElixirEnabler(CompoundRule):
    spec = "enable elixir"

    def _process_recognition(self, node, extras):
        elixirBootstrap.disable()
        elixirGrammar.enable()
        print "Elixir grammar enabled!"


class ElixirDisabler(CompoundRule):
    spec = "disable elixir"

    def _process_recognition(self, node, extras):
        elixirGrammar.disable()
        elixirBootstrap.enable()
        print "Elixir grammar disabled"


def output_module(module_name):
    execute_with_dictation(
        module_name,
        lambda n: Text("defmodule %s do\nend" % format_module_name(n)),
        lambda n: replace_in_text("defmodule $ do end")
    )


def output_struct(module_name):
    execute_with_dictation(
        module_name,
        lambda n: replace_in_text("defmodule %s do defstruct [$] end" % format_module_name(n)),
        lambda n: replace_in_text("defstruct [$]")
    )


def output_function(name):
    execute_with_dictation(
        name,
        lambda n: replace_in_text("def %s($) do _ end" % format_name(n)),
        lambda n: replace_in_text("def $(_) do _ end")
    )


def output_module_directive(module_name, directive):
    execute_with_dictation(
        module_name,
        lambda n: Text("%s %s" % (directive, format_module_name(n))),
        lambda n: Text("%s " % directive),
    )


def output_alias(module_name, alias_name):
    alias_suffix = ", as: %s" % format_module_name(alias_name) if alias_name != "" else ""

    execute_with_dictation(
        module_name,
        lambda n: Text("alias %s%s" % (format_module_name(n), alias_suffix)),
        lambda n: replace_in_text("alias $%s" % alias_suffix)
    )


def output_handle_cast(is_info=False):
    name = "info" if is_info else "cast"
    replace_in_text("def handle_%s(_message, _state) do$end" % name).execute()


def output_handle_call():
    replace_in_text("def handle_call(_message, _from, _state) do$end").execute()


def output_init():
    replace_in_text("def init($) do _ end").execute()


def output_binding(name):
    execute_with_dictation(
        name,
        lambda n: Text("%s = " % format_name(name)),
        lambda n: Text(" = ")
    )


def output_for_loop(name, binding):
    binding_text = format_name(binding) if binding != "" else "$"

    execute_with_dictation(
        name,
        lambda n: replace_in_text("for %s <- %s do $ end" % (binding_text, format_name(n))),
        lambda n: replace_in_text("for %s <- $ do end")
    )


gen_server_command_choice_map = {
    "start link": "start_link(__MODULE__, $, name: _name)",
    "call": "call(__MODULE__, $)",
    "cast": "cast(__MODULE__, $)",
}


def gen_server_command_choice(name="gen_server_command"):
    return Choice(name, gen_server_command_choice_map)


def output_gen_server_command(gen_server_command=None):
    has_command = replace_in_text("GenServer.%s" % gen_server_command)
    does_not_have_command = Text("GenServer")
    command = has_command if gen_server_command is not None else does_not_have_command

    command.execute()


def output_pipe_into(name):
    execute_with_dictation(
        name,
        lambda n: Text("|> %s()" % format_name(n)),
        lambda n: Text("|> ")
    )


log_level_choice_map = {
    "debug": "debug",
    "warn": "warn",
    "worn": "warn",
    "error": "error",
}


def log_level_choice(name="log_level"):
    return Choice(name, log_level_choice_map)


def output_log_statement(name, log_level=None):
    if log_level is not None:
        execute_with_dictation(
            name,
            lambda n: Text(
                "Logger.%s(\"XXXXXX: #{inspect(%s, pretty: true)}\")" % (log_level, format_name(n))
            ),
            lambda n: replace_in_text(
                "Logger.%s(\"XXXXXX: #{inspect($, pretty: true)}\")" %
                log_level
            ),
        )


interactive_command_choice_map = {
    "mix": "-S mix",
    "run": "-S mix",
    "phoenix": "-S mix phx.server",
    "run phoenix": "-S mix phx.server",
}


def interactive_command_choice(name="interactive_command"):
    return Choice(name, interactive_command_choice_map)


def output_interactive_command(interactive_command=None):
    interactive_command_output = interactive_command if interactive_command is not None else ""

    Text("iex %s" % interactive_command_output).execute()


mix_command_choice_map = {
    "test": "test",
    # @TODO: should probably make this a subcommand of its own
    "help": "help",
    # @TODO: should probably make this a subcommand of its own
    "new": "new ",
    "new phoenix": "phx.new ",
    "get dependencies": "deps.get",
    "compile dependencies": "deps.compile",
    "generate migration": "ecto.gen.migration ",
    "migrate": "ecto.migrate",
    "create database": "ecto.create",
}


def mix_command_choice(name="mix_command"):
    return Choice(name, mix_command_choice_map)


def output_mix_command(mix_command=None):
    if mix_command is not None:
        Text("mix %s" % mix_command).execute()


def format_module_name(name):
    name_string = str(name)
    components = name_string.split(".")
    module_name = ".".join([proper(n) for n in components])

    return module_name


def format_name(name):
    return snake_case(str(name))


class ElixirUtilities(MappingRule):
    mapping = {
        "for loop [over <name>] [binding <binding>]": Function(output_for_loop),
        "if": replace_in_text("if $ do _ else _"),
        "case": replace_in_text("case $ do_end"),
        "function [<name>]": Function(output_function),
        "handle cast": Function(output_handle_cast),
        "handle call": Function(output_handle_call),
        "handle info": Function(output_handle_cast, is_info=True),
        "define in it": Function(output_init),
        "module [<module_name>]": Function(output_module),
        "struct [<module_name>]": Function(output_struct),
        "[<name>] equals": Function(output_binding),
        "anonymous function": replace_in_text("fn ($) -> _ end"),
        "spec": replace_in_text("@spec $(_) :: _"),
        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "map": Text("Enum.map"),
        "reduce": Text("Enum.reduce"),
        "enumeration": Text("Enum"),
        "equals": Text(" = "),
        "arrow": Text(" -> "),
        "fat arrow": Text(" => "),
        "log <log_level> [<name>]": Function(output_log_statement),
        "use [<module_name>]": Function(output_module_directive, directive="use"),
        "use jen server": Text("use GenServer"),
        "jen server [<gen_server_command>]": Function(output_gen_server_command),
        "require [<module_name>]": Function(output_module_directive, directive="require"),
        "alias [<module_name>] [as <alias_name>]": Function(output_alias),
        "interactive [<interactive_command>]": Function(output_interactive_command),
        "pipe into [<name>]": Function(output_pipe_into),
        "mix <mix_command>": Function(output_mix_command),
    }

    extras = [
        Dictation("module_name", default=""),
        Dictation("alias_name", default=""),
        Dictation("name", default=""),
        Dictation("binding", default=""),
        gen_server_command_choice("gen_server_command"),
        log_level_choice("log_level"),
        interactive_command_choice("interactive_command"),
        mix_command_choice("mix_command"),
    ]


# The main Elixir grammar rules are activated here
elixirBootstrap = Grammar("elixir bootstrap")
elixirBootstrap.add_rule(ElixirEnabler())
elixirBootstrap.load()

elixirGrammar = Grammar("elixir grammar")
elixirGrammar.add_rule(ElixirUtilities())
elixirGrammar.add_rule(ElixirDisabler())
elixirGrammar.load()
elixirGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global elixirGrammar
    if elixirGrammar:
        elixirGrammar.unload()
    elixirGrammar = None
