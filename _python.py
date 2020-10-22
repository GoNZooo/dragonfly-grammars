from dragonfly import (Grammar, CompoundRule, Text, Key, MappingRule, Dictation, Function, Choice)
from macro_utilities import (replace_in_text, comment_choice, execute_with_dictation)
from vim.rules.letter import (snake_case, proper)


class PythonEnabler(CompoundRule):
    spec = "enable Python"

    def _process_recognition(self, node, extras):
        pythonBootstrap.disable()
        pythonGrammar.enable()
        print("Python grammar enabled!")


class PythonDisabler(CompoundRule):
    spec = "disable Python"

    def _process_recognition(self, node, extras):
        pythonGrammar.disable()
        pythonBootstrap.enable()
        print("Python grammar disabled")


comparison_choice_map = {
    "equal": "==",
    "not equal": "!=",
    "less or equal": "<=",
    "greater or equal": ">=",
    "less": "<",
    "greater": ">",
    "none": "is None",
    "not none": "is not None",
}


def comparison_choice(name="comparison"):
    return Choice(name, comparison_choice_map)


def output_if_comparison(name, comparison=None, construct="if"):
    if comparison is not None:
        execute_with_dictation(
            name,
            on_dictation=lambda v: Text("%s %s %s " % (construct, format_name(v), comparison)),
            on_other=lambda v: replace_in_text("%s $ %s:" % (construct, comparison))
        )


def output_if_expression_comparison(name, comparison=None):
    if comparison is not None:
        execute_with_dictation(
            name,
            on_dictation=lambda v: replace_in_text(
                "_ if %s %s $ else _" % (format_name(v), comparison)),
            on_other=lambda v: replace_in_text("_ if $ %s _ else _" % comparison)
        )


def output_function(function_name):
    execute_with_dictation(
        function_name,
        on_dictation=lambda v: replace_in_text("def %s($):" % format_name(v)),
        on_other=lambda v: replace_in_text("def $(_):")
    )


def output_class(class_name, superclass):
    if superclass != "":
        superclass = "(" + format_class_name(superclass) + ")"

    execute_with_dictation(
        class_name,
        on_dictation=lambda v: Text("class %s%s:" % (format_class_name(v), superclass)),
        on_other=lambda v: replace_in_text("class $%s:" % superclass)
    )


def output_from_import(import_name):
    execute_with_dictation(
        import_name,
        on_dictation=lambda v: replace_in_text("from %s import ($)" % format_name(v)),
        on_other=lambda v: replace_in_text("from $ import (_)")
    )


def output_qualified_import(import_name):
    execute_with_dictation(
        import_name,
        on_dictation=lambda v: Text("import %s as " % format_name(v)),
        on_other=lambda v: replace_in_text("import $ as _"),
    )


def output_if(name, statement_type="if"):
    execute_with_dictation(
        name,
        on_dictation=lambda v: Text("%s %s:" % (statement_type, format_name(name))),
        on_other=lambda v: replace_in_text("%s $:" % statement_type),
    )


def output_if_expression(name):
    execute_with_dictation(
        name,
        on_dictation=lambda v: replace_in_text("$ if %s else _" % format_name(name)),
        on_other=lambda v: replace_in_text("_ if $ else _"),
    )


def output_for_loop(name):
    execute_with_dictation(
        name,
        on_dictation=lambda v: replace_in_text("for $ in %s:" % format_name(name)),
        on_other=lambda v: replace_in_text("for $ in _:"),
    )


def output_binding(name):
    execute_with_dictation(
        name,
        on_dictation=lambda v: Text("%s = " % format_name(name)),
        on_other=lambda v: Text(" = ")
    )


def output_wrapped_optional_name(name, around):
    execute_with_dictation(
        name,
        on_dictation=lambda v: Text("%s(%s)" % (around, format_name(name))),
        on_other=lambda v: replace_in_text("%s($)" % around)
    )


def output_comparison(name, comparison=None):
    if comparison is not None:
        execute_with_dictation(
            name,
            on_dictation=lambda v: Text("%s %s " % (format_name(name), comparison)),
            on_other=lambda v: Text(" %s " % comparison)
        )


def output_anonymous_function(name):
    execute_with_dictation(
        name,
        on_dictation=lambda v: replace_in_text("lambda %s: $" % format_name(name)),
        on_other=lambda v: replace_in_text("lambda $: ")
    )


def output_comment(comment, comment_type=None):
    if comment_type is None:
        output_text = "# %s" % comment
    else:
        output_text = "# %s %s" % (comment_type, comment)
    Text(output_text).execute()


def output_method_call(method_name, name):
    method_name = format_name(method_name)
    name = format_name(name)

    if method_name == "" and name == "":
        command = replace_in_text("$._()")
    elif method_name == "":
        command = replace_in_text("%s.$()" % name)
    elif name == "":
        command = replace_in_text("$.%s()" % method_name)
    else:
        command = Text("%s.%s()" % (name, method_name))

    command.execute()


def output_function_call(function_name, name):
    function_name = format_name(function_name)
    name = format_name(name)

    if function_name == "" and name == "":
        command = replace_in_text("_($)")
    elif function_name == "":
        command = replace_in_text("$(%s)" % name)
    elif name == "":
        command = replace_in_text("%s($)" % function_name)
    else:
        command = Text("%s(%s)" % (function_name, name))

    command.execute()


def format_name(name):
    return snake_case(str(name))


def format_class_name(name):
    return proper(str(name))


class PythonUtilities(MappingRule):
    mapping = {
        # control flow
        "if [<name>] is <comparison>": Function(output_if_comparison, construct="if"),
        "if [<name>]": Function(output_if, construct="if"),
        "expression if [<name>] is <comparison>": Function(output_if_expression_comparison),
        "expression if [<name>]": Function(output_if_expression),

        "else if [<name>]": Function(output_if, statement_type="elif"),
        "else if [<name>] is <comparison>": Function(output_if_comparison, construct="elif"),

        "else": Text("else:") + Key("enter"),

        # loops
        "for loop [over <name>]": Function(output_for_loop),
        "while loop": replace_in_text("while $:"),

        # logic checks
        "check [<name>] is <comparison>": Function(output_comparison),

        # declarations/definitions
        "function [<function_name>]": Function(output_function),
        "class [<class_name>] [derives from <superclass>]": Function(output_class),
        "anonymous function [taking <name>]": Function(output_anonymous_function),
        "[<name>] equals": Function(output_binding),

        # imports
        "from [<import_name>] import": Function(output_from_import),
        "qualified import [<import_name>]": Function(output_qualified_import),
        "import dragonfly": Text("import dragonfly as dragonfly"),

        # other convenience
        "method [<method_name>] on [<name>]": Function(output_method_call),
        "call [<function_name>] on [<name>]": Function(output_function_call),
        "string from [<name>]": Function(output_wrapped_optional_name, around="str"),
        "length of [<name>]": Function(output_wrapped_optional_name, around="len"),
        "pass": Text("pass"),
        "[<comment_type>] comment [<comment>]": Function(output_comment),
    }

    extras = [
        Dictation("function_name", default=""),
        Dictation("class_name", default=""),
        Dictation("superclass", default=""),
        Dictation("import_name", default=""),
        Dictation("name", default=""),
        Dictation("method_name", default=""),
        comparison_choice("comparison"),
        comment_choice("comment_type"),
        Dictation("comment", default="")
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


def unload():
    global pythonGrammar
    if pythonGrammar:
        pythonGrammar.unload()
    pythonGrammar = None
