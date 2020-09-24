from dragonfly import (Grammar, CompoundRule, AppContext, MappingRule, Text, Choice, Function)

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


fugitive_command_choice_map = {
    "commit": "Gcommit",
    "status": "Gstatus",
    "stage": "Gwrite",
    "abort": "q!",
    "finish commit": "wq",
}


def fugitive_command_choice(name="fugitive_command"):
    return Choice(name, fugitive_command_choice_map)


def output_fugitive_command(fugitive_command=None):
    if fugitive_command is not None:
        Text(":%s\n" % fugitive_command).execute()


class VimUtilities(MappingRule):
    mapping = {
        "save buffer": Text(":w\n"),
        "(fugitive|pope) <fugitive_command>": Function(output_fugitive_command),
    }

    extras = [
        fugitive_command_choice("fugitive_command")
    ]


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
VimGrammar.add_rule(VimUtilities())
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
