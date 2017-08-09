import os
import numpy as np
import sys


def walk_all(root, ext):
    for (dirpath, dirname, files) in os.walk(root):
        for fname in files:
            if fname.strip()[-len(ext):] == ext:
                yield os.path.join(dirpath, fname)

def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("npy_dir")
    args = parser.parse_args()


    mse = { x:0 for x in xrange(500) }
    cnt = { x:0 for x in xrange(500) }
    for f in walk_all( args.npy_dir, '.npy' ):

        print 'load file:', f
        for x in np.load( f ).item().items():

            mse[ x[ 0]] += x[ 1]
            cnt[ x[ 0]] += 1

    for x in xrange( len( mse ) ):

        if cnt[ x] > 0:
            print mse[ x] / cnt[ x]
        else:
            print 0.0


if __name__ == '__main__':
    go()
