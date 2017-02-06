#define DEBUG
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unordered_map>

extern "C" {
#include "plinker.h"
#include "board.h"
#include "debug.h"
#include "engine.h"
#include "tactics/selfatari.h"
#include "tactics/dragon.h"
#include "tactics/ladder.h"
#include "tactics/1lib.h"
#include "random.h"
#include "playout.h"
#include "timeinfo.h"
#include "playout/moggy.h"
#include "replay/replay.h"
#include "uct/uct.h"
#include "montecarlo/montecarlo.h"
} /* extern "C" */
#include "dcnn.h"

int debug_level = 0;
bool debug_boardprint = true;
long verbose_logs = 0;

std::unordered_map<std::string, struct board*> BoardMap;
std::unordered_map<std::string, struct engine*> EngineMap;
std::unordered_map<std::string, struct time_info> TimeInfoMap;

struct time_info g_ti_default = { .period = time_info::time_period::TT_NULL };

void *g_fp_get_prob = NULL;

typedef void (*_callback_get_prob)(float *n);
void callback_get_prob(void *fp)
{
    g_fp_get_prob = fp;
}


int engine_init(char* key, char *enginearg)
{
    //printf("__engine_init__ [%s]\n", _engine);
    struct board *_board = board_init(NULL);
    board_resize(_board, 19);
    board_clear(_board);
    struct engine *_engine = engine_uct_init(enginearg, _board);
    struct time_info _timeInfo;
    _timeInfo = g_ti_default;

    BoardMap[std::string(key)] = _board;
    EngineMap[std::string(key)] = _engine;
    TimeInfoMap[std::string(key)] = _timeInfo;

    return 0;
}

int engine_end(char *key)
{
    struct board *_board = BoardMap[std::string(key)];
    struct engine *_engine = EngineMap[std::string(key)];

    board_done_noalloc(_board);
    engine_done(_engine);

    BoardMap.erase(std::string(key));
    EngineMap.erase(std::string(key));
    TimeInfoMap.erase(std::string(key));

    return 0;
}

int gen_move(char *key, int color)
{
    struct board *_board = BoardMap[std::string(key)];
    struct engine *_engine = EngineMap[std::string(key)];
    struct time_info _timeInfo = TimeInfoMap[std::string(key)];

    //printf("__genmove__ %d, %d, %d\n", _engine, _board, color);
    coord_t* c = NULL;
    stone _color = S_NONE;
    if (color == 1)
        _color = S_BLACK;
    else if (color == -1)
        _color = S_WHITE;

    c = _engine->genmove(_engine, _board, &_timeInfo, _color, 0);
    struct move m = { *c, _color };
    int ret = board_play(_board, &m);
    if (m.coord == -1 || m.coord == -2)
    {
        coord_done(c);
        return m.coord;
    }

    int x = coord_x(*c, _board);
    int y = coord_y(*c, _board);
    int xy = 100 * x+y;

    coord_done(c);
    engine_board_print(_engine, _board, stderr);
    return xy;
}

int play(char *key, int coord, int color)
{
    struct board *_board = BoardMap[std::string(key)];
    struct engine *_engine = EngineMap[std::string(key)];

    //printf("__play__ %s, %d\n", str, color);
    struct move m;
    if (color == 1)
        m.color = S_BLACK;
    else if (color == -1)
        m.color = S_WHITE;
    else
        m.color = S_NONE;
    if (coord != -1)
    {
        int x = coord / 100;
        int y = coord % 100;
        coord_t *c = coord_init(x, y, 21);
        m.coord = *c; coord_done(c);
    } else
    {
        coord_t c = -1;
        m.coord = c;
    }
    char *enginearg = NULL;
    if (_engine->notify_play != 0)
        _engine->notify_play(_engine, _board, &m, enginearg);
    int ret = board_play(_board, &m);
    //printf("\tboard_play: %d\n", ret);
    //engine_board_print(_engine, _board, stderr);
    return ret;
}

void set_size(char *key, int n)
{
    struct board *_board = BoardMap[std::string(key)];

    board_resize(_board, n);
    board_clear(_board);
}

void setkomi(char *key, int k)
{
    struct board *_board = BoardMap[std::string(key)];

    _board->komi = k / 10.0;
}

void set_playout_count(char *key, int n)
{
    if (n > 0)
    {
        struct time_info _timeInfo = TimeInfoMap[std::string(key)];
        _timeInfo.dim = time_info::time_dimension::TD_GAMES;
        _timeInfo.len.games = n;
        _timeInfo.period = time_info::time_period::TT_MOVE;

        TimeInfoMap[std::string(key)] = _timeInfo;
    }
}

void clear(char *key)
{
    struct board *_board = BoardMap[std::string(key)];

    board_clear(_board);
}

//send board data to NGo module
void send_data(float data[])
{
    if(g_fp_get_prob != NULL)
    {
        ((_callback_get_prob)g_fp_get_prob)(data);
    }
}
