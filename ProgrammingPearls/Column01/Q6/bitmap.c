#include <stdio.h>
#include "bitmap.h"

void set(int i)
{
    int val, *Loc;
    int offset = (i & MASK) * DOMAINSIZE;

    Loc = &BitMap[i>>SHIFT];
    val = (*Loc & (DOMAINMASK<<offset)) + (1<<offset); 
    clr(i);
    *Loc |= val;
}

void init_bmp(void)
{
    int i;
    for (i = 0; i < 1 + UPPERBOUND*DOMAINSIZE/BITSPERWORD; i++)
        BitMap[i] = 0;
}
