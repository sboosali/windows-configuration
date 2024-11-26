
#================================================#

from dragonfly import (Grammar, MappingRule,)
from dragonfly import (Key, Text, Mouse, Playback,
                       BringApp, StartApp, FocusWindow, RunCommand, Function,)
from dragonfly import (Dictation, Choice, IntegerRef, Repetition,)

#================================================#

character_nicknames = {
    "(bar|vertical bar|pipe)": "|",
    "(dash|minus|hyphen)": "-",
    "(dot|period)": ".",
    "comma": ",",
    "backslash": "\\",
    "underscore": "_",
    "(star|asterisk)": "*",
    "colon": ":",
    "(semicolon|semi-colon)": ";",
    "at": "@",
    "[double] quote": '"',
    "single quote": "'",
    "hash": "#",
    "dollar": "$",
    "percent": "%",
    "and": "&",
    "slash": "/",
    "equal": "=",
    "plus": "+",
    "space": " ",
}

#------------------------------------------------#

class GlobalRule(MappingRule):
    mapping = {

        # dragon:

        "lock it":   Playback([(["go", "to", "sleep"], 0.0)]),
        "unlock it": Playback([(["wake", "up"],        0.0)]),

        # formatted insertion:

        "camel <camel_text>":       Text("%(camel_text)"),
        "class <class_text>":       Text("%(class_text)"),
        "worm  <lisp_text>":        Text("%(lisp_text)"),
        "snake <python_text>":      Text("%(python_text)"),
        "envy  <envvar_text>":      Text("%(envvar_text)"),
        "cappy <capitalized_text>": Text("%(capitalized_text)"),
        "lower <lowercased_text>":  Text("%(lowercased_text)"),
        "upper <uppercased_text>":  Text("%(uppercased_text)"),

        # file-extensions:

        "dot (pie|P Y)":       Text(".py"),
        "dot (E lisp|L)":      Text(".el"),
        "dot (haskell|H S)":   Text(".hs"),
        "dot (shell|S H)":     Text(".sh"),
        "dot (text|T X T)":    Text(".txt"),
        "dot (mark down|M D)": Text(".md"),
        "dot (rest|R S R)":    Text(".rst"),
        "dot J S":             Text(".js"),
        "dot (css|C S S)":     Text(".css"),
        "dot (html|H T M L)":  Text(".html"),

        # protocols:

        "proto H T T P S":     Text("https://"),
        "proto (git|G I T)":   Text("git://"),
        "proto (shush|S S H)": Text("ssh://"),

        # etc:

        "bring explorer": BringApp("explorer"),
        "start explorer": StartApp("explorer"),

        "shell ping": RunCommand('ping -w 4 localhost'),

        # "[use] function":              Function(my_function),

    }

    extras = [
        Dictation("text"),

        Dictation("camel_text").camel(),
        Dictation("class_text").title().replace(" ", ""),
        Dictation("lisp_text").lower().replace(" ", "-"),
        Dictation("python_text").lower().replace(" ", "_"),
        Dictation("envvar_text").upper().replace(" ", "_"),
        Dictation("capitalized_text").title(),
        Dictation("lowercased_text").lower(),
        Dictation("uppercased_text").lower(),

        # Dictation("…_text").apply(lambda s: s.…()),

        IntegerRef("n", 1, 10),
        Choice("char", character_nicknames),
    ]

    defaults = {
        "n": 1,
    }

#------------------------------------------------#

global_grammar = Grammar("Global sboosali")
global_grammar.add_rule(GlobalRule())
global_grammar.load()

#================================================#

'''


<press> exported =
  press <mods> <key>;
<mods> =
  [control] [(meta | alt)] [window] [shift];
<key> = ();


        redo = ContextAction(default=Key('c-y'), actions=[
            # Use cs-z for rstudio
            (AppContext(executable="rstudio"), Key('cs-z')),
        ])


            str_func = lambda s: s.upper()
            Dictation("formattedtext").apply(str_func)
            Dictation("snake_text").lower().replace(" ", "_")
            Dictation("camelText").camel()

        If you are using Dragon/Natlink and want the spoken form of the
        dictated words instead of the written form, this can be achieved by
        passing ``False`` when calling the ``format()`` method of the
        ``NatlinkDictationContainer`` object given as this element's value.


class ExampleRule(CompoundRule):
    spec = "do something computer"                  # Spoken form of command.
    def _process_recognition(self, node, extras):   # Callback when command is spoken.
        print("Voice command spoken.")


'''
