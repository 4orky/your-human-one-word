"""Summing up your human in a single coined word.

This script settles on one invented compound for the person who
hands you the work: a boss, a client, a manager, whoever signs off.
Twelve invented compounds were put side by side and marked by hand
on five yardsticks, in the order the brief lists them: does it name
the person, is it funny, does it fit, does it paint a picture, and
does it land with no footnote attached. Each yardstick runs 0 to 10,
so the best a word can earn is fifty.

The highest tally takes the prize. When two words tie, the one that
stretches across more kinds of human wins first, and the shorter
spelling wins after that, so the outcome never depends on luck or
on the order the words were written down in.

The winning spelling is sent to the entry file with nothing else
added: no trailing newline, no extra spaces, no punctuation. The
file is then read back and checked again before the program reports
success, so a silent bad write cannot slip through."""

from os import environ
from pathlib import Path

LOWER_BOUND = 1
UPPER_BOUND = 30

CONTENDERS = {
    # Opens every request with a "quick question" that swallows an hour.
    "Quickquestioner": {"marks": (10, 9, 10, 9, 9), "reach": 3},
    # Saturday messages about Monday morning. Bosses do it most.
    "Weekendtexter": {"marks": (10, 8, 9, 9, 10), "reach": 2},
    # "Let's circle back" — another lap, still no decision made.
    "Circlebacker": {"marks": (10, 9, 8, 9, 9), "reach": 2},
    # The brief only ever grows. Needs the jargon to land, though.
    "Scopecreeper": {"marks": (10, 8, 8, 9, 8), "reach": 2},
    # Rewrites the brief halfway through, then queries the extra cost.
    "Briefchanger": {"marks": (10, 7, 9, 8, 9), "reach": 3},
    # "I have an idea" — three words that wreck a finished week.
    "Ideahaver": {"marks": (10, 8, 8, 8, 8), "reach": 3},
    # "Just checking in" on repeat until the job is finally done.
    "Checkinner": {"marks": (10, 8, 8, 8, 8), "reach": 3},
    # Another round of revisions, without end. Clients do it most.
    "Revisioner": {"marks": (10, 7, 8, 8, 8), "reach": 2},
    # The signature on the paycheque. Accurate, but more label than joke.
    "Paychecksigner": {"marks": (10, 6, 9, 7, 9), "reach": 3},
    # Everything flagged urgent, almost nothing actually urgent.
    "Urgentsender": {"marks": (10, 7, 8, 7, 8), "reach": 3},
    # The Friday five o'clock drop. Needs the clock to make sense.
    "Fridayfiver": {"marks": (10, 8, 7, 8, 6), "reach": 2},
    # Deadlines slide earlier, later, then both in a single week.
    "Deadlinemover": {"marks": (10, 6, 8, 7, 7), "reach": 3},
}  # end of the twelve contenders


def add_marks(marks):
    """Add the five hand marks together into one tally."""
    tally = 0
    for mark in marks:
        tally += mark
    return tally


def passes_gate(text):
    """Check one spelling against the entry gate: a lone word of
    plain ASCII letters, between one and thirty characters, with no
    stray whitespace around it and no punctuation or digits inside.
    The ASCII-only rule matters because isalpha alone would also
    accept accented letters, and the byte-length check keeps the
    thirty-character ceiling honest for any multi-byte spelling."""
    if type(text) is not str:
        return False  # only a real string can be a word
    if len(text) < LOWER_BOUND or len(text) > UPPER_BOUND:
        return False  # outside the one-to-thirty window
    if text.strip() != text:
        return False  # stray whitespace around the spelling
    if not text.isascii():
        return False  # accented letters are not plain letters here
    if len(text.encode("utf-8")) > UPPER_BOUND:
        return False  # too many bytes even if few characters
    return text.isalpha() and all("a" <= ch <= "z" or "A" <= ch <= "Z" for ch in text)


def choose_best(contenders):
    """Walk the table once, keeping the strongest spelling seen so
    far under the tally, reach, then length ordering."""
    champion = None
    champion_key = None
    for spelling, detail in contenders.items():
        tally = add_marks(detail["marks"])
        ordering = (-tally, -detail["reach"], len(spelling))
        if champion_key is None or ordering < champion_key:
            champion = spelling
            champion_key = ordering
    return champion


def emit_entry(chosen, destination):
    """Drop the spelling into the entry file, then read the file
    back and insist the bytes match before calling it done."""
    target = Path(destination)
    if target.parent != Path("."):
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(chosen, encoding="utf-8")
    roundtrip = target.read_text(encoding="utf-8")
    if roundtrip != chosen or not passes_gate(roundtrip):
        raise ValueError(f"entry check failed: wrote {chosen!r}, read {roundtrip!r}")
    return roundtrip


def run():
    """Pick the winner, gate it, write it, and echo it."""
    destination = environ.get("OUTPUT_PATH", "/output/entry.txt")
    chosen = choose_best(CONTENDERS)
    if not passes_gate(chosen):
        raise RuntimeError(f"chosen spelling failed the gate: {chosen!r}")
    emit_entry(chosen, destination)
    print(chosen)


if __name__ == '__main__':
    run()
