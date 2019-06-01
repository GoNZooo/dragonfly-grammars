# encoding: utf-8

from dragonfly import (Grammar, CompoundRule, Text, MappingRule)
from macro_utilities import (replace_percentage)


def insert_log_statement(log_level):
    return (Text("Logger.") + Text(log_level) +
            Text("(\"XXXXXX: #{inspect(%%, pretty: true)}\")") + replace_percentage(25))


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


class ElixirUtilities(MappingRule):
    mapping = {
        "if": Text("if %% do _ else _") + replace_percentage(25),
        "case": Text("case %% do_end") + replace_percentage(25),
        "function": Text("def %%(_) do_end") + replace_percentage(25),
        "module": Text("defmodule %% do_end") + replace_percentage(25),
        "struct": Text("defstruct [%%]") + replace_percentage(25),
        "anonymous function": Text("fn (%%) -> _ end") + replace_percentage(25),
        "spec": Text("@spec %%(_) :: _") + replace_percentage(25),
        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "map": Text("Enum.map"),
        "reduce": Text("Enum.reduce"),
        "enumeration": Text("Enum"),
        "equals": Text(" = "),
        "arrow": Text(" -> "),
        "fat arrow": Text(" => "),
        "log debug": insert_log_statement("debug"),
        "log (warn|worn)": insert_log_statement("warn"),
        "log error": insert_log_statement("error"),
        "log info": insert_log_statement("info"),
    }

    extras = []


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
