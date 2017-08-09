import numpy as np
import operator
import os
import sys
sys.path.append(os.pardir)
sys.path.append('.')

from gmpy2 import mpz
from pattern import print_hash


_BORDER  = 1
_EMPTY   = 2
_WHITE   = 3
_BLACK   = 4

_HASHVALUE = 5#33

TRANSFORMATIONS_3x3 = [
    [4, 0, 5, #noop
     1,    2,
     6, 3, 7],
    [5, 0, 4, #fliplr
     2,    1,
     7, 3, 6],
    [6, 3, 7, #flipud
     1,    2,
     4, 0, 5],
    [4, 1, 6, #diag1
     0,    3,
     5, 2, 7],
    [7, 2, 5, #diag2
     3,    0,
     6, 1, 4],
    [5, 2, 7, #rot90
     0,    3,
     4, 1, 6],
    [7, 3, 6, #rot180
     2,    1,
     5, 0, 4],
    [6, 1, 4, #rot270
     3,    0,
     7, 2, 5],
]


TRANSFORMATIONS_12d = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], #noop
    [0, 3, 2, 1, 7, 6, 5, 4, 10, 9, 8, 11], #fliplr
    [11, 8, 9, 10, 4, 5, 6, 7, 1, 2, 3, 0], #flipud
    [4, 1, 5, 8, 0, 2, 9, 11, 3, 6, 10, 7], #diag1
    [7, 10, 6, 3, 11, 9, 2, 0, 8, 5, 1, 4], #diag2
    [7, 3, 6, 10, 0, 2, 9, 11, 1, 5, 8, 4], #rot90
    [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], #rot180
    [4, 8, 5, 1, 11, 9, 2, 0, 10, 6, 3, 7], #rot270
]

TRANSFORMATIONS_5x5 = [
    [ 0,  1,  2,  3,  4, #noop
      5,  6,  7,  8,  9,
     10, 11, 12, 13, 14,
     15, 16, 17, 18, 19,
     20, 21, 22, 23, 24],
    [ 4,  3,  2,  1,  0, #fliplr
      9,  8,  7,  6,  5,
     14, 13, 12, 11, 10,
     19, 18, 17, 16, 15,
     24, 23, 22, 21, 20],
    [20, 21, 22, 23, 24, #flipud
     15, 16, 17, 18, 19,
     10, 11, 12, 13, 14,
      5,  6,  7,  8,  9,
      0,  1,  2,  3,  4],
    [ 0,  5, 10, 15, 20, #diag1
      1,  6, 11, 16, 21,
      2,  7, 12, 17, 22,
      3,  8, 13, 18, 23,
      4,  9, 14, 19, 24],
    [24, 19, 14,  9,  4, #diag2
     23, 18, 13,  8,  3,
     22, 17, 12,  7,  2,
     21, 16, 11,  6,  1,
     20, 15, 10,  5,  0],
    [20, 15, 10,  5,  0, #rot270
     21, 16, 11,  6,  1,
     22, 17, 12,  7,  2,
     23, 18, 13,  8,  3,
     24, 19, 14,  9,  4],
    [24, 23, 22, 21, 20, #rot180
     19, 18, 17, 16, 15,
     14, 13, 12, 11, 10,
      9,  8,  7,  6,  5,
      4,  3,  2,  1,  0],
    [ 4,  9, 14, 19, 24, #rot90
      3,  8, 13, 18, 23,
      2,  7, 12, 17, 22,
      1,  6, 11, 16, 21,
      0,  5, 10, 15, 20],
    '''
    [ 4,  9, 14, 19, 24, #rot90
      3,  8, 13, 18, 23,
      2,  7, 12, 17, 22,
      1,  6, 11, 16, 21,
      0,  5, 10, 15, 20],
    [24, 23, 22, 21, 20, #rot180
     19, 18, 17, 16, 15,
     14, 13, 12, 11, 10,
      9,  8,  7,  6,  5,
      4,  3,  2,  1,  0],
    [20, 15, 10,  5,  0, #rot270
     21, 16, 11,  6,  1,
     22, 17, 12,  7,  2,
     23, 18, 13,  8,  3,
     24, 19, 14,  9,  4],
    '''
]

