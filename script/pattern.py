import os
import numpy as np
import operator
import sys
sys.path.append(os.pardir)
sys.path.append('.')


#POS_3x3 = ['dd', 'db', 'bd', 'bb', 'dc', 'cd', 'cb', 'bc', 'cc']
#POS_12d = ['ec', 'dd', 'dc', 'db', 'ce', 'cd', 'cb', 'ca', 'bd', 'bc', 'bb', 'ac', 'aa']
#POS_nakade = ['ee', 'ed', 'ec', 'eb', 'ea', 'de', 'dd', 'dc', 'db', 'da', 'ce', 'cd', 'cb', 'ca', 'be', 'bd', 'bc', 'bb', 'ba', 'ae', 'ad', 'ac', 'ab', 'aa', 'cc']


_BORDER  = 1
_EMPTY   = 2
_WHITE   = 3
_BLACK   = 4

_HASHVALUE = 5#33


_C = ['  ', ' _', ' .', ' O', ' X', '0)', 'X)']
_L = ['  ', ' 1', ' 2', ' 3']
_D = [[0,0,5,0,0], [0,2,6,9,0], [1,3,0,10,12], [0,4,7,11,0], [0,0,8,0,0]]

def print_hash(hash, msg=''):

    key = hash
    c_arr, l_arr = [], []

    if hash < 1000000000000000L: # 3x3 pattern

        c_arr.append( key % _HASHVALUE )
        l_arr.append( 0 )
        key /= _HASHVALUE

        for i in xrange(8):
            l_arr.append( key % _HASHVALUE ) # LIBERTY
            key /= _HASHVALUE

            c_arr.append( key % _HASHVALUE ) # STONE
            key /= _HASHVALUE

        print msg

        #[4, 8, 3, 7, 0, 6, 2, 5, 1]:
        print '{}{}{}  {}{}{}\n{}{}{}  {}{}{}\n{}{}{}  {}{}{}'.format(\
            _C[ c_arr[4] ], _C[ c_arr[8] ], _C[ c_arr[3] ], _L[ l_arr[4] ], _L[ l_arr[8] ], _L[ l_arr[3] ],\
            _C[ c_arr[7] ], _C[ c_arr[0] ], _C[ c_arr[6] ], _L[ l_arr[7] ], _L[ l_arr[0] ], _L[ l_arr[6] ],\
            _C[ c_arr[2] ], _C[ c_arr[5] ], _C[ c_arr[1] ], _L[ l_arr[2] ], _L[ l_arr[5] ], _L[ l_arr[1] ])

    elif hash > 50000000000000000000L: # nakade pattern

        c_arr.append( int( key % _HASHVALUE ) )
        l_arr.append( 0 )
        key /= _HASHVALUE

        for i in xrange(12):
            l_arr.append( int( key % _HASHVALUE ) ) # LIBERTY
            key /= _HASHVALUE

            c_arr.append( int( key % _HASHVALUE ) ) # STONE
            key /= _HASHVALUE

        key = (hash / _HASHVALUE**24 - _HASHVALUE) / _HASHVALUE
        for i in xrange(12):
            l_arr.append( int( key % _HASHVALUE ) ) # LIBERTY
            key /= _HASHVALUE

            c_arr.append( int( key % _HASHVALUE ) ) # STONE
            key /= _HASHVALUE

        print msg

        #[]:
        print '{}{}{}{}{}  {}{}{}{}{}\n{}{}{}{}{}  {}{}{}{}{}\n{}{}{}{}{}  {}{}{}{}{}\n{}{}{}{}{}  {}{}{}{}{}\n{}{}{}{}{}  {}{}{}{}{}'.format(\
            _C[ c_arr[24] ], _C[ c_arr[23] ], _C[ c_arr[22] ], _C[ c_arr[21] ], _C[ c_arr[20] ],\
            _L[ l_arr[24] ], _L[ l_arr[23] ], _L[ l_arr[22] ], _L[ l_arr[21] ], _L[ l_arr[20] ],\
            _C[ c_arr[19] ], _C[ c_arr[18] ], _C[ c_arr[17] ], _C[ c_arr[16] ], _C[ c_arr[15] ],\
            _L[ l_arr[19] ], _L[ l_arr[18] ], _L[ l_arr[17] ], _L[ l_arr[16] ], _L[ l_arr[15] ],\
            _C[ c_arr[14] ], _C[ c_arr[13] ], _C[ c_arr[ 0] ], _C[ c_arr[12] ], _C[ c_arr[11] ],\
            _L[ l_arr[14] ], _L[ l_arr[13] ], _L[ l_arr[ 0] ], _L[ l_arr[12] ], _L[ l_arr[11] ],\
            _C[ c_arr[10] ], _C[ c_arr[ 9] ], _C[ c_arr[ 8] ], _C[ c_arr[ 7] ], _C[ c_arr[ 6] ],\
            _L[ l_arr[10] ], _L[ l_arr[ 9] ], _L[ l_arr[ 8] ], _L[ l_arr[ 7] ], _L[ l_arr[ 6] ],\
            _C[ c_arr[ 5] ], _C[ c_arr[ 4] ], _C[ c_arr[ 3] ], _C[ c_arr[ 2] ], _C[ c_arr[ 1] ],\
            _L[ l_arr[ 5] ], _L[ l_arr[ 4] ], _L[ l_arr[ 3] ], _L[ l_arr[ 2] ], _L[ l_arr[ 1] ])

    else: # 12-point diamond pattern

        y = key % _HASHVALUE# - 2
        key /= _HASHVALUE

        x = key % _HASHVALUE# - 2
        key /= _HASHVALUE

        c = key % _HASHVALUE
        #print key, x, y, c

        c_arr.append( c % 2 + _WHITE )
        l_arr.append( 0 )
        key /= _HASHVALUE
        #print key

        for i in xrange(12):
            l_arr.append( key % 5 ) # LIBERTY
            key /= _HASHVALUE
            #print key

            c_arr.append( key % 5 ) # STONE
            key /= _HASHVALUE
            #print key

        if c_arr[ _D[x][y] ] != _EMPTY:
            print 'ERROR:', _D[x][y], c_arr[ _D[x][y] ]
        else:
            #print _D[x][y]
            c_arr[ _D[x][y] ] = c + 2

        print msg

        #[]:
        print '    {}          {}\n  {}{}{}      {}{}{}\n{}{}{}{}{}  {}{}{}{}{}\n  {}{}{}      {}{}{}\n    {}          {}'.format(\
            _C[ c_arr[12] ], _L[ l_arr[12] ],\
            _C[ c_arr[11] ], _C[ c_arr[10] ], _C[ c_arr[9] ], _L[ l_arr[11] ], _L[ l_arr[10] ], _L[ l_arr[9] ],\
            _C[ c_arr[8] ], _C[ c_arr[7] ], _C[ c_arr[0] ], _C[ c_arr[6] ], _C[ c_arr[5] ],\
            _L[ l_arr[8] ], _L[ l_arr[7] ], _L[ l_arr[0] ], _L[ l_arr[6] ], _L[ l_arr[5] ],\
            _C[ c_arr[4] ], _C[ c_arr[3] ], _C[ c_arr[2] ], _L[ l_arr[4] ], _L[ l_arr[3] ], _L[ l_arr[2] ],\
            _C[ c_arr[1] ], _L[ l_arr[1] ])


def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default='./snapshot/')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if args.input:

        #ddd = {'1458808396657308047': 10000}
        #print len(ddd), type(ddd)
        #np.save(args.input, ddd)

        dict, p = {}, {}
        sorted_list = []
        all_move_count = 0

        try:
            dict = np.load(args.input).item()
            all_move_count = sum(dict.values()) * 1.0
            print 'pattern count: {},{} ({})'.format(len(dict), all_move_count, args.input)

            #p = {k: v for k, v in dict.iteritems() if v >= 5000}
            #print 'v >= 5000: {} ({})'.format(len(p), args.input)

            sorted_list = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)

        except:
            return

        for x in sorted_list:

            print_hash( x[0], '\ncount: {0}, {1:.2f}%'.format(x[1], x[1]/all_move_count*100) )


if __name__ == '__main__':
    go()
