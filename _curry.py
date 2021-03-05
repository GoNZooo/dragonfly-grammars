from dragonfly import (Grammar, CompoundRule, Text, MappingRule, Dictation, Function, Choice)
from macro_utilities import (replace_in_text, comment_choice)
from vim.rules.letter import (camel_case, proper)


class CurryEnabler(CompoundRule):
    spec = "enable Curry"

    def _process_recognition(self, node, extras):
        curryBootstrap.disable()
        curryGrammar.enable()
        print("Curry grammar enabled!")


class CurryDisabler(CompoundRule):
    spec = "disable Curry"

    def _process_recognition(self, node, extras):
        curryGrammar.disable()
        curryBootstrap.enable()
        print("Curry grammar disabled")


def dictation_to_identifier(dictation):
    return camel_case(str(dictation).lower())


def output_bind(name):
    if name == "":
        command = replace_in_text("$ <- _")
    else:
        name = dictation_to_identifier(name)
        command = replace_in_text("%s <- $" % name)
    command.execute()


def output_let(name):
    if name == "":
        command = replace_in_text("let $ = _")
    else:
        name = dictation_to_identifier(name)
        command = replace_in_text("let %s = $" % name)
    command.execute()


def output_case(name):
    if name == "":
        command = replace_in_text("case $ of")
    else:
        name = dictation_to_identifier(name)
        command = Text("case %s of" % name)
    command.execute()


def output_if(name):
    if name == "":
        command = replace_in_text("if $ then _ else _")
    else:
        name = dictation_to_identifier(name)
        command = replace_in_text("if %s then $ else _" % name)
    command.execute()


def output_type_signature(name):
    if name == "":
        command = replace_in_text("$ :: _")
    else:
        name = dictation_to_identifier(name)
        command = replace_in_text("%s :: $" % name)
    command.execute()


def format_module_name(module_name):
    module_name = str(module_name)
    components = module_name.split(".")
    formatted_components = []
    for component in components:
        formatted_components.append(proper(component))

    return ".".join(formatted_components)


def output_import(import_name):
    if import_name == "":
        command = replace_in_text("import $ (_)")
    else:
        import_name = format_module_name(import_name)
        command = replace_in_text("import %s ($)" % import_name)
    command.execute()


def output_import_qualified(import_name):
    if import_name == "":
        command = replace_in_text("import qualified $ as _")
    else:
        import_name = format_module_name(import_name)
        command = replace_in_text("import qualified %s as $" % import_name)
    command.execute()


def output_import_as(import_name):
    if import_name == "":
        command = replace_in_text("import $ as _")
    else:
        import_name = format_module_name(import_name)
        command = replace_in_text("import %s as $" % import_name)
    command.execute()


def output_binding(name):
    if name == "":
        command = replace_in_text("$ = _")
    else:
        name = dictation_to_identifier(name)
        command = Text("%s = " % name)
    command.execute()


def output_if_equal(name):
    output_if_comparison("==", name)


def output_if_not_equal(name):
    output_if_comparison("/=", name)


def output_if_comparison(comparison, name):
    if name == "":
        command = replace_in_text("if $ %s _ then _ else _" % comparison)
    else:
        name = dictation_to_identifier(name)
        command = replace_in_text("if %s %s $ then _ else _" % (name, comparison))
    command.execute()


def output_check_equal(name):
    output_check_comparison("==", name)


def output_check_not_equal(name):
    output_check_comparison("/=", name)


def output_check_comparison(comparison, name):
    if name == "":
        command = replace_in_text("$ %s _" % comparison)
    else:
        name = dictation_to_identifier(name)
        command = replace_in_text("%s %s $" % (name, comparison))
    command.execute()


def output_data_type(type_name):
    if type_name == "":
        command = replace_in_text("data $ =")
    else:
        type_name = dictation_to_type_name(type_name)
        command = Text("data %s = " % type_name)
    command.execute()


def dictation_to_type_name(name):
    return proper(str(name).replace("-", ""))


def output_new_type(type_name, new_type_base):
    if type_name == "" and new_type_base == "":
        command = replace_in_text("newtype $ = _")
    elif type_name == "":
        new_type_base = dictation_to_type_name(new_type_base)
        command = replace_in_text("newtype $ = _ %s" % new_type_base)
    elif new_type_base == "":
        type_name = dictation_to_type_name(type_name)
        command = Text("newtype %s = %s " % (type_name, type_name))
    else:
        type_name = dictation_to_type_name(type_name)
        new_type_base = dictation_to_type_name(new_type_base)
        command = Text("newtype %s = %s %s" % (type_name, type_name, new_type_base))
    command.execute()


