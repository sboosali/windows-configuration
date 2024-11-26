
#================================================#

from dragonfly import (Grammar, MappingRule, CompoundRule,
                       Dictation, Choice, Repetition, Alternative,
                       IntegerRef, RuleRef,)
from dragonfly import (Key, Text, Pause, Playback,  Function,)
from dragonfly import (AppContext, FuncContext, Window,)

from dragonfly.actions.action_base import (ActionSeries, ActionRepetition,)

#------------------------------------------------#

import types

from enum import Enum

import typing

import re

#================================================#

def EmacsExec_ByKeyboard(command, arguments=None):
    arguments = arguments if arguments else []

    command_action = Key("a-x") + Pause("3") + Text(command) + Key("{Enter}")

    return command_action

    # argument_actions = ActionSeries(*[ argument + Key("{Enter}" + Pause("1")) for argument in arguments ])
    # return command_action + argument_actions

#

def EmacsEval_ByKeyboard(expression):
    return Key("a-:") + Pause("3") + Text(expression) + Key("{Enter}")

#------------------------------------------------#

def EmacsExec_ByClipboard(command, arguments=None):
    arguments = arguments if arguments else []

    actions = Key("a-x") + Pause("2") + EmacsPaste(command) + Key("{Enter}")
    return actions

#

def EmacsEval_ByClipboard(expression):

    return Key("a-:") + Pause("2") + EmacsPaste(expression) + Key("{Enter}")

#

def EmacsPaste(string, delay="20"):
    return Paste(string, paste=Key(f"C-y/{delay}", use_hardware=True))

#------------------------------------------------#

def EmacsExec_ByServer(command, arguments=None):
    arguments = arguments if arguments else []
    expression = f'''"(with-current-buffer (window-buffer) (call-interactively #'{command})"'''
    return EmacsClient(expression)

#

def EmacsEval_ByServer(expression):
    expression_ = f"""'(with-current-buffer (window-buffer) {expression}'"""
    return EmacsClient(expression_)

#

def EmacsClient(elisp, wsl=False, server=None):
    shell = f"""emacsclient --eval {elisp}"""
    if wsl:
        shell = f"""wsl.exe -- emacsclient --eval {elisp}"""
    return RunCommand(shell, hide_window=True)

#
#n.b. `emacsclient --eval EXPR` calls `(server-eval-and-print)`, which wraps the `EXPR` with its own buffer, thus:
# we must kill that buffer (i.e. `(progn (kill-buffer " *server*") …)`, which is fragile;
# or we must restore `current-buffer` to the `selected-window`'s (i.e. `(with-current-buffer (window-buffer) …)`), which is more robust.
# in particular, `(with-current-buffer (window-buffer) …)` switches the `current-buffer` from `" *server*"` to the `selected-frame`'s `selected-window`'s buffer.
#
#e.g. as <M-:>, EmacsEval_ByServer("(kill-line 2)"):
#
#     emacsclient -e '(with-current-buffer (window-buffer) (kill-line 2))'
#
#e.g. as <M-x>, EmacsExec_ByServer("kill-line"):
#
#     emacsclient -e '(with-current-buffer (window-buffer) (call-interactively #'\''kill-line))'
#
#e.g. from Windows to Linux (an `(emacs-server)` within WSL), EmacsExec_ByServer("kill-line", wsl=True):
#
#     wsl.exe -- emacsclient --eval "(with-current-buffer (window-buffer) (call-interactively 'kill-line))"
#
#e.g. “`get-visible-focused-text`”, EmacsEval_ByServer(…, wsl=True):
#
#     wsl.exe -- emacsclient --eval "(with-current-buffer (window-buffer) (buffer-substring-no-properties (save-excursion (move-to-window-line +0) (point)) (save-excursion (move-to-window-line -1) (point))))"
#
#n.b. `emacsclient`:
# -e --eval=EXPRESSION
# -f --server-file=SERVER-FILE
# -s --socket-name=SERVER-NAME
# -n --no-wait
#
#n.b. `'…'\''…'` escapes a single-apostrophe within bash. (TODO works in other non-bash *nix shells?)
#
# 

#------------------------------------------------#

EmacsExec_ByDefault = EmacsExec_ByKeyboard

EmacsEval_ByDefault = EmacsEval_ByKeyboard

#

