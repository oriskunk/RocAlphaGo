import os
import numpy as np
import sgf
import sys
sys.path.append(os.pardir)
sys.path.append('.')

from AlphaGo.go import GameState
from AlphaGo.util import sgf_iter_states


def _is_sgf(fname):
    return fname.strip()[-4:] == ".sgf"


def _walk_all_sgfs(root):
    for (dirpath, dirname, files) in os.walk(root):
        for filename in files:
            if _is_sgf(filename):
                yield os.path.join(dirpath, filename)

def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_data", help='./data/rollout/')
    parser.add_argument("type", help='3x3, 12d, nakade')
    parser.add_argument("--output", default='./patterns/_01.npy', help='./patterns/3x3_01.npy')
    args = parser.parse_args()

    patterns = {}
    if args.input_data:
        for _file in _walk_all_sgfs(args.input_data):
            print _file
            with open(_file, 'r') as f:
                _sgf = f.read()#.decode('euc-kr')
                probs = sgf.parse(_sgf)[0].root.properties
                if probs.get('RE') == None:
                    print 'result is none'
                    continue
                if probs.get('RE')[0] in ['W+Time', 'B+Time', 'W+Forfeit', 'B+Forfeit']:
                    print probs.get('RE')[0], 'PASS!!!'
                    continue
                if probs.get('AB') != None:
                    print probs.get('AB')[0], 'PASS!!!'
                    continue
                '''
                if probs.get('RU')[0] != 'Chinese':
                #if probs.get('RU')[0] != 'Japanese':
                    print probs.get('RU')[0], 'PASS!!!'
                    continue
                '''

                try:
                    for (gs, move, _) in sgf_iter_states(_sgf):

                        if len(gs.get_history()) > 0 and gs.get_history()[-1] == move:
                            break

                        if move == -1:
                            break

                        if args.type == '3x3': # Non-response 3x3 pattern
                            pattern_hash = gs._get_hash_3x3(move)
                            if pattern_hash != -1:
                                if pattern_hash in patterns:
                                    patterns[pattern_hash] = patterns[pattern_hash] + 1
                                else:
                                    patterns[pattern_hash] = 1
        
                                print pattern_hash, patterns[pattern_hash], move
                        elif args.type == '12d': # Response 12-point daimond pattern
                            if len(gs.get_history()) > 0 and gs.get_history()[-1] != move:
                                xDis = gs.get_history()[-1][0] - move[0]
                                yDis = gs.get_history()[-1][1] - move[1]
                                if abs(xDis) + abs(yDis) > 2:
                                    continue
                                pattern_hash = gs._get_hash_12d(gs.get_history()[-1], xDis+2, yDis+2)
                                if pattern_hash != -1:
                                    if pattern_hash in patterns:
                                        patterns[pattern_hash] = patterns[pattern_hash] + 1
                                    else:
                                        patterns[pattern_hash] = 1
            
                                    print pattern_hash, patterns[pattern_hash], move
                        elif args.type == 'nakade':
                            pattern_hash = gs._get_hash_nakade(move)
                            if pattern_hash != -1:
                                if pattern_hash in patterns:
                                    patterns[pattern_hash] = patterns[pattern_hash] + 1
                                else:
                                    patterns[pattern_hash] = 1

                                print pattern_hash, patterns[pattern_hash], move#, p_count

                except:# IllegalMove as ex:
                    print('IllegalMove exception:', _file)

        np.save(args.output, patterns)

if __name__ == '__main__':
    go()
