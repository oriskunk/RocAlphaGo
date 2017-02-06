"""Policy players"""
import numpy as np
from operator import itemgetter
from AlphaGo import go
from AlphaGo import mcts
from ctypes import *

import os
import sys
sys.path.append(os.environ['NGO_HOME']+'/pachi/')
from policy_extractor import callback_get_prob
import policy_extractor

import logging
logging.basicConfig(filename='ngo.log', level=logging.DEBUG)

class GreedyPolicyPlayer(object):
    """A player that uses a greedy policy (i.e. chooses the highest probability
       move each turn)
    """

    def __init__(self, policy_function, pass_when_offered=False, move_limit=None):
        self.policy = policy_function
        self.pass_when_offered = pass_when_offered
        self.move_limit = move_limit

    def get_move(self, state):
        # check move limit
        if self.move_limit is not None and len(state.history) > self.move_limit:
            return go.PASS_MOVE

        # check if pass was offered and we want to pass
        if self.pass_when_offered:
            if len(state.history) > 100 and state.history[-1] == go.PASS_MOVE:
                return go.PASS_MOVE

        # list with sensible moves
        sensible_moves = [move for move in state.get_legal_moves(include_eyes=False)]

        # check if there are sensible moves left to do
        if len(sensible_moves) > 0:
            move_probs = self.policy.eval_state(state, sensible_moves)
            max_prob = max(move_probs, key=itemgetter(1))
            return max_prob[0]

        # No 'sensible' moves available, so do pass move
        return go.PASS_MOVE


class ProbabilisticPolicyPlayer(object):
    """A player that samples a move in proportion to the probability given by the
       policy.
       By manipulating the 'temperature', moves can be pushed towards totally random
       (high temperature) or towards greedy play (low temperature)
    """

    def __init__(self, policy_function, temperature=1.0, pass_when_offered=False,
                 move_limit=None, greedy_start=None):
        assert(temperature > 0.0)
        self.policy = policy_function
        self.move_limit = move_limit
        self.beta = 1.0 / temperature
        self.pass_when_offered = pass_when_offered
        self.greedy_start = greedy_start

    def apply_temperature(self, distribution):
        log_probabilities = np.log(distribution)
        # apply beta exponent to probabilities (in log space)
        log_probabilities = log_probabilities * self.beta
        # scale probabilities to a more numerically stable range (in log space)
        log_probabilities = log_probabilities - log_probabilities.max()
        # convert back from log space
        probabilities = np.exp(log_probabilities)
        # re-normalize the distribution
        return probabilities / probabilities.sum()

    def get_move(self, state):
        # check move limit
        if self.move_limit is not None and len(state.history) > self.move_limit:
            return go.PASS_MOVE

        # check if pass was offered and we want to pass
        if self.pass_when_offered:
            if len(state.history) > 100 and state.history[-1] == go.PASS_MOVE:
                return go.PASS_MOVE

        # list with 'sensible' moves
        sensible_moves = [move for move in state.get_legal_moves(include_eyes=False)]

        # check if there are 'sensible' moves left to do
        if len(sensible_moves) > 0:

            move_probs = self.policy.eval_state(state, sensible_moves)

            if self.greedy_start is not None and len(state.history) >= self.greedy_start:
                # greedy

                max_prob = max(move_probs, key=itemgetter(1))
                return max_prob[0]
            else:
                # probabilistic

                # zip(*list) is like the 'transpose' of zip;
                # zip(*zip([1,2,3], [4,5,6])) is [(1,2,3), (4,5,6)]
                moves, probabilities = zip(*move_probs)
                # apply 'temperature' to the distribution
                probabilities = self.apply_temperature(probabilities)
                # numpy interprets a list of tuples as 2D, so we must choose an
                # _index_ of moves then apply it in 2 steps
                choice_idx = np.random.choice(len(moves), p=probabilities)
                return moves[choice_idx]

        # No 'sensible' moves available, so do pass move
        return go.PASS_MOVE

    def get_moves(self, states):
        """Batch version of get_move. A list of moves is returned (one per state)
        """
        sensible_move_lists = [[move for move in st.get_legal_moves(include_eyes=False)]
                               for st in states]
        all_moves_distributions = self.policy.batch_eval_state(states, sensible_move_lists)
        move_list = [None] * len(states)
        for i, move_probs in enumerate(all_moves_distributions):
            if len(move_probs) == 0 or len(states[i].history) > self.move_limit:
                move_list[i] = go.PASS_MOVE
            else:
                if self.greedy_start is not None and len(states[i].history) >= self.greedy_start:
                    # greedy

                    max_prob = max(move_probs, key=itemgetter(1))
                    move_list[i] = max_prob[0]
                else:
                    # probabilistic

                    moves, probabilities = zip(*move_probs)
                    # apply 'temperature' to the distribution
                    probabilities = self.apply_temperature(probabilities)
                    # numpy interprets a list of tuples as 2D, so we must choose an
                    # _index_ of moves then apply it in 2 steps
                    choice_idx = np.random.choice(len(moves), p=probabilities)
                    move_list[i] = moves[choice_idx]
        return move_list