TRANSFORMATIONS_nakade = [
    [ 0,  1,  2,  3,  4, #noop
      5,  6,  7,  8,  9, 
     10, 11,     12, 13,
     14, 15, 16, 17, 18,
     19, 20, 21, 22, 23],
    [ 4,  3,  2,  1,  0, #fliplr
      9,  8,  7,  6,  5,
     13, 12,     11, 10,
     18, 17, 16, 15, 14,
     23, 22, 21, 20, 19,],
    [19, 20, 21, 22, 23, #flipud
     14, 15, 16, 17, 18,
     10, 11,     12, 13,
      5,  6,  7,  8,  9,
      0,  1,  2,  3,  4],
    [ 0,  5, 10, 14, 19, #diag1
      1,  6, 11, 15, 20,
      2,  7,     16, 21,
      3,  8, 12, 17, 22,
      4,  9, 13, 18, 23],
    [23, 18, 13,  9,  4, #diag2
     22, 17, 12,  8,  3,
     21, 16,      7,  2,
     20, 15, 11,  6,  1,
     19, 14, 10,  5,  0],
    [ 4,  9, 13, 18, 23, #rot90
      3,  8, 12, 17, 22,
      2,  7,     16, 21,
      1,  6, 11, 15, 20,
      0,  5, 10, 14, 19],
    [23, 22, 21, 20, 19, #rot180
     18, 17, 16, 15, 14,
     13, 12,     11, 10,
      9,  8,  7,  6,  5,
      4,  3,  2,  1,  0],
    [19, 14, 10,  5,  0, #rot270
     20, 15, 11,  6,  1,
     21, 16,      7,  2,
     22, 17, 12,  8,  3,
     23, 18, 13,  9,  4],
]


def get_hash_3x3(hash, use_color):

    key = hash
    color, lib, other_color = [], [], []

    player = key % _HASHVALUE
    key /= _HASHVALUE

    for i in xrange(8):
        lib.append( key % _HASHVALUE)
        key /= _HASHVALUE

        color.append( key % _HASHVALUE)
        key /= _HASHVALUE

    color.reverse()
    lib.reverse()

    for x in color:
        if x == _BLACK:
            other_color.append( _WHITE )
        elif x == _WHITE:
            other_color.append( _BLACK )
        else:
            other_color.append( x )

    other_player = _WHITE if player == _BLACK else _BLACK

    hash_dict = {}
    for trans in TRANSFORMATIONS_3x3:
        _hash = _HASHVALUE
        _hash_other = _HASHVALUE
        for i in [1, 3, 4, 6, 0, 2, 5, 7]:
            _hash += color[ trans[i]]
            _hash *= _HASHVALUE

            _hash += lib[ trans[i]]
            _hash *= _HASHVALUE

            _hash_other += other_color[ trans[i]]
            _hash_other *= _HASHVALUE

            _hash_other += lib[ trans[i]]
            _hash_other *= _HASHVALUE

        if _hash + player not in hash_dict:
            hash_dict[_hash + player] = 1
            yield _hash + player

        if use_color == True and _hash_other + other_player not in hash_dict:
            hash_dict[_hash_other + other_player] = 1
            yield _hash_other + other_player


def get_hash_12d(hash, use_color):

    key = hash
    color, lib, other_color = [], [], []

    y = key % _HASHVALUE# - 2
    key /= _HASHVALUE

    x = key % _HASHVALUE# - 2
    key /= _HASHVALUE

    player = key % _HASHVALUE
    key /= _HASHVALUE

    # working
    for i in xrange(12):
        lib.append( key % _HASHVALUE)
        key /= _HASHVALUE

        color.append( key % _HASHVALUE)
        key /= _HASHVALUE

    color.reverse()
    lib.reverse()

    for xx in color:
        if xx == _BLACK:
            other_color.append( _WHITE )
        elif xx == _WHITE:
            other_color.append( _BLACK )
        else:
            other_color.append( xx )

    other_player = _WHITE if player == _BLACK else _BLACK

    hash_dict = {}
    for trans, trans_xy in zip(TRANSFORMATIONS_12d, TRANSFORMATIONS_5x5):
        _hash = mpz(_HASHVALUE)
        _hash_other = mpz(_HASHVALUE)

        xy = trans_xy[x + y*5]
        _x = xy % 5
        _y = xy / 5

        for i in range(12):
            _hash += color[ trans[i]]
            _hash *= _HASHVALUE

            _hash += lib[ trans[i]]
            _hash *= _HASHVALUE

            _hash_other += other_color[ trans[i]]
            _hash_other *= _HASHVALUE

            _hash_other += lib[ trans[i]]
            _hash_other *= _HASHVALUE

        if _hash + player not in hash_dict:
            hash_dict[_hash + player] = 1
            yield ((_hash + player) * _HASHVALUE + _x) * _HASHVALUE + _y

        if use_color == True and _hash_other + other_player not in hash_dict:
            hash_dict[_hash_other + other_player] = 1
            yield ((_hash_other + other_player) * _HASHVALUE + _x) * _HASHVALUE + _y

