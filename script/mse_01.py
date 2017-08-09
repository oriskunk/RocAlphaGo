import os
import numpy as np
import sgf
import sys
sys.path.append(os.pardir)
sys.path.append('./pachi')
sys.path.append('.')

from ctypes import *
from AlphaGo import go
from AlphaGo.ai import RolloutPlayer
from AlphaGo.go import GameState
from AlphaGo.models.value import CNNValue
from AlphaGo.models.rollout import CNNRollout
from AlphaGo.util import sgf_iter_states


def _is_sgf(fname):
    return fname.strip()[-4:] == ".sgf"


def _walk_all_sgfs(root):
    for (dirpath, dirname, files) in os.walk(root):
        for filename in files:
            if _is_sgf(filename):
                yield os.path.join(dirpath, filename)

                                            
def update(current, limit, mse, total_width):
    sys.stdout.write('\b' * total_width)
    sys.stdout.write('\r')
    numdigits = int(np.floor(np.log10(limit))) + 1
    barstr = '%%%dd/%%%dd [' % (numdigits, numdigits)
    bar = barstr % (current, limit)
    prog = float(current) / limit
    prog_width = int(30 * prog)
    if prog_width > 0:
        bar += ('=' * (prog_width - 1))
    if current < limit:
        bar += '>'
    else:
        bar += '='
    bar += ('.' * (30 - prog_width))
    bar += ']'
    sys.stdout.write(bar)
    total_width = len(bar)

    info = ' - mse: %.4f' % mse
    total_width += len(info)

    sys.stdout.write(info)
    sys.stdout.flush()
    return total_width


def get_mse(gs, move, player, winner, mode='value_network'):

    start = time.time()
    if mode == 'value_network':
        _output = value.eval_state(gs)
        _output = _output * player   # WHITE PLAYER
        output = 0.5 + (_output/2.0) # -1 ~ +1 to 0 ~ +1
        if winner == -1:             # 0 ~ +1
            winner = 0
        return abs(winner - output)

    if mode == 'pachi_rollout':
        if move == None:
            plinker.play(key, -1, player, True)
        else:
            plinker.play(key, (move[0]+1)*100 + move[1]+1, player, True)
        #if len(gs.history) < 5:
        #    plinker.print_board(key)
        plinker._rollout.restype = c_float
        return plinker._rollout(key, player, winner, 100);

    if mode == 'rollout_policy':

        win = 0
        player = RolloutPlayer(policy, temperature=0.67, pass_when_offered=True, move_limit=500)#, greedy_start=int(gs.get_history_size() + 2))
        for i in xrange(100):
            state = GameState(copyState=gs)
            #print state.get_history()
            while True:
                move = player.get_move(state)
                state.do_move(move)
                if state.is_end_of_game():
                    if state.get_winner() == 4 and winner == -1: # BLACK vs WHITE
                        win += 1
                    elif state.get_winner() == 3 and winner == 1: # WHITE vs BLACK
                        win += 1
                    break
            #print state.get_history()

        print (time.time() - start), (win / 100.0)
        return (win / 100.0)

    return None


def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("weights")
    parser.add_argument("sgf_file")
    parser.add_argument("--temperature", type=int, default=0.67)
    parser.add_argument("--move_from", type=int, default=0)
    parser.add_argument("--num_moves", type=int, default=300)
    parser.add_argument("--num_games", type=int, default=1)
    parser.add_argument("--output", default='./mse')
    parser.add_argument("--mode", default='rollout_policy')
    args = parser.parse_args()

    global player

    # ROLLOUT POLICY
    global policy
    if args.mode == 'rollout_policy':
        policy = CNNRollout.load_model(args.model)
        policy.model.load_weights(args.weights)
        player = RolloutPlayer(policy, temperature=args.temperature, pass_when_offered=True, move_limit=500)

    with open(args.sgf_file) as f: 

        if not os.path.exists( args.output ):
            os.makedirs( args.output )

        sgf_string = f.read()#.decode('euc-kr')
        probs = sgf.parse(sgf_string)[0].root.properties

        if probs.get('RE') == None:
            print 'RE == None'
            return

        #if probs.get('RE')[0] not in ['W+Resign', 'B+Resign']:
        #    print probs.get('RE')[0], '=> PASS'
        #    return

        if probs.get('RE')[0] in ['W+Time', 'B+Time', 'W+Forfeit', 'B+Forfeit', 'W+T', 'B+T']:
            print probs.get('RE')[0], '=> PASS'
            return

        if probs.get('KM') == None:
            print 'KM == None'
            return

        if probs.get('KM')[0] != '6.50':
            print probs.get('KM')[0], '=> PASS'
            return

        if probs.get('AB') != None:
            print probs.get('AB')[0], '=> PASS'
            return

        mse = {}
        for (gs, move, _, winner, p_count) in sgf_iter_states(sgf_string, True):

            if p_count is None:
                continue

            if args.move_from >= p_count:
                continue

            if args.move_from + args.num_moves < p_count:
                break

            correct = 0.0
            for _ in xrange( args.num_games ):

                state = GameState( copyState=gs )
                while True:

                    move = player.get_move( state )
                    state.do_move( move )
                    if state.is_end_of_game():

                        if state.get_winner() == 3 and winner == -1:

                            correct += 1
                        elif state.get_winner() == 4 and winner == 1:

                            correct += 1
                        break

            mse[ p_count ] = 1 - (correct / args.num_games)
            np.save('{}/{}.{}_{}'.format(args.output, os.path.basename(args.sgf_file), args.move_from, args.num_moves), mse)
            print mse[ p_count ], correct, args.num_games


if __name__ == '__main__':
    go()
