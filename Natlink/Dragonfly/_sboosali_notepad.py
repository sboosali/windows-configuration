
#================================================#

from dragonfly import (Grammar, AppContext, MappingRule, Dictation,)
from dragonfly import (Key, Text, BringApp, Function, Playback,)

#------------------------------------------------#

import types

#================================================#



#================================================#

# Voice command rule combining spoken forms and action execution.
class NotepadRule(MappingRule):
    # Define the commands and the actions they execute.
    mapping = {
        "save [file]":            Key("c-s"),
        "save [file] as":         Key("a-f, a/20"),
        "save [file] as <text>":  Key("a-f, a/20") + Text("%(text)s"),
        "find <text>":            Key("c-f/20") + Text("%(text)s\n"),
    }

    # Define the extras list of Dragonfly elements which are available
    # to be used in mapping specs and actions.
    extras = [
        Dictation("text")
    ]

#================================================#

context = AppContext(executable="notepad")
grammar = Grammar("sboosali Notepad", context=context)
grammar.add_rule(NotepadRule())
grammar.load()

#================================================#
