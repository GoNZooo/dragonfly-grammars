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
        function_name = format_name(function_name)
        command = replace_in_text("def %s($):" % function_name)
    command.execute()


def output_class(class_name, superclass):
    if superclass != "":
        superclass = "(" + proper(str(superclass)) + ")"
    if class_name == "":
        command = replace_in_text("class $%s:" % superclass)
    else:
        class_name = proper(str(class_name))
        command = Text("class %s%s:" % (class_name, superclass)) + Key("enter")
    command.execute()


def output_from_import(import_name):
    if import_name == "":
        command = replace_in_text("from $ import (_)")
    else:
        import_name = format_name(import_name)
        command = replace_in_text("from %s import ($)" % import_name)
    command.execute()


def output_qualified_import(import_name):
    if import_name == "":
        command = replace_in_text("import $ as _")
    else:
        import_name = format_name(import_name)
        command = replace_in_text("import %s as $" % import_name)
    command.execute()


def output_if(name):
    output_if_or_else_if("if", name)


def output_else_if(name):
    output_if_or_else_if("elif", name)


def output_if_or_else_if(statement_type, name):
    if name == "":
        command = replace_in_text("%s $:" % statement_type)
    else:
        name = format_name(name)
        command = replace_in_text("%s %s$:" % (statement_type, name))
    command.execute()


def output_for_loop(name):
    if name == "":
        command = replace_in_text("for $ in _:")
    else:
        name = format_name(name)
        command = replace_in_text("for $ in %s:" % name)
    command.execute()


def output_binding(name):
    if name == "":
        command = Text(" = ")
    else:
        name = format_name(name)
        command = Text("%s = " % name)
    command.execute()


def output_string_from(name):
    if name == "":
        command = replace_in_text("str($)")
    else:
        name = format_name(name)
        command = Text("str(%s)" % name)
    command.execute()


def output_check_equal(name):
    output_comparison("==", name)


def output_check_not_equal(name):
    output_comparison("!=", name)


def output_comparison(operator, name):
    if name == "":
        command = Text(" %s " % operator)
    else:
        name = format_name(name)
        command = Text("%s %s " % (name, operator))
    command.execute()


def output_if_equal(name):
    if name == "":
        command = replace_in_text("if $ == _:")
    else:
        name = format_name(name)
        command = replace_in_text("if %s == $:" % name)
    command.execute()


def output_if_not_equal(name):
    if name == "":
        command = replace_in_text("if $ != _:")
    else:
        name = format_name(name)
        command = replace_in_text("if %s != $:" % name)
    command.execute()


def output_else_if_equal(name):
    if name == "":
        command = replace_in_text("elif $ == _:")
    else:
        name = format_name(name)
        command = replace_in_text("elif %s == $:" % name)
    command.execute()


def output_else_if_not_equal(name):
    if name == "":
        command = replace_in_text("elif $ != _:")
    else:
        name = format_name(name)
        command = replace_in_text("elif %s != $:" % name)
    command.execute()


def output_anonymous_function(name):
    if name == "":
        command = replace_in_text("lambda $: ")
    else:
        name = format_name(name)
        command = replace_in_text("lambda %s: $" % name)
    command.execute()


def format_name(name):
    return snake_case(str(name))


def output_length_of(name):
    if name != "":
        command = replace_in_text("len($)")
    else:
        name = format_name(name)
        command = Text("len(%s)" % name)
    command.execute()


class PythonUtilities(MappingRule):
    mapping = {
        "else if [<name>]": Function(output_else_if),
        "else if [<name>] is equal": Function(output_else_if_equal),
        "else if [<name>] is not equal": Function(output_else_if_not_equal),
        "else": Text("else:") + Key("enter"),
        "if [<name>]": Function(output_if),
        "if [<name>] is equal": Function(output_if_equal),
        "if [<name>] is not equal": Function(output_if_not_equal),
        "for loop [over <name>]": Function(output_for_loop),
        "while loop": replace_in_text("while $:"),
        "pass": Text("pass"),
        "class [<class_name>] [derives from <superclass>]": Function(output_class),
        "anonymous function [taking <name>]": Function(output_anonymous_function),
        "function [<function_name>]": Function(output_function),
        "from [<import_name>] import": Function(output_from_import),
        "qualified import [<import_name>]": Function(output_qualified_import),
        "import dragonfly": Text("import dragonfly as dragonfly"),
        "check [<name>] is equal": Function(output_check_equal),
        "check [<name>] is not equal": Function(output_check_not_equal),
        "[<name>] equals": Function(output_binding),
        "string from [<name>]": Function(output_string_from),
        "length of [<name>]": Function(output_length_of),
    }

    extras = [
        Dictation("function_name", default=""),
        Dictation("class_name", default=""),
        Dictation("superclass", default=""),
        Dictation("import_name", default=""),
        Dictation("name", default=""),
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
