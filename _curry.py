from dragonfly import (Grammar, CompoundRule, Text, MappingRule)
from macro_utilities import (replace_percentage)


class CurryEnabler(CompoundRule):
    spec = "enable Curry"

    def _process_recognition(self, node, extras):
        curryBootstrap.disable()
        curryGrammar.enable()
        print "Curry grammar enabled!"


class CurryDisabler(CompoundRule):
    spec = "disable Curry"

    def _process_recognition(self, node, extras):
        curryGrammar.disable()
        curryBootstrap.enable()
        print "Curry grammar disabled"


class CurryUtilities(MappingRule):
    mapping = {
        "if": Text("if %% then _ else _") + replace_percentage(15),
        "case": Text("case %% of") + replace_percentage(15),
        "let": Text("let %% = _ in") + replace_percentage(15),
        "anonymous function": Text("\\%% -> _") + replace_percentage(15),
        "type signature": Text("%% :: _") + replace_percentage(15),
        "import": Text("import %% (_)") + replace_percentage(15),
        "qualified Haskell import": Text("import qualified %% as _") + replace_percentage(15),
        "qualified pure script import": Text("import %% as _") + replace_percentage(15),
        "check equal": Text(" == "),
        "check not equal": Text(" != "),
        "map": Text(" <$> "),
        "apply": Text(" <*> "),
        "bind": Text(" >>= "),
        "discard": Text(" >> "),
        "equals": Text(" = "),
        "backwards arrow": Text(" <- "),
        "backwards fat arrow": Text(" <= "),
        "arrow": Text(" -> "),
        "fat arrow": Text(" => "),
        "monad reader": Text("MonadReader e m"),
        "monad IO": Text("MonadIO m"),
        "monad state": Text("MonadState s m"),
        "define data type": Text("data %% =") + replace_percentage(15),
        "define new type": Text("newtype %% =") + replace_percentage(15),
    }

    extras = []


# The main Curry grammar rules are activated here
curryBootstrap = Grammar("curry bootstrap")
curryBootstrap.add_rule(CurryEnabler())
curryBootstrap.load()

curryGrammar = Grammar("curry grammar")
curryGrammar.add_rule(CurryUtilities())
curryGrammar.add_rule(CurryDisabler())
curryGrammar.load()
curryGrammar.disable()

# Unload function which will be called by natlink at unload time.


def unload():
    global curryGrammar
    if curryGrammar:
        curryGrammar.unload()
    curryGrammar = None
