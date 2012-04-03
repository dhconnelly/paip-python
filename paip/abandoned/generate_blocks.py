import json
import sys

def move_op(a, b, c):
    return {
        'action': 'move %s from %s to %s' % (a, b, c),
        'preconds': [
            'space on %s' % a,
            'space on %s' % c,
            '%s on %s' % (a, b)
        ],
        'add': move_ons(a, b, c),
        'delete': move_ons(a, c, b),
    }


def move_ons(a, b, c):
    moves = ['%s on %s' % (a, c)]
    if b != 'table':
        moves.append('space on %s' % b)
    return moves


def generate(blocks):
    ops = []
    for a in blocks:
        for b in blocks:
            if a == b: continue
            for c in blocks:
                if c in (a, b): continue
                ops.append(move_op(a, b, c))
            ops.append(move_op(a, 'table', b))
            ops.append(move_op(a, b, 'table'))
    print json.dumps(ops, indent=4)


if __name__ == '__main__':
    generate(sys.argv[1:])