def output_wrapped_type(type_name, new_type_base):
    if type_name == "" and new_type_base == "":
        command = replace_in_text("type $ = Wrapped \"_\" _")
    elif type_name == "":
        new_type_base = dictation_to_type_name(new_type_base)
        command = replace_in_text("type $ = Wrapped \"_\" %s" % new_type_base)
    elif new_type_base == "":
        type_name = dictation_to_type_name(type_name)
        command = Text("type %s = Wrapped \"%s\" " % (type_name, type_name))
    else:
        type_name = dictation_to_type_name(type_name)
        new_type_base = dictation_to_type_name(new_type_base)
        command = Text("type %s = Wrapped \"%s\" %s" % (type_name, type_name, new_type_base))
    command.execute()


def output_language_extension(language_extension):
    Text("{-# LANGUAGE %s #-}" % proper(str(language_extension))).execute()


def output_comment(comment, comment_type=None):
    if comment_type is None:
        command = Text("-- %s" % comment)
    else:
        command = Text("-- %s %s" % (comment_type, comment))
    command.execute()


stack_command_choice_map = {
    "build fast": "build --fast",
    "build": "build",
    "shell": "repl",
    "shall": "repl",
    "test": "test",
    "test fast": "test --fast",
    "run": "run",
    "install": "install",
}


def stack_command_choice(name="stack_command"):
    return Choice(name, stack_command_choice_map)


def output_stack_command(stack_command=None):
    command_text = "stack "
    if stack_command is None:
        command = Text(command_text)
    else:
        command = Text(command_text + str(stack_command))
    command.execute()


class CurryUtilities(MappingRule):
    mapping = {
        "if [<name>]": Function(output_if),
        "if [<name>] is equal": Function(output_if_equal),
        "if [<name>] is not equal": Function(output_if_not_equal),
        "case [on <name>]": Function(output_case),
        "let [<name>]": Function(output_let),
        "anonymous function": replace_in_text("\\$ -> _"),
        "signature [for <name>]": Function(output_type_signature),
        "import [<import_name>]": Function(output_import),
        "import qualified [<import_name>]": Function(output_import_qualified),
        "import [<import_name>] as": Function(output_import_as),
        "qualified pure script import": replace_in_text("import $ as _"),
        "check [<name>] is equal": Function(output_check_equal),
        "check [<name>] is not equal": Function(output_check_not_equal),
        "map": Text(" <$> "),
        "apply": Text(" <*> "),
        "operator bind": Text(" >>= "),
        "discard": Text(" >> "),
        "[<name>] equals": Function(output_binding),
        "bind [to <name>]": Function(output_bind),
        "backwards arrow": Text(" <- "),
        "backwards fat arrow": Text(" <= "),
        "arrow": Text(" -> "),
        "fat arrow": Text(" => "),
        "monad reader": Text("MonadReader e m"),
        "monad IO": Text("MonadIO m"),
        "monad state": Text("MonadState s m"),
        "data type [<type_name>]": Function(output_data_type),
        "new type [<new_type_base>] is called [<type_name>]": Function(output_new_type),
        "wrapped [<new_type_base>] is called [<type_name>]": Function(output_wrapped_type),
        "language extension <language_extension>": Function(output_language_extension),
        "[<comment_type>] comment [<comment>]": Function(output_comment),

        # terminal commands
        "stack [<stack_command>]": Function(output_stack_command),
    }

    extras = [
        Dictation("name", default=""),
        Dictation("comment", default=""),
        Dictation("type_name", default=""),
        Dictation("new_type_base", default=""),
        Dictation("import_name", default=""),
        Dictation("language_extension", default=""),
        comment_choice("comment_type"),
        stack_command_choice("stack_command"),
    ]


# The main Curry grammar rules are activated here
curryBootstrap = Grammar("curry bootstrap")
curryBootstrap.add_rule(CurryEnabler())
curryBootstrap.load()

curryGrammar = Grammar("curry grammar")
curryGrammar.add_rule(CurryUtilities())
curryGrammar.add_rule(CurryDisabler())
curryGrammar.load()
curryGrammar.disable()


def unload():
    global curryGrammar
    if curryGrammar:
        curryGrammar.unload()
    curryGrammar = None
