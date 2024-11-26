
#================================================#

from dragonfly import (Grammar, AppContext, MappingRule, Dictation,)
from dragonfly import (Key, Text, BringApp, Function, Playback,)

#------------------------------------------------#

#import types

#================================================#



#================================================#

class NotepadRule(MappingRule):

    mapping = {
        "save [file]":            Key("c-s"),
        "save [file] as":         Key("a-f, a/20"),
        "save [file] as <text>":  Key("a-f, a/20") + Text("%(text)s"),
        "find <text>":            Key("c-f/20") + Text("%(text)s\n"),
    }

    extras = [
        Dictation("text")
    ]

#------------------------------------------------#

context = AppContext(executable="notepad")
grammar = Grammar("sboosali Notepad", context=context)
grammar.add_rule(NotepadRule())
grammar.load()

#================================================#