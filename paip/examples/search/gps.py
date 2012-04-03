from paip.search import beam_search

## GPS implemented as search

def successors(states, operators):
    ret = []
    for op in applicable_ops(states, operators):
        ret.append([s for s in states if s not in op['delete']] + op['add'])
    return ret
    

def applicable_ops(states, ops):
    states = set(states)
    return [op for op in ops if set(op['preconds']) <= states]
            

def gps(initial_states, goal_states, operators, beam_width=10):
    prefix = 'Executing '
    for operator in operators:
        operator['add'].append(prefix + operator['action'])

    def get_successors(states):
        return successors(states, operators)

    def goal_reached(states):
        for goal in goal_states:
            if goal not in states:
                return False
        return True
    
    def cost(states):
        sum = len([s for s in states if s.startswith(prefix)])
        sum += len([g for g in goal_states if g not in states])
        return sum
            
    final = beam_search(initial_states, goal_reached,
                        get_successors, cost, beam_width)
    return [state for state in final if state.startswith(prefix)]
    

## Example problem definition

problem = {
    "start": ["space on a", "a on b", "b on c", "c on table", "space on table"],
    "finish": ["space on c", "c on b", "b on a", "a on table", "space on table"],
    "ops": [
        {
            "action": "move a from b to c", 
            "preconds": [
                "space on a", 
                "space on c", 
                "a on b"
            ], 
            "add": [
                "a on c", 
                "space on b"
            ], 
            "delete": [
                "a on b", 
                "space on c"
            ]
        }, 
        {
            "action": "move a from table to b", 
            "preconds": [
                "space on a", 
                "space on b", 
                "a on table"
            ], 
            "add": [
                "a on b"
            ], 
            "delete": [
                "a on table", 
                "space on b"
            ]
        }, 
        {
            "action": "move a from b to table", 
            "preconds": [
                "space on a", 
                "space on table", 
                "a on b"
            ], 
            "add": [
                "a on table", 
                "space on b"
            ], 
            "delete": [
                "a on b"
            ]
        }, 
        {
            "action": "move a from c to b", 
            "preconds": [
                "space on a", 
                "space on b", 
                "a on c"
            ], 
            "add": [
                "a on b", 
                "space on c"
            ], 
            "delete": [
                "a on c", 
                "space on b"
            ]
        }, 
        {
            "action": "move a from table to c", 
            "preconds": [
                "space on a", 
                "space on c", 
                "a on table"
            ], 
            "add": [
                "a on c"
            ], 
            "delete": [
                "a on table", 
                "space on c"
            ]
        }, 
        {
            "action": "move a from c to table", 
            "preconds": [
                "space on a", 
                "space on table", 
                "a on c"
            ], 
            "add": [
                "a on table", 
                "space on c"
            ], 
            "delete": [
                "a on c"
            ]
        }, 
        {
            "action": "move b from a to c", 
            "preconds": [
                "space on b", 
                "space on c", 
                "b on a"
            ], 
            "add": [
                "b on c", 
                "space on a"
            ], 
            "delete": [
                "b on a", 
                "space on c"
            ]
        }, 
        {
            "action": "move b from table to a", 
            "preconds": [
                "space on b", 
                "space on a", 
                "b on table"
            ], 
            "add": [
                "b on a"
            ], 
            "delete": [
                "b on table", 
                "space on a"
            ]
        }, 
        {
            "action": "move b from a to table", 
            "preconds": [
                "space on b", 
                "space on table", 
                "b on a"
            ], 
            "add": [
                "b on table", 
                "space on a"
            ], 
            "delete": [
                "b on a"
            ]
        }, 
        {
            "action": "move b from c to a", 
            "preconds": [
                "space on b", 
                "space on a", 
                "b on c"
            ], 
            "add": [
                "b on a", 
                "space on c"
            ], 
            "delete": [
                "b on c", 
                "space on a"
            ]
        }, 
        {
            "action": "move b from table to c", 
            "preconds": [
                "space on b", 
                "space on c", 
                "b on table"
            ], 
            "add": [
                "b on c"
            ], 
            "delete": [
                "b on table", 
                "space on c"
            ]
        }, 
        {
            "action": "move b from c to table", 
            "preconds": [
                "space on b", 
                "space on table", 
                "b on c"
            ], 
            "add": [
                "b on table", 
                "space on c"
            ], 
            "delete": [
                "b on c"
            ]
        }, 
        {
            "action": "move c from a to b", 
            "preconds": [
                "space on c", 
                "space on b", 
                "c on a"
            ], 
            "add": [
                "c on b", 
                "space on a"
            ], 
            "delete": [
                "c on a", 
                "space on b"
            ]
        }, 
        {
            "action": "move c from table to a", 
            "preconds": [
                "space on c", 
                "space on a", 
                "c on table"
            ], 
            "add": [
                "c on a"
            ], 
            "delete": [
                "c on table", 
                "space on a"
            ]
        }, 
        {
            "action": "move c from a to table", 
            "preconds": [
                "space on c", 
                "space on table", 
                "c on a"
            ], 
            "add": [
                "c on table", 
                "space on a"
            ], 
            "delete": [
                "c on a"
            ]
        }, 
        {
            "action": "move c from b to a", 
            "preconds": [
                "space on c", 
                "space on a", 
                "c on b"
            ], 
            "add": [
                "c on a", 
                "space on b"
            ], 
            "delete": [
                "c on b", 
                "space on a"
            ]
        }, 
        {
            "action": "move c from table to b", 
            "preconds": [
                "space on c", 
                "space on b", 
                "c on table"
            ], 
            "add": [
                "c on b"
            ], 
            "delete": [
                "c on table", 
                "space on b"
            ]
        }, 
        {
            "action": "move c from b to table", 
            "preconds": [
                "space on c", 
                "space on table", 
                "c on b"
            ], 
            "add": [
                "c on table", 
                "space on b"
            ], 
            "delete": [
                "c on b"
            ]
        }
    ]
}


from paip import search


def main():
    start = problem['start']
    finish = problem['finish']
    ops = problem['ops']
    for action in gps(start, finish, ops):
        print action


if __name__ == '__main__':
    main()
