from vim.rules.letter import (snake_case, proper, camel_case)
from macro_utilities import (replace_in_text, comment_choice, execute_with_dictation)
from dragonfly import (Grammar, CompoundRule, Text, MappingRule,
                       Dictation, Function, Choice, IntegerRef)
from textwrap import (wrap)


class ZigEnabler(CompoundRule):
    spec = "enable zig"

    def _process_recognition(self, node, extras):
        zigBootstrap.disable()
        zigGrammar.enable()
        print "Zig grammar enabled!"


class ZigDisabler(CompoundRule):
    spec = "disable zig"

    def _process_recognition(self, node, extras):
        zigGrammar.disable()
        zigBootstrap.enable()
        print "Zig grammar disabled"


comparison_choice_map = {
    "equal": "==",
    "not equal": "!=",
    "less or equal": "<=",
    "greater or equal": ">=",
    "less": "<",
    "greater": ">",
}


def comparison_choice(name="comparison"):
    return Choice(name, comparison_choice_map)


def output_test(test_name):
    if test_name == "":
        command = replace_in_text("test \"$\" {}")
    else:
        command = Text("test \"%s\" {\n" % test_name)
    command.execute()


def output_constant(value_name, type_name):
    if type_name != "":
        value_type_components = str(type_name).split(" ")
        if len(value_type_components) != 1:
            type_name = proper(str(type_name))
    output_value("const", value_name, type_name)


def output_variable(value_name, type_name, is_undefined=False):
    if type_name != "":
        value_type_components = str(type_name).split(" ")
        if len(value_type_components) != 1:
            type_name = proper(str(type_name))
    else:
        type_name = "_"
    output_value("var", value_name, type_name, is_undefined=is_undefined)


def output_value(definition_type, value_name, type_name, is_undefined=False):
    value_placeholder = "undefined" if is_undefined else "$"

    if value_name == "":
        command = replace_in_text("%s $ = %s;" % (definition_type, value_placeholder))
    else:
        value_name = format_value_name(value_name)
        if type_name != "":
            value_name += ": %s" % type_name
        if is_undefined:
            command_constructor = Text
        else:
            command_constructor = replace_in_text
        command = command_constructor("%s %s = %s;" %
                                      (definition_type, value_name, value_placeholder))
    command.execute()


def output_type_definition(type_name, definition_type):
    if type_name == "":
        command = Text("%s {}" % definition_type)
    else:
        type_name = proper(str(type_name))
        command = replace_in_text("const %s = %s {$};" % (type_name, definition_type))
    command.execute()


def output_for_loop(value_name, binding_name=None):
    binding = format_value_name(binding_name) if binding_name is not None else "_"

    if value_name == "":
        command = replace_in_text("for ($) |%s| {}" % binding)
    else:
        value_name = format_value_name(value_name)
        if binding_name is not None:
            command = Text("for (%s) |%s| {}" % (value_name, binding))
        else:
            command = replace_in_text("for (%s) |$| {}" % value_name)
    command.execute()


def output_while_loop(value_name, binding_name=None):
    maybe_unpack = "|%s| " % format_value_name(binding_name) if binding_name is not None else ""

    if value_name == "":
        command = replace_in_text("while ($) %s{}" % (maybe_unpack))
    else:
        value_name = format_value_name(value_name)
        command = Text("while (%s) %s{}" % (value_name, maybe_unpack))
    command.execute()


def output_if(value_name, construct):
    if value_name == "":
        command = replace_in_text("%s ($) {}" % construct)
    else:
        value_name = format_value_name(value_name)
        command = Text("%s (%s) {}" % (construct, value_name))
    command.execute()


def output_switch(value_name):
    if value_name == "":
        command = replace_in_text("switch ($) {}")
    else:
        value_name = format_value_name(value_name)
        command = Text("switch (%s) {}" % value_name)
    command.execute()


def output_function(function_name, type_name, visibility_attribute=None):
    attribute_string = visibility_attribute + " " if visibility_attribute is not None else ""

    if type_name != "":
        type_name_components = str(type_name).split(" ")
        if len(type_name_components) != 1:
            type_name = proper(str(type_name))
    else:
        type_name = "_"
    if function_name == "":
        command = replace_in_text("%sfn $(_) %s {}" % (attribute_string, type_name))
    else:
        function_name = format_function_name(function_name)
        command = replace_in_text("%sfn %s($) %s {}" % (attribute_string, function_name, type_name))
    command.execute()


def output_if_comparison(value_name, construct, comparison=None):
    if comparison is not None:
        if value_name == "":
            command = replace_in_text("%s ($ %s _) {}" % (construct, comparison))
        else:
            value_name = snake_case(str(value_name))
            command = replace_in_text("%s (%s %s $) {}" % (construct, value_name, comparison))
        command.execute()


