import json
import sys
from paip import eliza

rules = {
    "?*x hello ?*y": [
        "How do you do. Please state your problem."
    ],
    "?*x I want ?*y": [
        "What would it mean if you got ?y?",
        "Why do you want ?y?",
        "Suppose you got ?y soon."
    ],
    "?*x if ?*y": [
        "Do you really think its likely that ?y?",
        "Do you wish that ?y?",
        "What do you think about ?y?",
        "Really--if ?y?"
    ],
    "?*x no ?*y": [
        "Why not?",
        "You are being a bit negative.",
        "Are you saying 'No' just to be negative?"
    ],
    "?*x I was ?*y": [
        "Were you really?",
        "Perhaps I already knew you were ?y.",
        "Why do you tell me you were ?y now?"
    ],
    "?*x I feel ?*y": [
        "Do you often feel ?y?"
    ],
    "?*x I felt ?*y": [
        "What other feelings do you have?"
    ],
    "?*x my name is ?*y yours ?*z": [
	"My name is Eliza. Nice to meet you, ?y."
    ]
}

def main():
    # We need the rules in a list containing elements of the following form:
    # `(input pattern, [output pattern 1, output pattern 2, ...]`
    rules_list = []
    for pattern, transforms in rules.items():
        # Remove the punctuation from the pattern to simplify matching.
        pattern = eliza.remove_punct(str(pattern.upper())) # kill unicode
        transforms = [str(t).upper() for t in transforms]
        rules_list.append((pattern, transforms))
    eliza.interact(rules_list)

if __name__ == '__main__':
    main(sys.argv[1:])
