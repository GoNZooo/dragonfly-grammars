from dragonfly import (Grammar, CompoundRule, Text, MappingRule,
                       Dictation, Function, Choice, IntegerRef)
from dragonfly.windows.clipboard import (Clipboard)
from vim.rules.letter import (barbecue, formatting_choice, format_dictation)


class DynamicConfigurationEnabler(CompoundRule):
    spec = "enable dynamic configuration"

    def _process_recognition(self, node, extras):
        dynamic_configuration_bootstrap.disable()
        dynamic_configuration_grammar.enable()
        print "dynamic configuration grammar enabled!"


class DynamicConfigurationDisabler(CompoundRule):
    spec = "disable dynamic configuration"

    def _process_recognition(self, node, extras):
        dynamic_configuration_grammar.disable()
        dynamic_configuration_bootstrap.enable()
        print "dynamic configuration grammar disabled"


sleep = 15


def get_sleep_value():
    global sleep
    return sleep


def set_sleep(sleep_value):
    global sleep
    sleep = sleep_value


def show_sleep():
    global sleep
    print("Current sleep value is: %d" % sleep)


class DynamicConfigurationUtilities(MappingRule):
    mapping = {
        "set sleep to <sleep_value>": Function(set_sleep),
        "show sleep value": Function(show_sleep),
    }

    extras = [
        IntegerRef("sleep_value", 0, 251),
    ]


# The main DynamicConfiguration grammar rules are activated here
dynamic_configuration_bootstrap = Grammar("dynamic_configuration bootstrap")
dynamic_configuration_bootstrap.add_rule(DynamicConfigurationEnabler())
dynamic_configuration_bootstrap.load()

dynamic_configuration_grammar = Grammar("dynamic_configuration grammar")
dynamic_configuration_grammar.add_rule(DynamicConfigurationUtilities())
dynamic_configuration_grammar.add_rule(DynamicConfigurationDisabler())
dynamic_configuration_grammar.load()
dynamic_configuration_grammar.enable()

# Unload function which will be called by natlink at unload time.


def unload():
    global dynamic_configuration_grammar
    if dynamic_configuration_grammar:
        dynamic_configuration_grammar.unload()
    dynamic_configuration_grammar = None