def output_unpack_if(value_name, binding_name=None):
    if binding_name is not None:
        binding_name = "|%s|" % format_value_name(binding_name)
    else:
        if value_name == "":
            binding_name = "|_|"
        else:
            binding_name = "|$|"

    if value_name == "":
        command = replace_in_text("if ($) %s {}" % binding_name)
    else:
        value_name = format_value_name(value_name)
        command = Text("if (%s) %s {}" % (value_name, binding_name))
    command.execute()


def format_value_name(name):
    return snake_case(str(name).replace("-", "_"))


def output_comment(comment, comment_type=None):
    if comment_type == "documentation":
        output_text = "/// %s" % comment
    elif comment_type is None:
        output_text = "// %s" % comment
    else:
        output_text = "// %s %s" % (comment_type, comment)
    Text(output_text).execute()


def output_comparison(value_name, comparison=None):
    if comparison is not None:
        if value_name == "":
            command = replace_in_text("$ %s _" % comparison)
        else:
            value_name = format_value_name(value_name)
            command = Text("%s %s " % (value_name, comparison))
        command.execute()


def output_binding(value_name, is_pointer=False):
    pointer_suffix = ".*" if is_pointer else ""

    if value_name == "":
        command = replace_in_text("$%s = " % pointer_suffix)
    else:
        value_name = format_value_name(value_name)
        command = Text("%s%s = " % (value_name, pointer_suffix))
    command.execute()


visibility_attribute_map = {
    "external": "extern",
    "public": "pub",
}


def format_function_name(function_name):
    return camel_case(str(function_name).replace("-", ""))


def visibility_attribute_choice(name="visibility_attribute"):
    return Choice(name, visibility_attribute_map)


class CastingSpec:
    def __init__(self, casting_type, size, prefix):
        self.casting_type = casting_type
        self.size = size
        self.prefix = prefix

    def get_cast_expression(self, value):
        type_to_cast_into = self.prefix + str(self.size)

        return "%s(%s, %s)" % (self.casting_type, type_to_cast_into, value)

    def get_safe_cast_expression(self, value):
        type_to_cast_into = self.prefix + str(self.size)

        return "@as(%s, %s)" % (type_to_cast_into, value)


class CastingFloat(CastingSpec):
    def __init__(self, size):
        CastingSpec.__init__(self, "@floatCast", size, "f")


class CastingSigned(CastingSpec):
    def __init__(self, size):
        CastingSpec.__init__(self, "@intCast", size, "i")


class CastingUnsigned(CastingSpec):
    def __init__(self, size):
        CastingSpec.__init__(self, "@intCast", size, "u")


typecast_choice_map = {
    "you sixty four": CastingUnsigned(64),
    "you thirty two": CastingUnsigned(32),
    "you eight": CastingUnsigned(8),
    "you one twenty eight": CastingUnsigned(128),
    "unsigned sixty four": CastingUnsigned(64),
    "unsigned thirty two": CastingUnsigned(32),
    "unsigned eight": CastingUnsigned(8),
    "unsigned one twenty eight": CastingUnsigned(128),
    "character": CastingUnsigned(8),
    "char": CastingUnsigned(8),
    "i sixty four": CastingSigned(64),
    "i thirty two": CastingSigned(32),
    "i eight": CastingSigned(8),
    "i one twenty eight": CastingSigned(128),
    "signed sixty four": CastingSigned(64),
    "signed thirty two": CastingSigned(32),
    "signed eight": CastingSigned(8),
    "signed one twenty eight": CastingSigned(128),
    "float thirty two": CastingFloat(32),
    "float sixty four": CastingFloat(64),
    "float one twenty eight": CastingFloat(128),
    "unsigned long": "u64",
    "long": "i64",
    "unsigned integer": "i32",
    "integer": "i32",
    "unsigned short": "u16",
    "short": "i16",
}


def typecast_choice(name="type_choice"):
    return Choice(name, typecast_choice_map)


def output_typecast(value_name, type_choice=None, is_safe=True):
    if type_choice is None:
        if value_name == "":
            command = replace_in_text("@as($, _)")
        else:
            value_name = format_value_name(value_name)
            command = replace_in_text("@as($, %s)" % value_name)
    else:
        if value_name == "":
            if is_safe:
                output_string = type_choice.get_safe_cast_expression("$")
            else:
                output_string = type_choice.get_cast_expression("$")
            command = replace_in_text(output_string)
        else:
            value_name = format_value_name(value_name)
            if is_safe:
                output_string = type_choice.get_safe_cast_expression(value_name)
            else:
                output_string = type_choice.get_cast_expression(value_name)
            command = Text(output_string)

    command.execute()


calling_convention_choice_map = {
    "see": ".C",
    "standard": ".Stdcall",
    "naked": ".Naked",
    "asynchronous": ".Async",
}