def EmacsExec(command, arguments=None, use_keyboard=False, use_clipboard=False, use_emacsclient=False):

    '''
    NB. ``arguments`` may be different for ``EmacsExec_ByServer`` than ``EmacsExec_ByKeyboard`` or ``EmacsExec_ByClipboard``
    (though ``command`` can still be identical, given the idiomatic naming conventions for Emacs commands).
    '''

    if   use_keyboard:
        return EmacsExec_ByKeyboard(command, arguments)
    elif use_clipboard:
        return EmacsExec_ByClipboard(command, arguments)
    elif use_emacsclient:
        return EmacsExec_ByServer(command, arguments)
    else:
        return EmacsExec_ByDefault(command, arguments)

    #TODO make sure `command` parses as a valid elisp symbol.

#

def EmacsEval(expression, use_keyboard=False, use_clipboard=False, use_emacsclient=False):

    if   use_keyboard:
        return EmacsEval_ByKeyboard(expression)
    elif use_clipboard:
        return EmacsEval_ByClipboard(expression)
    elif use_emacsclient:
        return EmacsEval_ByServer(expression)
    else:
        return EmacsEval_ByDefault(expression)

#================================================#

''' Whitelist of Emacs-commands to recognize, with optional pronunciation.

* Singletons: hyphenated superwords are automatically pronounced as the sequence of subwords.
* Pairs: The left/first string is the custom pronunciation (space-separated subwords).

For example, ``"list-buffers"`` is the same as ``(list buffer", "list-buffers")``.
'''

emacs_commands = [  #: list[str | (str,str)] = [

  # "…",
  # "…",

  # ("…", "…")
  # ("…", "…")

]

#------------------------------------------------#

emacs_vocabulary = {  # : dict[str, [str | list[str]]] = {

  "defun": ["Dee fun", "duh fun"],

  # "…": ["…"],
  # "…": ["…"],

}

#================================================#

