import os
import unittest
import numpy as np
import sys
sys.path.append(os.pardir)
sys.path.append('.')

from AlphaGo import go
from AlphaGo.go import GameState
from AlphaGo.models.rollout import CNNRollout


class TestCNNRollout(unittest.TestCase):

    def test_copy_weights(self):

        model_file = './tests/rollout.json'
        weights_file = './tests/rollout.hdf5'

        policy = CNNRollout.load_model(model_file)
        policy.model.load_weights(weights_file)

        state = GameState()
        state.do_move(( 3, 3))
        state.do_move((15,15))
        state.do_move(( 3,15))
        state.do_move(( 5,16))
        state.do_move(( 7,16))

        print policy.preprocessor.get_feature_list()
        tensor = policy.preprocessor.state_to_tensor(state)
        output = policy.forward(tensor)

        policy2 = CNNRollout.load_model(model_file)
        output2 = policy2.forward(tensor)
        self.assertFalse(np.array_equal(output, output2))
        print output, output2

        policy2.model.layers[0].set_weights( policy.model.layers[0].get_weights() ) # Conv
        #policy2.model.layers[1].set_weights( policy.model.layers[1].get_weights() )
        policy2.model.layers[2].set_weights( policy.model.layers[2].get_weights() ) # Bias
        #policy2.model.layers[3].set_weights( policy.model.layers[3].get_weights() )

        output2 = policy2.forward(tensor)
        self.assertTrue(np.array_equal(output, output2))


    def test_change_weights(self):

        model_file = './tests/rollout.json'
        model13_file = './tests/rollout13.json'
        weights_file = './tests/rollout.hdf5'

        policy = CNNRollout.load_model(model_file)
        policy.model.load_weights(weights_file)
        policy2 = CNNRollout.load_model(model13_file)
        policy3 = CNNRollout.load_model(model13_file)

        state = GameState()
        state.do_move(( 3, 3))
        state.do_move((15,15))
        state.do_move(( 3,15))
        state.do_move(( 5,16))
        state.do_move(( 7,16))

        tensor = policy.preprocessor.state_to_tensor(state)
        output = policy.forward(tensor)
        print 'tensor.shape:', tensor.shape

        conv = policy.model.layers[0].get_weights()
        print 'conv_layer_weights:', conv[0].shape
        #print conv[0]

        p_size = [491, 4500, 2200]
        new_tensor = []
        for i in xrange(13):
            new_tensor.append(tensor[0][i])
        new_tensor = np.concatenate(new_tensor).reshape((1, 13, 19, 19)).astype(float)
        print 'new_tensor.shape:', new_tensor.shape

        fid = 10
        pid = 10
        _tensor = tensor[:,pid:pid+p_size[0],:,:]#.reshape((100, 361))
        for x in xrange(19):
            for y in xrange(19):
                 new_tensor[0][fid][x][y] = 0
                 for p in xrange( p_size[0] ):
                     if _tensor[0][p][x][y] == 1:
                         new_tensor[0][fid][x][y] = conv[0][0][4+p][0][0]
                         continue
        pid += p_size[ 0 ] 
        fid += 1

        _tensor = tensor[:,pid:pid+p_size[1],:,:]#.reshape((100, 361))
        for x in xrange(19):
            for y in xrange(19):
                 new_tensor[0][fid][x][y] = 0
                 for p in xrange( p_size[1] ):
                     if _tensor[0][p][x][y] == 1:
                         new_tensor[0][fid][x][y] = conv[0][0][pid+p][0][0]
                         continue

        pid += p_size[ 1 ]
        fid += 1

        _tensor = tensor[:,pid:pid+p_size[2],:,:]#.reshape((100, 361))
        for x in xrange(19):
            for y in xrange(19):
                 new_tensor[0][fid][x][y] = 0
                 for p in xrange( p_size[2] ):
                     if _tensor[0][p][x][y] == 1:
                         new_tensor[0][fid][x][y] = conv[0][0][pid+p][0][0]
                         continue
        fid += 1

        conv[0] = conv[0][:,:fid,:,:]
        conv[0][0][10][0][0] = 1.0
        conv[0][0][11][0][0] = 1.0
        conv[0][0][12][0][0] = 1.0
        print 'new conv_layer_weights:', conv[0].shape
        #print conv[0]
        policy2.model.layers[0].set_weights( conv ) # Conv
        policy2.model.layers[2].set_weights( policy.model.layers[2].get_weights() ) # Bias

        output2 = policy2.forward(new_tensor)
        self.assertTrue(np.array_equal(output, output2))
        #print 'output:', output
        #print 'output2:', output2

        policy2.model.save_weights('./tests/rollout13.hdf5')

        policy3.model.load_weights('./tests/rollout13.hdf5')
        output3 = policy3.forward(new_tensor)
        self.assertTrue(np.array_equal(output, output3))
        print output, output2, output3

        print 'response:  ', conv[0][0][0][0][0]
        print 'save atari:', conv[0][0][1][0][0]
        print 'neighbour: ', conv[0][0][2][0][0], conv[0][0][3][0][0]

        # neighbour
        #conv[0][0][2][0][0] /= 4.0
        #conv[0][0][3][0][0] /= 4.0
        print 'new neighbour:', conv[0][0][2][0][0], conv[0][0][3][0][0]
        policy2.model.layers[0].set_weights( conv ) # Conv
        policy2.model.layers[2].set_weights( policy.model.layers[2].get_weights() ) # Bias
        policy2.model.save_weights('./tests/rollout13.hdf5')

        '''
        tensor = policy2.preprocessor.state_to_tensor(state)

        output3 = policy2.forward(tensor)
        self.assertTrue(np.array_equal(output2, output3))
        '''


if __name__ == '__main__':
    unittest.main()