def get_hash_nakade(hash, use_color):

    key = hash
    color, lib, other_color = [], [], []

    player = key % _HASHVALUE
    key /= _HASHVALUE

    for i in xrange(12):
        lib.append( key % _HASHVALUE)
        key /= _HASHVALUE

        color.append( key % _HASHVALUE)
        key /= _HASHVALUE

    key = (hash / _HASHVALUE**24 - _HASHVALUE) / _HASHVALUE
    for i in xrange(12):
        lib.append( key % _HASHVALUE)
        key /= _HASHVALUE

        color.append( key % _HASHVALUE)
        key /= _HASHVALUE

    color.reverse()
    lib.reverse()

    for x in color:
        if x == _BLACK:
            other_color.append( _WHITE )
        elif x == _WHITE:
            other_color.append( _BLACK )
        else:
            other_color.append( x )

    other_player = _WHITE if player == _BLACK else _BLACK

    hash_dict = {}
    for trans in TRANSFORMATIONS_nakade:
        _hash = _HASHVALUE
        _hash2 = _HASHVALUE
        _hash_other = _HASHVALUE
        _hash_other2 = _HASHVALUE
        for i in range(12):
            _hash += color[ trans[i]]
            _hash *= _HASHVALUE

            _hash += lib[ trans[i]]
            _hash *= _HASHVALUE

            _hash2 += color[ trans[i+12]]
            _hash2 *= _HASHVALUE

            _hash2 += lib[ trans[i+12]]
            _hash2 *= _HASHVALUE

            _hash_other += other_color[ trans[i]]
            _hash_other *= _HASHVALUE

            _hash_other += lib[ trans[i]]
            _hash_other *= _HASHVALUE

            _hash_other2 += other_color[ trans[i+12]]
            _hash_other2 *= _HASHVALUE

            _hash_other2 += lib[ trans[i+12]]
            _hash_other2 *= _HASHVALUE

        _hash = mpz(_hash)*_HASHVALUE**24 + _hash2
        _hash_other = mpz(_hash_other)*_HASHVALUE**24 + _hash_other2

        if _hash + player not in hash_dict:
            hash_dict[_hash + player] = 1
            yield _hash + player

        if use_color == True and _hash_other + other_player not in hash_dict:
            hash_dict[_hash_other + other_player] = 1
            yield _hash_other + other_player


def go(cmd_line_args=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default='./patterns/_02.npy')
    parser.add_argument("--output2", default='./patterns/_03.npy')
    parser.add_argument("-c", default=False, action='store_true')

    if cmd_line_args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(cmd_line_args)

    patterns = {}
    if args.input:
        dict = np.load(args.input).item()
        all_move_count = sum(dict.values()) * 1.0
        print 'pattern count: {},{} ({})'.format(len(dict), all_move_count, args.input)

        keys = dict.keys()
        for hash in keys:

            value = 0
            if hash < 1000000000000000L: # 3x3 pattern
                for _hash in get_hash_3x3( hash, args.c ):
                    value += dict.get( _hash, 0 )
                    patterns[ _hash ] = value
            elif hash > 50000000000000000000L: # nakade pattern
                for _hash in get_hash_nakade( hash, args.c ):
                    value += dict.get( _hash, 0 )
                    patterns[ _hash ] = value
            else: # 12-point diamond pattern
                for _hash in get_hash_12d( hash, args.c ):
                    #if _hash in keys:
                    #    value += dict[ _hash ]
                    value += dict.get( _hash, 0 )
                    patterns[ _hash ] = value

            print hash, value

        np.save(args.output, patterns)

        #return

        # pattern id
        patterns = {}
        number = 0

        dict = np.load(args.output).item()
        sorted_list = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)

        for x in sorted_list:
            if x[0] in patterns:
                #print 'key in patterns:', x[0], x[1]
                continue

            if x[0] < 1000000000000000L: # 3x3 pattern
                for _hash in get_hash_3x3(x[0], args.c):
                    patterns[_hash] = number
                    print_hash( _hash, '\n{0} - {1}, {2:.2f}%'.format(number, _hash, x[1]/all_move_count*100) )

            elif x[0] > 50000000000000000000L: # nakade pattern
                for _hash in get_hash_nakade(x[0], args.c):
                    patterns[_hash] = number
                    print_hash( _hash, '\n{0} - {1}, {2:.2f}%'.format(number, _hash, x[1]/all_move_count*100) )

            else: # 12-point diamond pattern
                for _hash in get_hash_12d(x[0], args.c):
                    patterns[_hash] = number
                    print_hash( _hash, '\n{0} - {1}, {2:.2f}%'.format(number, _hash, x[1]/all_move_count*100) )

            number += 1
            #print number

        np.save(args.output2, patterns)


if __name__ == '__main__':
    args = None
    #args = ['patterns/12d_01.npy', '--output', '02.npy', '--output2', '03.npy', '-c']
    go(args)
