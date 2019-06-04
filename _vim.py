from dragonfly import (Grammar, CompoundRule, AppContext)

from vim.rules.letter import LetterSequenceRule


class VimEnabler(CompoundRule):
    spec = "Enable fancy"

    def _process_recognition(self, node, extras):
        VimGrammar.enable()
        print "### vim grammar enabled ###"


class VimDisabler(CompoundRule):
    spec = "Disable fancy"

    def _process_recognition(self, node, extras):
        VimGrammar.disable()
        print "### vim grammar disabled ###"


putty_context = AppContext(executable="putty")
code_context = AppContext(executable="code")
firefox_context = AppContext(executable="firefox")
discord_context = AppContext(executable="discord")
franz_context = AppContext(executable="Franz")
powerbash_context = AppContext(executable="powershell")
vim_context = (putty_context | code_context | firefox_context |
               discord_context | franz_context | powerbash_context)

# the bootstrapper loads the grammar
VimBootstrap = Grammar("vim bootstrap", context=vim_context)
VimBootstrap.add_rule(VimEnabler())
VimBootstrap.load()

VimGrammar = Grammar("vim grammar", context=vim_context)
VimGrammar.add_rule(LetterSequenceRule())
VimGrammar.add_rule(VimDisabler())
VimGrammar.add_rule(VimEnabler())
VimGrammar.load()
VimGrammar.enable()

# Unload function which will be called by natlink at unload time.


def unload():
    global VimGrammar
    if VimGrammar:
        VimGrammar.unload()
    VimGrammar = None
