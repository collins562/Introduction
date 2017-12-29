#include "bitmap.h"

void init_bmp(void)
{
    int i;
    for (i = 0; i < 1 + UPPERBOUND/BITSPERWORD; i++)
        BitMap[i] = 0;
}