from dragonfly import (Grammar, CompoundRule, Text, Key, MappingRule, Dictation, Function)
from macro_utilities import (replace_in_text)
from vim.rules.letter import (snake_case, proper)


class PythonEnabler(CompoundRule):
    spec = "enable Python"

    def _process_recognition(self, node, extras):
        pythonBootstrap.disable()
        pythonGrammar.enable()
        print "Python grammar enabled!"


class PythonDisabler(CompoundRule):
    spec = "disable Python"

    def _process_recognition(self, node, extras):
        pythonGrammar.disable()
        pythonBootstrap.enable()
        print "Python grammar disabled"


def output_function(function_name):
    if function_name == "":
        command = replace_in_text("def $(_):")
    else:
        function_name = snake_case(str(function_name))
        command = replace_in_text("def %s($):" % function_name)
    command.execute()


def output_class(class_name):
    if class_name == "":
        command = replace_in_text("class $:")
    else:
        class_name = proper(str(class_name))
        command = Text("class %s:" % class_name) + Key("enter")
    command.execute()


def output_from_import(import_name):
    if import_name == "":
        command = replace_in_text("from $ import (_)")
    else:
        import_name = snake_case(str(import_name))
        command = replace_in_text("from %s import ($)" % import_name)
    command.execute()


def output_qualified_import(import_name):
    if import_name == "":
        command = replace_in_text("import $ as _")
    else:
        import_name = snake_case(str(import_name))
        command = replace_in_text("import %s as $" % import_name)
    command.execute()


class PythonUtilities(MappingRule):
    mapping = {
        "else if": replace_in_text("elif $:"),
        "else": Text("else:") + Key("enter"),
        "if": replace_in_text("if $:"),
        "for loop": replace_in_text("for $ in _:"),
        "while loop": replace_in_text("while $:"),
        "pass": Text("pass"),
        "class [<class_name>]": Function(output_class),
        "anonymous function": replace_in_text("lambda $: "),
        "function [<function_name>]": Function(output_function),
        "from [<import_name>] import": Function(output_from_import),
        "qualified import [<import_name>]": Function(output_qualified_import),
        "import dragonfly": Text("import dragonfly as dragonfly"),
        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "equals": Text(" = "),
    }

    extras = [
        Dictation("function_name", default=""),
        Dictation("class_name", default=""),
        Dictation("import_name", default="")
    ]


# The main Python grammar rules are activated here
pythonBootstrap = Grammar("python bootstrap")
pythonBootstrap.add_rule(PythonEnabler())
pythonBootstrap.load()

pythonGrammar = Grammar("python grammar")
pythonGrammar.add_rule(PythonUtilities())
pythonGrammar.add_rule(PythonDisabler())
pythonGrammar.load()
pythonGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global pythonGrammar
    if pythonGrammar:
        pythonGrammar.unload()
    pythonGrammar = None