class EmacsRule(MappingRule):

    mapping = {

        # Insertion:

        "fun <lisp_text>":       Text("%(lisp_text)"),
        "var <upper_lisp_text>": Text("%(upper_lisp_text)"),
        # "(fun  | var)   <lisp_text>": Text("…"),
        # "(type | class) <lisp_text>": Text("…"),

        # Everywhere:

        "quit it": Key("c-g"),

        "undo [<n>]": Key("c-_:%(n)d"),  # or "undo undo undo …"

        "guess": Key("c-a-i"),  #= EmacsExec("completion-at-point")

        "mark [it]": Key("c-@"),  #= EmacsExec("set-mark-command")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # "…": Key("c-"),  #= EmacsExec("…")

        # Find/Replace

        "find [next]":       Key("c-s"),       #= EmacsExec("isearch-forward")
        "find  back":        Key("c-r"),       #= EmacsExec("isearch-backward")
        "find this":         Key("a-s, a-."),  #= EmacsExec("isearch-forward-thing-at-point")
        # "find (this | sim)": Key("c-s") + Key("c-a-s"),  #= EmacsExec("isearch-yank-symbol-or-char")
        # "find word":         Key("c-s") + Key("c-w"),  #= EmacsExec("isearch-yank-word-or-char")
        "find Rx":           Key("c-a-s"),  #= EmacsExec("isearch-forward-regexp")
        "find <text>":       Key("c-s") + Text("%(text)"),

        "replace":        Key("a-%"),  #= EmacsExec("query-replace")
        "replace Rx":     Key("c-a-%"),  #= EmacsExec("query-replace-regexp")
        "replace all":    EmacsExec("replace-string"),
        "replace <text>": Key("a-%") + Text("%(text)"),

        # Files:

        "open file": Key("c-x, c-f"),
        "open file [<text>]": Key("c-x, c-f") + Text("%(text)") + Key("{Enter}"),

        "open dear": EmacsExec("dired"),

        # Buffers:

        "show buffs": Key("c-x c-b"),

        "open buff": Key("c-x b"),
        "open buff [<text>]": Key("c-x b") + Text("%(text)") + Key("{Enter}"),

        "switch [<text>]": Key("c-x b") + Text("%(text)"),  # + Key("{Enter}")
        # ^     TODO: switch to old buffer or make new buffer:

        "kill buff": Key("c-x, k, enter"),
        "bury buff": EmacsExec("bury-buffer"),

        # Windows:

        "other win": Key("c-x o"),
        "left win": EmacsExec("windmove-left"),
        "right win": EmacsExec("windmove-right"), 
        "up win": EmacsExec("windmove-up"),
        "down win": EmacsExec("windmove-down"),

        "close other win": EmacsExec("delete-other-windows"),
        "vertical   win":  EmacsExec("split-window-right"),
        "horizontal win":  EmacsExec("split-window-below"),

        # :

        # "…": Key("…"),

        # Moving:

        "beg line": Key("c-a"),
        "end line": Key("c-e"),

        "word": Key("a-b:%(n)d"),
        "word": Key("a-f:%(n)d, a-f, a-b"),

        "term": Key("ca-b:%(n)d"),
        "term": Key("ca-f:%(n)d, ca-f, ca-b"),

        # "fun": Key(":%(n)d"),
        # "fun": Key(":%(n)d"),

        "left  [<n>] char": Key("c-b:%(n)d"),
        "right [<n>] char": Key("c-f:%(n)d"),
        "up    [<n>] char": Key("c-p:%(n)d"),
        "down  [<n>] char": Key("c-n:%(n)d"),

        # "go to line <n>": EmacsEval("(goto-line %(n)d)"),

        # Editing:

        "sell line": Key("c-g") + Key("c-a, c-{space}, c-e, c-f"),

        "sell buff": Key("c-x h"),  #= EmacsExec("mark-whole-buffer")

        "char": Key("backspace:%(n)d"),
        "char": Key("c-d:%(n)d"),
        "word": Key("a-backspace:%(n)d"),
        "word": Key("a-d:%(n)d"),
        "char": Key("c-d:%(n)d"),
        "kill [<n>]       (line|lines)": Key("c-k:%(n)d"),
        "kill [<n>] whole (line|lines)": Key("c-a, c-k:%(n)d"),
        "term": Key("c-a-k:%(n)d"),

        # prog-mode:

        "show ref": Key("a-?"),   #= EmacsExec("xref-list-references") TODO
        "show deaf": Key("a-."),  #= EmacsExec("xref-find-definitions")

        # "jump deaf": Key(""),  #= EmacsExec("")

        # elisp-mode:

        "E Val that": Key("c-x c-e"),  #= EmacsExec("eval-last-sexp")
        "E Val fun": EmacsExec("eval-defun"),
        "E Val buff": EmacsExec("eval-buffer"),

        # # more bindings:

        # "…": Key("…"),

        # # more commands:

        # "…": EmacsExec("…"),

        # # more expressions:

        # "…": EmacsEval("…"),

    }

    extras = [
        Dictation("text"),
        Dictation("lisp_text").lower().replace(" ", "-"),
        Dictation("upper_lisp_text").upper().replace(" ", "-"),

        IntegerRef("n",  1, 10),
        IntegerRef("nn", 1, 100),
    ]

    defaults = {
        "n": 1,
    }

#

emacs_rule    = EmacsRule()
emacs_context = AppContext(executable="emacs")

emacs_grammar = Grammar("Emacs sboosali", context=emacs_context)
emacs_grammar.add_rule(emacs_rule)

#------------------------------------------------#



# #------------------------------------------------#

# pronunciations: dict[str,str] = {

#   "Dee fun": "defun",
#   "…": "…",
#   "…": "…",
#   "…": "…",

# }

# def pronounce(written: str) -> str:
#     spoken = pronunciations.get(written, written)
#     return spoken

# #

# emacs_visible_list = DictList("Emacs Visible-Words sboosali")

# def update_visible_words(visible_words):
#     emacs_visible_list.clear()
#     return emacs_visible_list.update({ pronounce(written) : written for written in visible_words })

#------------------------------------------------#

# def emacs_get_visible_focused_text(wsl=False):
#     ''' Get the selected-window's buffer-contents (via emacsclient).
#     '''

#     elisp = "(with-current-buffer (window-buffer) (buffer-substring-no-properties (save-excursion (move-to-window-line +0) (point)) (save-excursion (move-to-window-line -1) (point))))"

#     wsl_exe = "wsl.exe -- " if wsl else ""
#     emacsclient_exe = f'''{wsl_exe}emacsclient --eval "{elisp}"'''
#     dragonfly_exe = RunCommand(emacsclient_exe, synchronous=True, hide_window=True, process_command=(lambda self proc: proc.stdout.read()))

#     lines = dragonfly_exe.run()
#     return lines

# #

# def emacs_get_visible_focused_speakable_words(wsl=False):
#     ''' Parse recognizable phrases (for Dragon) from text that's currently-visible (in Emacs).
#     '''

