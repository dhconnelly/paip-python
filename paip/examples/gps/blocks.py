from paip.gps import gps

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

def main():
    start = problem['start']
    finish = problem['finish']
    ops = problem['ops']
    for action in gps(start, finish, ops):
        print action

if __name__ == '__main__':
    main()
