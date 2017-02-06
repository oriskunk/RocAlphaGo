from AlphaGo import go
from AlphaGo.models.policy import CNNPolicy
from operator import itemgetter
from ctypes import *
import numpy as np

policy = None

def callback_get_prob(pachi_board):

    #cast c float pointer to object of python
    array_ptr = cast(pachi_board, POINTER(c_float))
    arr = [array_ptr[i] for i in xrange(19*19*2)]

    #make state according to the pachi data array
    state = go.GameState()
    move_history = [None]*8;

    for i in xrange(19):
        for j in xrange(19):
            coord = arr[i*19+j]
            if coord > 0:
                color = go.BLACK
            elif coord < 0:
                color = go.WHITE

            if abs(coord) == 1.0:
                move = (i,j)
                state.do_move(move, color)
            elif abs(coord) > 1.0:
                move_history[int(abs(coord))-2] = [(i,j), color]

    #apply history information to state
    for i in xrange(len(move_history)):
        move_color = move_history[-(i+1)]
        if move_color is not None:
            move, color = move_color
            state.do_move(move, color)
    #print 'state history: ',state.history

    #forward state to SL policy network
    global policy
    sensible_moves = [move for move in state.get_legal_moves(include_eyes=False)]
    if len(sensible_moves) > 0:
        move_probs = policy.eval_state(state, sensible_moves)
        for xy in xrange(19*19):
            array_ptr[xy] = 0.0
        for move, prob in move_probs:
            x,y = move
            array_ptr[x*19+y] = prob
