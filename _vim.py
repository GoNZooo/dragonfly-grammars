from dragonfly import (Grammar, CompoundRule, AppContext, MappingRule, Text, Choice, Function)

from vim.rules.letter import LetterSequenceRule


class VimEnabler(CompoundRule):
    spec = "Enable fancy"

    def _process_recognition(self, node, extras):
        VimGrammar.enable()
        print("### vim grammar enabled ###")


class VimDisabler(CompoundRule):
    spec = "Disable fancy"

    def _process_recognition(self, node, extras):
        VimGrammar.disable()
        print("### vim grammar disabled ###")


buffer_command_choice_map = {
    "write": "w",
    "close": "q",
    "write and close": "wq",
    "force close": "q!",
    "delete": "bd",
}


def buffer_command_choice(name="buffer_command"):
    return Choice(name, buffer_command_choice_map)


def output_buffer_command(buffer_command=None):
    if buffer_command is not None:
        Text(":%s\n" % buffer_command).execute()


fugitive_command_choice_map = {
    "commit": "Gcommit",
    "status": "Gstatus",
    "stage": "Gwrite",
    "push": "Gpush",
    "abort commit": "q!",
    "finish commit": "wq",
}


def fugitive_command_choice(name="fugitive_command"):
    return Choice(name, fugitive_command_choice_map)


def output_fugitive_command(fugitive_command=None):
    if fugitive_command is not None:
        Text(":%s\n" % fugitive_command).execute()


gitgutter_command_choice_map = {
    "stage": " hs",
    "next": "]c",
    "previous": "[c",
    "preview": " hp",
    "undo": " hu",
}


def gitgutter_command_choice(name="gitgutter_command"):
    return Choice(name, gitgutter_command_choice_map)


def output_gitgutter_command(gitgutter_command=None):
    if gitgutter_command is not None:
        Text("%s" % gitgutter_command).execute()


class VimUtilities(MappingRule):
    mapping = {
        # general
        "<buffer_command> buffer": Function(output_buffer_command),

        # `tpope/vim-fugitive`
        "(fugitive|pope) <fugitive_command>": Function(output_fugitive_command),

        # `airblade/vim-gitgutter`
        "<gitgutter_command> hunk": Function(output_gitgutter_command),
    }

    extras = [
        fugitive_command_choice("fugitive_command"),
        gitgutter_command_choice("gitgutter_command"),
        buffer_command_choice("buffer_command"),
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
clion_context = AppContext(executable="clion64")
goland_context = AppContext(executable="goland64")
pycharm_context = AppContext(executable="pycharm64")
webstorm_context = AppContext(executable="webstorm64")
total_commander_context = AppContext(executable="TOTALCMD64")
vim_context = (code_context | firefox_context | terminal_preview_context | discord_context |
               powerbash_context | graphical_neovim_context | skype_context | ripcord_context |
               edge_context | slack_context | hexchat_context | clion_context | goland_context |
               pycharm_context | webstorm_context | total_commander_context)

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


def unload():
    global VimGrammar
    if VimGrammar:
        VimGrammar.unload()
    VimGrammar = None