def calling_convention_choice(name="calling_convention"):
    return Choice(name, calling_convention_choice_map)


def output_calling_convention(calling_convention=None):
    if calling_convention is None:
        command = replace_in_text("callconv($)")
    else:
        command = Text("callconv(%s)" % calling_convention)
    command.execute()


library_choice_map = {
    "memory": "mem",
    "standard memory": "std.mem",
    "dynamic memory": "heap",
    "standard dynamic memory": "std.heap",
    "file system": "fs",
    "standard file system": "std.fs",
    "standard": "std",
}


def library_choice(name="library"):
    return Choice(name, library_choice_map)


def output_library(library=None):
    if library is not None:
        Text(library).execute()


def format_index(index):
    index_string = list(str(index))
    index_string.reverse()
    chunks = wrap("".join(index_string), 3)
    chunks.reverse()
    reversed_chunks = []
    for c in chunks:
        chunk_list = list(c)
        chunk_list.reverse()
        reversed_chunks.append("".join(chunk_list))
    result = "_".join(reversed_chunks)

    return result


def output_index(value_name, start=None, end=None, rest=False):
    value_name = format_value_name(value_name)
    if start is None and end is None:
        command = replace_in_text("%s[$]" % value_name)
    elif start is None:
        formatted_end = format_index(end)
        command = Text("%s[0..%s]" % (value_name, formatted_end))
    elif end is None:
        if rest:
            formatted_start = format_index(start)
            command = Text("%s[%s..]" % (value_name, formatted_start))
        else:
            formatted_start = format_index(start)
            command = Text("%s[%s]" % (value_name, formatted_start))
    else:
        formatted_start = format_index(start)
        formatted_end = format_index(end)
        command = Text("%s[%s..%s]" % (value_name, formatted_start, formatted_end))

    command.execute()


def output_method_call(function_name, value_name, with_try=False):
    function_name = format_function_name(function_name)
    value_name = format_value_name(value_name)
    command_text = "try " if with_try else ""

    if function_name == "" and value_name == "":
        command_text += "$._()"
        command = replace_in_text(command_text)
    elif function_name == "":
        command_text += "%s." % value_name
        command = Text(command_text)
    elif value_name == "":
        command_text += "$.%s()" % function_name
        command = replace_in_text(command_text)
    else:
        command_text += "%s.%s()" % (value_name, function_name)
        command = Text(command_text)

    command.execute()


def output_function_call(function_name, value_name, with_try=False):
    function_name = format_function_name(function_name)
    value_name = format_value_name(value_name)
    command_text = "try " if with_try else ""

    if function_name == "" and value_name == "":
        command_text += "$(_)"
        command = replace_in_text(command_text)
    elif function_name == "":
        command_text += "$(%s)" % value_name
        command = replace_in_text(command_text)
    elif value_name == "":
        command_text += "%s($)" % function_name
        command = replace_in_text(command_text)
    else:
        command_text += "%s(%s)" % (function_name, value_name)
        command = Text(command_text)

    command.execute()


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


def output_zig_build(build_target_name=None, gnu=False, optimization=None, run=False):
    libc_spec = "-gnu" if gnu else ""
    running = "run " if run else ""

    command_output = "zig build %s" % running
    if build_target_name is not None:
        command_output = "zig build %s-Dtarget=native-%s%s" % (
            running, build_target_name, libc_spec)
    elif gnu:
        command_output = "zig build %s-Dtarget=native-native-gnu" % running

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


initialization_type_choice_map = {
    "executable": "exe",
    "binary": "exe",
    "library": "lib",
    "lib": "lib",
}


def initialization_type_choice(name="initialization_type"):
    return Choice(name, initialization_type_choice_map)


def output_zig_initialization(initialization_type=None):
    if initialization_type is not None:
        Text("zig init-%s" % initialization_type).execute()


def output_using_namespace(visibility_attribute=None):
    visibility_prefix = "%s " % visibility_attribute if visibility_attribute is not None else ""

    Text("%susingnamespace " % visibility_prefix).execute()


def output_return(value_name):
    execute_with_dictation(
        value_name,
        lambda n: Text("return %s;" % format_value_name(n)),
        lambda n: replace_in_text("return $;")
    )


