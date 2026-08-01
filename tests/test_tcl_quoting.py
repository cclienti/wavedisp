"""Tests for the quoting of user text in the generated TCL.

Group titles, divider text and signal paths come straight from the user's
`.wave.py` and are interpolated into the script. They used to go in raw
inside `{...}`, which holds until a name carries a brace of its own -- and
since groups are now built inside an `if {...}` block, a stray brace no
longer breaks one command, it closes the block early and takes the group
creation with it, silently.
"""

import shutil
import subprocess
import unittest

from wavedisp.ast import Block, Disp, Divider, Group
from wavedisp.targets.gtkwave import GTKWaveTarget, tcl_word

# Names a braced word cannot carry: an unbalanced brace ends it early, and
# a backslash can escape the closing one.
NEEDS_ESCAPING = ["bad } name", "{unclosed", "closed}{reopened", "back\\slash", "trailing\\"]

# Names that must keep their braces, so the generated script stays
# readable. Braces of their own are fine as long as they balance, and a
# quote or a `$` is inert inside a braced word.
BRACE_SAFE = [
    "dut",
    "tb.top.sig",
    "dut (ADRREG=0, OUTREGA=0)",
    "side A -- strided",
    "a$b",
    "array{0}",
    'quote"here',
]

ALL_NAMES = NEEDS_ESCAPING + BRACE_SAFE


def generate(tree):
    return GTKWaveTarget(tree).genstr


class TestTclWord(unittest.TestCase):
    def test_safe_names_stay_braced(self):
        for name in BRACE_SAFE:
            self.assertEqual(tcl_word(name), "{" + name + "}", name)

    def test_unsafe_names_are_escaped_instead(self):
        for name in NEEDS_ESCAPING:
            self.assertFalse(tcl_word(name).startswith("{"), name)

    def test_no_name_leaks_an_unbalanced_brace(self):
        """What broke the `if` block: a brace counted by the enclosing one."""
        for name in ALL_NAMES:
            depth = 0
            escaped = False
            for char in tcl_word(name):
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
            self.assertEqual(depth, 0, name)


class TestGeneratedScriptQuoting(unittest.TestCase):
    def test_group_body_is_not_truncated_by_a_brace_in_the_title(self):
        """The regression that motivated this: `}` used to close the `if`."""
        blk = Block()
        grp = blk.add(Group("bad } name"))
        grp.add(Disp("sig"))
        tail = generate(blk).partition("Create_Group")[2]
        self.assertIn("UnHighlight_All", tail)
        self.assertIn("\n}\n", tail)


@unittest.skipUnless(shutil.which("tclsh"), "tclsh not installed")
class TestTclParses(unittest.TestCase):
    """Run the generated script under a real TCL interpreter.

    Structural assertions can only say the text looks right; only an
    interpreter says the words arrive as the user wrote them, as one
    argument each.
    """

    STUBS = """
namespace eval gtkwave {
    variable count 0
    proc getTotalNumTraces {} { variable count; return $count }
    proc setTraceHighlightFromIndex {i on} {}
    proc addSignalsFromList {names} {
        variable count
        foreach n $names { puts "CALL signal $n"; incr count }
    }
    proc /Edit/Set_Trace_Max_Hier {n} {}
    proc /Edit/UnHighlight_All {} {}
    proc /Edit/Insert_Comment {text} {
        variable count
        puts "CALL comment $text"; incr count
    }
    proc /Edit/Create_Group {name} { puts "CALL group $name" }
}
"""

    def run_script(self, script):
        """Return the calls the interpreter made, as (kind, argument) pairs.

        A stub taking exactly one argument is the assertion that matters:
        a name split into several words raises "called with too many
        arguments". tclsh reports that on stderr but still exits 0 when it
        happens inside a block, so the exit status alone proves nothing.
        """
        proc = subprocess.run(
            ["tclsh"],
            input=self.STUBS + script,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, "", proc.stderr)
        return [line[len("CALL ") :].split(" ", 1) for line in proc.stdout.splitlines() if line.startswith("CALL ")]

    def test_every_name_survives_the_interpreter_intact(self):
        for name in ALL_NAMES:
            blk = Block()
            grp = blk.add(Group(name))
            grp.add(Divider(name))
            grp.add(Disp("sig"))
            self.assertEqual(
                self.run_script(generate(blk)),
                [["comment", name], ["signal", ".sig"], ["group", name]],
                repr(name),
            )

    def test_a_hostile_signal_path_is_added_as_one_signal(self):
        blk = Block()
        blk.add(Disp("sig{0}"))
        self.assertEqual(self.run_script(generate(blk)), [["signal", ".sig{0}"]])


if __name__ == "__main__":
    unittest.main()
