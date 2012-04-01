import json
import sys
from paip import eliza

rules = {
    "?*x hello ?*y": [
        "Hello, my name is SUPPORT.  How can I help you today?",
        ],
    "?*x manager ?*y": [
        "Our manager is not available right now.  How can I help you?"
        ],
    "?*x problem with ?*y": [
        "Have you tried turning it off and back on?",
        "When did you first observe ?y to be a problem?",
        "How long has ?y been a problem?",
        "That is not covered by the warranty.",
        ],
    "?*x trouble with ?*y": [
        ("I'm sorry, ?y is handled by another department.\n" +
         "Please wait while I transfer your call."),
        "What seems to be the problem?",
        ],
    "?*x how to ?*y": [
        "Please consult the manual for more details.",
        "I'm sorry, I do not have that information.",
        "Can you be more specific?",
        "?y will void your warranty."
        ],
    "?*x why ?*y": [
        "I'm sorry, I can't discuss that.",
        ],
    "?*x ago ?*y": [
        "I'm sorry, your warranty ended a week earlier.",
        ]
    }

default_responses = [
    "I do not understand.",
    "Please elaborate.",
    "Please hold."
    ]

def main():
    # We need the rules in a list containing elements of the following form:
    # `(input pattern, [output pattern 1, output pattern 2, ...]`
    rules_list = []
    for pattern, transforms in rules.items():
        # Remove the punctuation from the pattern to simplify matching.
        pattern = eliza.remove_punct(str(pattern.upper())) # kill unicode
        transforms = [str(t).upper() for t in transforms]
        rules_list.append((pattern, transforms))
    eliza.interact('SUPPORT> ', rules_list, map(str.upper, default_responses))

if __name__ == '__main__':
    main(sys.argv[1:])
