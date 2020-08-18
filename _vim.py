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


code_context = AppContext(executable="code")
firefox_context = AppContext(executable="firefox")
discord_context = AppContext(executable="discord")
powerbash_context = AppContext(executable="powershell")
graphical_neovim_context = AppContext(executable="nvim-qt")
terminal_preview_context = AppContext(executable="WindowsTerminal")
ripcord_context = AppContext(executable="Ripcord")
skype_context = AppContext(title="Skype")
edge_context = AppContext(executable="msedge")
slack_context = AppContext(title="Slack")
hexchat_context = AppContext(title="HexChat")
vim_context = (code_context | firefox_context | terminal_preview_context | discord_context |
               powerbash_context | graphical_neovim_context | skype_context | ripcord_context |
               edge_context | slack_context | hexchat_context)

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