class ZigUtilities(MappingRule):
    mapping = {
        # control flow
        "if [<value_name>]": Function(output_if, construct="if"),
        "if [<value_name>] is <comparison>": Function(output_if_comparison, construct="if"),
        "unpack [<value_name>] [into <binding_name>]": Function(output_unpack_if),

        "else if [<value_name>]": Function(output_if, construct="else if"),
        "else if [<value_name>] is <comparison>": Function(output_if_comparison,
                                                           construct="else if"),

        "for loop [over <value_name>] [binding <binding_name>]": Function(output_for_loop),
        "while [<value_name>]": Function(output_while_loop, binding_name=None),
        "binding [<binding_name>] while [<value_name>] ": Function(output_while_loop,
                                                                   binding_name="_"),
        "switch [on <value_name>]": Function(output_switch),

        # logic checks
        "check [<value_name>] is <comparison>": Function(output_comparison),

        # value and function definitions
        "constant [<value_name>] [of type <type_name>]": Function(output_constant),
        "variable [<value_name>] [of type <type_name>]": Function(output_variable),
        "variable [<value_name>] [of type <type_name>] is undefined": Function(output_variable,
                                                                               is_undefined=True),
        "test [<test_name>]": Function(output_test),
        "[<visibility_attribute>] function [<function_name>] [returning <type_name>]":
            Function(output_function),
        "(call|calling) convention [<calling_convention>]": Function(output_calling_convention),

        # type definitions
        "struct [<type_name>]": Function(output_type_definition, definition_type="struct"),
        "union [<type_name>]": Function(output_type_definition, definition_type="union(enum)"),
        "enumeration [<type_name>]": Function(output_type_definition, definition_type="enum"),

        # assignment
        "[<value_name>] equals": Function(output_binding),
        "pointer [<value_name>] equals": Function(output_binding, is_pointer=True),

        # type casts / conversions
        "cast [<value_name>] [into <type_choice>]": Function(output_typecast, is_safe=False),
        "[<value_name>] as [<type_choice>]": Function(output_typecast),

        # calling methods and functions
        "method [<function_name>] [on <value_name>]": Function(output_method_call),
        "call [<function_name>] [on <value_name>]": Function(output_function_call),
        "try method [<function_name>] [on <value_name>]": Function(output_method_call,
                                                                   with_try=True),
        "try call [<function_name>] [on <value_name>]": Function(output_function_call,
                                                                 with_try=True),

        # indexing into slices and arrays
        "index [<start>] [to <end>]": Function(output_index),
        "index [<start>] onwards": Function(output_index, rest=True),
        "indexing [<start>] [to <end>] into <value_name>": Function(output_index),
        "indexing [<start>] onwards into <value_name>": Function(output_index, rest=True),

        # miscellaneous conveniences
        "[<visibility_attribute>] using namespace": Function(output_using_namespace),
        "import": replace_in_text("const $ = @import(\"_\");"),
        "[<comment_type>] comment [<comment>]": Function(output_comment),
        "documentation comment [<comment>]": Function(output_comment, comment_type="documentation"),
        "(library|lib) <library>": Function(output_library),
        "return [<value_name>]": Function(output_return),

        # keyword conveniences
        "compile time": Text("comptime "),
        "public": Text("pub "),
        "external": Text("extern "),
        "a sink": Text("async "),
        "await": Text("await "),
        "try": Text("try "),
        "catch": Text("catch "),
        "defer": Text("defer "),
        "see import": replace_in_text("@cImport({$});"),
        "see define": replace_in_text("@cDefine($);"),
        "see include": replace_in_text("@cInclude($);"),
        "arrow": Text(" => "),
        "pointer": Text("ptr"),

        # terminal commands
        "zig build [<optimization>] [for <build_target_name>]": Function(output_zig_build,
                                                                         gnu=False),
        "zig build [<optimization>] [for <build_target_name>] with (freedom|fascism)":
            Function(output_zig_build, gnu=True),
        "zig build run [<optimization>] [for <build_target_name>]": Function(output_zig_build,
                                                                             gnu=False, run=True),
        "zig build run [<optimization>] [for <build_target_name>] with (freedom|fascism)":
            Function(output_zig_build, gnu=True, run=True),
        "zig (in it|initialize) <initialization_type>": Function(output_zig_initialization),
    }

    extras = [
        Dictation("test_name", default=""),
        Dictation("value_name", default=""),
        Dictation("type_name", default=""),
        Dictation("function_name", default=""),
        Dictation("binding_name", default=None),
        Dictation("comment", default=""),
        comment_choice("comment_type"),
        comparison_choice("comparison"),
        visibility_attribute_choice("visibility_attribute"),
        typecast_choice("type_choice"),
        calling_convention_choice("calling_convention"),
        library_choice("library"),
        IntegerRef("start", 0, 10000000),
        IntegerRef("end", 0, 10000000),
        build_target_name_choice("build_target_name"),
        optimization_choice("optimization"),
        initialization_type_choice("initialization_type"),
    ]


# The main Zig grammar rules are activated here
zigBootstrap = Grammar("zig bootstrap")
zigBootstrap.add_rule(ZigEnabler())
zigBootstrap.load()

zigGrammar = Grammar("zig grammar")
zigGrammar.add_rule(ZigUtilities())
zigGrammar.add_rule(ZigDisabler())
zigGrammar.load()
zigGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global zigGrammar
    if zigGrammar:
        zigGrammar.unload()
    zigGrammar = None
