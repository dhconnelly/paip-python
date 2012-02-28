from paip.gps import gps

problem = {
    "start": ["son at home", "have money", "have phone book", "car needs battery"],
    "finish": ["son at school"],
    "ops": [
	{
	    "action": "drive son to school",
	    "preconds": ["son at home", "car works"],
	    "add": ["son at school"],
	    "delete": ["son at home"]
	},
	{
	    "action": "shop installs battery",
	    "preconds": ["car needs battery", "shop knows problem", "shop has money"],
	    "add": ["car works"],
	    "delete": []
	},
	{
	    "action": "tell shop problem",
	    "preconds": ["in communication with shop"],
	    "add": ["shop knows problem"],
	    "delete": []
	},
	{
	    "action": "telephone shop",
	    "preconds": ["know phone number"],
	    "add": ["in communication with shop"],
	    "delete": []
	},
	{
	    "action": "look up number",
	    "preconds": ["have phone book"],
	    "add": ["know phone number"],
	    "delete": []
	},
	{
	    "action": "give shop money",
	    "preconds": ["have money"],
	    "add": ["shop has money"],
	    "delete": ["have money"]
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