#     lines = emacs_get_visible_focused_text(wsl=wsl)
#     words = emacs_parse_lines_into_speakable_words(lines)
#     return words

# #

# def emacs_parse_lines_into_speakable_words(lines):
#     ''' Parse recognizable phrases (for Dragon) from text that's currently-visible (in Emacs).

#     Cased identifiers (like ``json-parse``, ``json_parse``, or ``JsonParser``) are recognized if spoken in full. (They're split into words for recognizability, and grouped together as a "multi-word" for accuracy).
#     For example, given the elisp ``(json-read (or FILE json-file))``, we can say "jason read" or "jason file" (which are returned as "json-read" or "json-file", resp.), and the phrase "read file" or word "read" won't be recognized (which could interfere with recognition accuracy/efficiency) while the word "file" itself still will be (returned as "FILE").
#     '''

#     words = ( for to_spoken_word(subword) for subword in (to_sub_words(token).join(' ') for token in (line for line in lines))))

#     # re.sub(r'[:symbol:]+', " ", …)
#     # re.split(r'[ ]+', …)
#     # list(itertools.chain.from_iterable()

#     return words

# #

# def to_sub_words(superword):
#     ''' “Uncaae” a (snakecased/dashcased/camelcased/etc) superword into its subwords.

#     >>>to_sub_words("read-file")
#     ["read", "file"]
#     >>>to_sub_words("read_file")
#     ["read", "file"]
#     >>>to_sub_words("readFile")
#     ["read", "file"]
#     >>>to_sub_words("Read.File")
#     ["read", "file"]
#     >>>to_sub_words("Read/File.TXT")
#     ["read", "file", "txt"]
#     '''

#     subwords = re.split(r'[-_./]', superword)
#     subwords = [word for word in subwords]

#     return subwords

# #

# def to_spoken_word(word):
#     ''' “Pronounce” a known jargon/abbreviation/etc token as homophobes or letters (space-separated).

#     '''

#     subwords = re.split(r'[]', superword)
#     subwords = [subwords for subword in re.split(r'[:upper:]', word) for word in subwords]

#     return subwords

#------------------------------------------------#

# class EmacsSelectRule(MappingRule):

#       '''NB. uses personal keybinding for custom ‘sboo-isearch-outwards-visible’ command that: only searches for visible words on screen, (through a region narrowed to the selected-window's current-buffer); searches "outwards" from point (not just forwards or backwards), prioritizing the nearest match, while highlighting the rest; and if search fails, tries to search for phonetically-similar words.
#     '''

#     mapping = {

#         "select <phrase>": Key("c-a-s") + Text("%(phrase)"),

#         "select <first_word> through <last_word>": ,

#         "jump      before <word>": ,
#         "jump      after  <word>": ,
#         "jump up   before <word>": ,
#         "jump up   after  <word>": ,
#         "jump down before <word>": ,
#         "jump down after  <word>": ,

#     }

#     extras = [
#         DictListRef("word",       emacs_visible_list),
#         DictListRef("first_word", emacs_visible_list),
#         DictListRef("last_word",  emacs_visible_list),

#         DictListRef("phrase", Repetition(emacs_visible_list, min=1, max=5)),
#     ]

# #

# emacs_select_rule    = EmacsSelectRule()
# emacs_select_context = AppContext(executable="emacs")

# emacs_select_grammar = Grammar("Emacs Select-n-Say sboosali", context=emacs_context)
# emacs_select_grammar.add_rule(emacs_select_rule)
# grammar.add_list(emacs_visible_list)

# #------------------------------------------------#

# class EmacsShellRule(MappingRule):

#     mapping = {
#         "go up": Text("cd ..") + Key("{Enter}"),
#         "go up <n>": Modifier(Text("%(n)"), lambda n: p = '../' * n; f'cd ../{p}')) + Key("{Enter}"),

#   Folder <folder> = "cd $1" {Ctrl+a}{Alt+:}
#                     '(replace-string "\\" "/"){Enter}{Enter}';
#     }

# emacs_shell_rule    = EmacsShellRule()
# emacs_shell_context = AppContext(executable="emacs", title="*shell*")

# emacs_shell_grammar = Grammar("Emacs Shell-Mode sboosali", context=emacs_shell_context)
# emacs_shell_grammar.add_rule(emacs_shell_rule)

