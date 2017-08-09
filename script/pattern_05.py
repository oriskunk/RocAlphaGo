import os
import numpy as np
import operator
import sys
sys.path.append(os.pardir)
sys.path.append('.')

from AlphaGo.models.rollout import CNNRollout


def go():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("weights")
    parser.add_argument("--index", default=4, type=int)
    parser.add_argument("--model", default='./model/rollout.json')
    parser.add_argument("--output", default='./patterns/3x3_w')
    args = parser.parse_args()


    if args.input:
        pattern_dict = np.load(args.input).item()
        print 'pattern count:', len(pattern_dict)

        policy = CNNRollout.load_model(args.model)
        policy.model.load_weights(args.weights)

        weights = policy.model.layers[0].get_weights()[0]
        print 'conv_layer_weights:', weights.shape
        print 'response:', weights[0][0]
        print 'save atari:', weights[0][1]
        print 'neighbour:', weights[0][2:4]
        #print 'nakade:', weights[0][4:571]
        #print '3x3:', weights[0][571:5071]
        #print '12d:', weights[0][5071:]

        print 'weight_index:', args.index
        pattern = {k: weights[0][args.index+v][0][0] for k, v in pattern_dict.iteritems()}
        print 'new pattern count:', len(pattern)

        for k in pattern_dict.keys():
            v = pattern_dict[k]
            w2 = pattern[k]
            w1 = weights[0][args.index+v][0][0]
            if w1 !=  w2:
                print w1, w2

        np.save(args.output, pattern)

        pattern2 = np.load(args.output+'.npy').item()
        for k in pattern_dict.keys():
            v = pattern_dict[k]
            w2 = pattern2[k]
            w1 = weights[0][args.index+v][0][0]
            if w1 !=  w2:
                print w1, w2

if __name__ == '__main__':
    go()
