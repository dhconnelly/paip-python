from paip import othello

def check(move, player, board):
    return othello.is_valid(move) and othello.is_legal(move, player, board)

def human(player, board):
    print othello.print_board(board)
    print 'Your move?'
    while True:
        move = raw_input('> ')
        if move and check(int(move), player, board):
            return int(move)
        elif move:
            print 'Illegal move--try again.'

def get_choice(prompt, options):
    print prompt
    print 'Options:', options.keys()
    while True:
        choice = raw_input('> ')
        if choice in options:
            return options[choice]
        elif choice:
            print 'Invalid choice.'

def get_players():
    print 'Welcome to OTHELLO!'
    options = { 'human': human,
                'random': othello.random_strategy,
                'max-diff': othello.maximizer(othello.score),
                'max-weighted-diff': othello.maximizer(othello.weighted_score),
                'minimax-diff': othello.minimax_searcher(3, othello.score),
                'minimax-weighted-diff':
                    othello.minimax_searcher(3, othello.weighted_score),
                'ab-diff': othello.alphabeta_searcher(3, othello.score),
                'ab-weighted-diff':
                    othello.alphabeta_searcher(3, othello.weighted_score) }
    black = get_choice('BLACK: choose a strategy', options)
    white = get_choice('WHITE: choose a strategy', options)
    return black, white

def main():
    try:
        black, white = get_players()
        board, score = othello.play(black, white)
    except othello.IllegalMoveError as e:
        print e
        return
    except EOFError as e:
        print 'Goodbye.'
        return
    print 'Final score:', score
    print '%s wins!' % ('Black' if score > 0 else 'White')
    print othello.print_board(board)