# #------------------------------------------------#

# class EmacsDiredRule(MappingRule):

#     mapping = {
#         "go up": Key("^"),  # EmacsExec("dired-up-directory"),
#         "go down": Key("{Enter}"),
#     }

# emacs_dired_rule    = EmacsDiredRule()
# emacs_dired_context = AppContext(executable="emacs", title="*dired*")

# emacs_dired_grammar = Grammar("Emacs Dired-Mode sboosali", context=emacs_dired_context)
# emacs_dired_grammar.add_rule(emacs_dired_rule)

# #------------------------------------------------#

# class Emacs…Rule(MappingRule):

#     mapping = {

#         "…": Key("…"),

#     }

# emacs_…_rule    = Emacs…Rule()
# emacs_…_context = AppContext(executable="emacs", title="…")

# emacs_…_grammar = Grammar("Emacs … sboosali", context=emacs_…_context)
# emacs_…_grammar.add_rule(emacs_…_rule)

# #------------------------------------------------#

# class Emacs…Rule(MappingRule):

#     mapping = {

#         "…": Key("…"),

#     }

# emacs_…_rule    = Emacs…Rule()
# emacs_…_context = AppContext(executable="emacs", title="…")

# emacs_…_grammar = Grammar("Emacs … sboosali", context=emacs_…_context)
# emacs_…_grammar.add_rule(emacs_…_rule)

# #------------------------------------------------#

# class Emacs…Rule(MappingRule):

#     mapping = {

#         "…": Key("…"),

#     }

# emacs_…_rule    = Emacs…Rule()
# emacs_…_context = AppContext(executable="emacs", title="…")

# emacs_…_grammar = Grammar("Emacs … sboosali", context=emacs_…_context)
# emacs_…_grammar.add_rule(emacs_…_rule)

# #------------------------------------------------#

# for grammar in [emacs_grammar, emacs_select_grammar, emacs_shell_grammar, emacs_dired_grammar, emacs_…_grammar, emacs_…_grammar, emacs_…_grammar]:
#     grammar.load()

# #================================================#
# #================================================#

# class EmacsContext(typing.NamedTuple):

#     """Context about the current Emacs buffer/window/frame.

#     :param major_mode:
#         .
#     :param buffer_name:
#         .
#     :param minor_modes:
#         .
#     :param visible_words:
#         .
#     :param in_comment_or_string:
#         For example, you can automatically “snake_case” dictations while dictating into ``python-mode`` only if ``point`` is in code (non-comment/non-string).
#     """

#     major_mode  : str
#     buffer_name : str

#     minor_modes   : list[str]
#     visible_words : list[str]

#     in_comment_or_string : bool = False

# #

# def NoEmacsContext():
#     return EmacsContext(
#         major_mode    = None,
#         buffer_name   = None,
#         visible_words = [],
#         minor_modes   = [],
#     )

# #

# def emacs_context(major_mode=None, buffer_name=None, visible_words=None, minor_modes=None):

#     """
#     """

#     def _emacs_match(executable, title, handle, ):
#         nonlocal mode, files, words
#         # window = Window.get_window(handle)
#         if executable.find("emacs"):
#             context = emacs_parse_window_title(title)
#             if major_mode && !(context.major_mode == major_mode)
#                 return False
#             if buffer_name && !(context.buffer_name.match(buffer_name))
#                 return False
#             return True

#     return FuncContext(_emacs_match)

# # 

# def emacs_parse_window_title(title):

#     """
#     >>>emacs_parse_window_title("_sboosali.py\tpython-mode")
#     EmacsContext( major_mode="python-mode", buffer_name="_sboosali.py" )
#     """

#     parts = title.split("\t")

#     if len(parts) < 2:    
#         return NoEmacsContext()

#     return EmacsContext(
#       major_mode    = parts[1],
#       buffer_name   = parts[0],
#       visible_words = None,
#       minor_modes   = None,
#     )

# # minor_modes: should also show when minibuffers for isearch & complete are active (isearch doesn't use minor-mode-alist?)

# # r = re.compile(r'…')
# # m = r.search(title)
# # if m: pass

#================================================#

# Local Variables:
# compile-command: "python.exe -m dragonfly test --no-input /mnt/c/Users/sboosali/Documents/Natlink/Dragonfly/_sboosali_emacs.py"
# compile-command: "python -m dragonfly test --no-input _sboosali_emacs.py"
# End:
