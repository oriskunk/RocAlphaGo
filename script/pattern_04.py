import os
import numpy as np
import operator
import sys
sys.path.append(os.pardir)
sys.path.append('.')


def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("count")
    parser.add_argument("--output", default='./patterns/_04')
    args = parser.parse_args()


    if args.input:
        pattern_dict = np.load(args.input).item()
        print 'pattern count:', len(pattern_dict)

        pattern = {k: v for k, v in pattern_dict.iteritems() if v < int(args.count)}
        print 'new pattern count:', len(pattern)

        np.save(args.output, pattern)


if __name__ == '__main__':
    go()
