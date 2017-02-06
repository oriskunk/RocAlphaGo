#ifndef PLINKER_H
#define PLINKER_H

void callback_get_prob(void *fp);

int engine_init(char *key, char *enginearg);
int engine_end(char *key);
int gen_move(char *key, int color);
int play(char *key, int coord, int color);
void set_size(char *key, int n);
void set_komi(char *key, int k);
void set_playout_count(char *key, int n);
void clear(char *key);

void send_data(float data[]);

#endif
