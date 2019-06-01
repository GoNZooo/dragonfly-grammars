from dragonfly import (Grammar, CompoundRule, Text, Key, MappingRule)
from macro_utilities import (replace_percentage, sleep_exit)


def insert_function():
    return Text("const %% = (_) => {};") + replace_percentage(25)


class JavaScriptEnabler(CompoundRule):
    spec = "enable JavaScript"

    def _process_recognition(self, node, extras):
        javascriptBootstrap.disable()
        javascriptGrammar.enable()
        print "JavaScript grammar enabled!"


class JavaScriptDisabler(CompoundRule):
    spec = "disable JavaScript"

    def _process_recognition(self, node, extras):
        javascriptGrammar.disable()
        javascriptBootstrap.enable()
        print "JavaScript grammar disabled"


class JavaScriptUtilities(MappingRule):
    mapping = {
        "statement if":
        Text("if (") + sleep_exit(25) + Text("lmzi) {") + Key("enter")
        + sleep_exit(25) + Text("`z"),
        "good if": Text("%% ? _ : _") + replace_percentage(25),
        "exported function": Text("export ") + insert_function(),
        "anonymous function": Text("(%%) => {}") + replace_percentage(25),
        "const": Text("const %% = ;") + replace_percentage(25),
        "let": Text("let %% = ;") + replace_percentage(25),
        "function": insert_function(),
        "generic qualified import": Text("import * as _ from \"%%\";") + replace_percentage(25),
        "generic import": Text("import _ from \"%%\";") + replace_percentage(25),
        "import react": Text("import * as React from \"react\";"),
        "import internal utilities":
        Text("import {%%} from \"bynk-typescript-utils\";") + replace_percentage(25),
        "check equal": Text(" === "),
        "check somewhat equal": Text(" == "),
        "check not equal": Text(" !== "),
        "check not somewhat equal": Text(" != "),
        "arrow": Text(" => "),
        "equals": Text(" = "),
    }

    extras = []


# The main JavaScript grammar rules are activated here
javascriptBootstrap = Grammar("javascript bootstrap")
javascriptBootstrap.add_rule(JavaScriptEnabler())
javascriptBootstrap.load()

javascriptGrammar = Grammar("javascript grammar")
javascriptGrammar.add_rule(JavaScriptUtilities())
javascriptGrammar.add_rule(JavaScriptDisabler())
javascriptGrammar.load()
javascriptGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global javascriptGrammar
    if javascriptGrammar:
        javascriptGrammar.unload()
    javascriptGrammar = None
