from dragonfly import (Grammar, CompoundRule, Text, MappingRule, Function, Dictation, Choice)
from macro_utilities import (replace_in_text, execute_with_dictation, with_dictation,
                             comment_choice)
from vim.rules.letter import (camel_case, proper, barbecue)


class TypescriptEnabler(CompoundRule):
    spec = "enable typescript"

    def _process_recognition(self, node, extras):
        typescriptBootstrap.disable()
        typescriptGrammar.enable()
        print("Typescript grammar enabled!")


class TypescriptDisabler(CompoundRule):
    spec = "disable Typescript"

    def _process_recognition(self, node, extras):
        typescriptGrammar.disable()
        typescriptBootstrap.enable()
        print("Typescript grammar disabled")


visibility_attribute_choice_map = {
    "public": "export",
    "exported": "export",
    "export": "export",
}


def visibility_attribute_choice(name="visibility_attribute"):
    return Choice(name, visibility_attribute_choice_map)


def output_function(function_name, visibility_attribute=None, asynchronous=False):
    attribute_output = ""
    if visibility_attribute is not None:
        attribute_output = "%s " % visibility_attribute

    asynchronous_output = ""
    if asynchronous:
        asynchronous_output = "async "

    execute_with_dictation(
        function_name,
        lambda n: replace_in_text(
            "%sconst %s = %s($): _ => {};" % (
                attribute_output, format_function_name(n), asynchronous_output
            )
        ),
        lambda n: replace_in_text(
            "%sconst $ = %s(_): _ => {};" % (attribute_output, asynchronous_output)
        )
    )


comparison_choice_map = {
    "equal": ("=== $", replace_in_text),
    "not equal": ("!== $", replace_in_text),
    "less or equal": ("<= $", replace_in_text),
    "greater or equal": (">= $", replace_in_text),
    "less": ("< $", replace_in_text),
    "greater": ("> $", replace_in_text),
    # these are all for null
    "null": ("=== null", Text),
    "not null": ("!== null", Text),
    "none": ("=== null", Text),
    "not none": ("!== null", Text),
    # for undefined
    "undefined": ("=== undefined", Text),
    "not undefined": ("!== undefined", Text),
}


def comparison_choice(name="comparison"):
    return Choice(name, comparison_choice_map)


def output_if_comparison(name, comparison=None, construct="if"):
    if comparison is not None:
        (comparison_text, comparison_command) = comparison
        execute_with_dictation(
            name,
            lambda n: comparison_command(
                "%s (%s %s) {}" % (construct, format_name(n), comparison_text)
            ),
            lambda n: replace_in_text("%s ($ %s) {}" % (construct, comparison_text))
        )
    else:
        execute_with_dictation(
            name,
            lambda n: Text("%s (%s) {}" % (construct, format_name(n))),
            lambda n: replace_in_text("%s ($) {}" % construct)
        )


def output_value(name, definition_type, visibility_attribute=None):
    attribute_output = ""
    if visibility_attribute is not None:
        attribute_output = "%s " % visibility_attribute

    if name == "":
        command = replace_in_text("%s%s $ = _;" % (attribute_output, definition_type))
    else:
        name = format_name(name)
        command = replace_in_text("%s%s %s = $;" % (attribute_output, definition_type, name))
    command.execute()


def output_switch(name):
    if name == "":
        command = replace_in_text("switch ($) {}")
    else:
        name = format_name(name)
        command = Text("switch (%s) {}" % name)
    command.execute()


def output_import_from(import_name):
    if import_name == "":
        command = replace_in_text("import _ from \"$\";")
    else:
        import_name = format_import_name(import_name)
        command = replace_in_text("import $ from \"%s\";" % import_name)
    command.execute()


def output_import_as(import_name):
    if import_name == "":
        command = replace_in_text("import * as _ from \"$\";")
    else:
        import_name = format_import_name(import_name)
        command = replace_in_text("import * as $ from \"%s\";" % import_name)
    command.execute()


def output_interface(type_name, visibility_attribute=None):
    attribute_output = ""
    if visibility_attribute is not None:
        attribute_output = "%s " % visibility_attribute

    if type_name == "":
        command = Text("%sinterface " % attribute_output)
    else:
        type_name = format_type_name(type_name)
        command = Text("%sinterface %s {}" % (attribute_output, type_name))
    command.execute()


def output_type(type_name, visibility_attribute=None):
    attribute_output = ""
    if visibility_attribute is not None:
        attribute_output = "%s " % visibility_attribute

    if type_name == "":
        command = replace_in_text("%stype $ = _" % attribute_output)
    else:
        type_name = format_type_name(type_name)
        command = replace_in_text("%stype %s = $" % (attribute_output, type_name))
    command.execute()