class MCTSPlayer(object):
    def __init__(self, value_function, policy_function, rollout_function, lmbda=.5, c_puct=5,
                 rollout_limit=500, playout_depth=40, n_playout=100):
        self.mcts = mcts.MCTS(value_function, policy_function, rollout_function, lmbda, c_puct,
                              rollout_limit, playout_depth, n_playout)

    def get_move(self, state):
        sensible_moves = [move for move in state.get_legal_moves(include_eyes=False)]
        if len(sensible_moves) > 0:
            move = self.mcts.get_move(state)
            self.mcts.update_with_move(move)
            return move
        # No 'sensible' moves available, so do pass move
        return go.PASS_MOVE


class PachiPlayer(object):

    def __init__(self, policy_function, pass_when_offered=False, move_limit=None, engine='', playout_count=0):
        logging.debug('PachiPlayer:__init__ - pc[%d]', playout_count)
        self.policy = policy_function
        self.pass_when_offered = pass_when_offered
        self.move_limit = move_limit
        self.plinker = cdll.LoadLibrary(os.environ['NGO_HOME']+'/pachi/libplinker.so')
        self.CWRAPPER_GET_PROB = CFUNCTYPE(None, POINTER(c_float))
        self.wrapped_callback_get_prob = self.CWRAPPER_GET_PROB(callback_get_prob)
        self.plinker.callback_get_prob(self.wrapped_callback_get_prob)
        self.plinker.engine_init(str(id(self)), engine)
        self.plinker.set_playout_count(str(id(self)), playout_count)
        policy_extractor.policy = self.policy

    def get_move(self, state):
        if self.move_limit is not None and len(state.history) > self.move_limit:
            return go.PASS_MOVE
        if self.pass_when_offered:
            if len(state.history) > 100 and state.history[-1] == go.PASS_MOVE:
                return go.PASS_MOVE

        move = self.plinker.gen_move(str(id(self)), state.current_player)
        logging.debug('_move_[%d]', move)
        if move == -1:
            return go.PASS_MOVE
        elif move == -2:
            return go.PASS_MOVE
            #return go.RESIGN_MOVE

        return (move/100-1, move%100-1)

    def make_move(self, move, color=go.BLACK):
        if (move == go.PASS_MOVE):
            self.plinker.play(str(id(self)), -1, color)
        else:
            self.plinker.play(str(id(self)), (move[0]+1)*100 + move[1]+1, color)

    def set_size(self, n):
        self.plinker.set_size(str(id(self)), n)

    def set_komi(self, k):
        self.plinker.set_komi(str(id(self)), int(k*10))

    def clear(self):
        self.plinker.clear(str(id(self)))

    def __del__(self):
        logging.debug('PachiPlayer:__del__')
        self.plinker.engine_end(str(id(self)))