def format_function_name(name):
    return camel_case(str(name))


def format_type_name(name):
    return proper(str(name))


def format_name(name):
    return camel_case(str(name))


def format_import_name(import_name):
    return barbecue(str(import_name))


def output_binding(name):
    if name == "":
        command = Text(" = ")
    else:
        name = format_name(name)
        command = Text("%s = " % name)
    command.execute()


def output_check_comparison(name, comparison=None):
    if comparison is not None:
        (comparison_text, comparison_command) = comparison
        if name == "":
            command = replace_in_text("$ %s" % comparison_text)
        else:
            name = format_name(name)
            command = Text("%s %s " % (name, comparison))
        command.execute()


def output_function_call(function_name, name):
    def do_output(fn):
        with_function_name = with_dictation(
            name,
            lambda n: Text("%s(%s)" % (format_function_name(fn), format_name(n))),
            lambda n: replace_in_text("%s($)" % format_function_name(fn))
        )
        without_function_name = with_dictation(
            name,
            lambda n: replace_in_text("$(%s)" % format_name(n)),
            lambda n: replace_in_text("$(_)")
        )

        return without_function_name if fn == "$" else with_function_name

    execute_with_dictation(
        function_name,
        lambda n: do_output(n),
        lambda n: do_output("$")
    )


def output_method_call(function_name, name):
    def do_output(fn):
        with_method_name = with_dictation(
            name,
            lambda n: Text("%s.%s()" % (format_name(n), format_function_name(fn))),
            lambda n: replace_in_text("$.%s()" % format_function_name(fn))
        )

        without_method_name = with_dictation(
            name,
            lambda n: replace_in_text("%s.$()" % format_name(n)),
            lambda n: replace_in_text("$._()")
        )

        return without_method_name if fn == "$" else with_method_name

    execute_with_dictation(
        function_name,
        lambda n: do_output(n),
        lambda n: do_output("$")
    )


def output_comment(comment, comment_type=None):
    type_output = comment_type if comment_type is not None else ""
    Text("// %s %s" % (type_output, comment)).execute()


class TypescriptUtilities(MappingRule):
    mapping = {
        # control flow
        "if [<name>] [is <comparison>]": Function(output_if_comparison),
        "else if [<name>] [is <comparison>]": Function(output_if_comparison, construct="else if"),
        "else": Text("else {\n"),
        "switch [<name>]": Function(output_switch),
        "ternary": replace_in_text("$ ? _ : _"),

        # bare comparisons
        "check [<name>] [is <comparison>]": Function(output_check_comparison),

        # function and value definitions
        "[<visibility_attribute>] function [<function_name>]": Function(output_function),
        "[<visibility_attribute>] asynchronous function [<function_name>]":
            Function(output_function, asynchronous=True),
        "[<visibility_attribute>] constant [<name>]": Function(output_value,
                                                               definition_type="const"),
        "[<visibility_attribute>] let [<name>]": Function(output_value, definition_type="let"),
        "[<name>] equals": Function(output_binding),
        "anonymous function": replace_in_text("($) => _"),

        # type definitions
        "[<visibility_attribute>] interface [<type_name>]": Function(output_interface),
        "[<visibility_attribute>] type [<type_name>]": Function(output_type),

        # calling functions and methods
        "call [<function_name>] with [<name>]": Function(output_function_call),
        "method [<function_name>] on [<name>]": Function(output_method_call),

        # miscellaneous helpers
        "import from [<import_name>]": Function(output_import_from),
        "import as [<import_name>]": Function(output_import_as),
        "import react": Text("import * as React from \"react\";"),
        "import express": Text("import express from \"express\";"),
        "[<comment_type>] comment [<comment>]": Function(output_comment),

        "arrow": Text(" => "),
        "a sink": Text("async "),
    }

    extras = [
        Dictation("name", default=""),
        Dictation("function_name", default=""),
        Dictation("import_name", default=""),
        Dictation("type_name", default=""),
        Dictation("comment", default=""),
        visibility_attribute_choice("visibility_attribute"),
        comparison_choice("comparison"),
        comment_choice("comment_type"),
    ]


# The main Typescript grammar rules are activated here
typescriptBootstrap = Grammar("typescript bootstrap")
typescriptBootstrap.add_rule(TypescriptEnabler())
typescriptBootstrap.load()

typescriptGrammar = Grammar("typescript grammar")
typescriptGrammar.add_rule(TypescriptUtilities())
typescriptGrammar.add_rule(TypescriptDisabler())
typescriptGrammar.load()
typescriptGrammar.disable()


def unload():
    global typescriptGrammar
    if typescriptGrammar:
        typescriptGrammar.unload()
    typescriptGrammar = None
