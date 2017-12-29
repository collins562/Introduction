#ifndef BitMap_H

#define BITSPERWORD 32
#define MASK        0x1F
#define SHIFT       5
#define UPPERBOUND  8000000

int BitMap[1 + UPPERBOUND / BITSPERWORD];

#define set(i)  BitMap[i>>SHIFT] |=  (1<<(i & MASK))
#define clr(i)  BitMap[i>>SHIFT] &= ~(1<<(i & MASK))
#define test(i) BitMap[i>>SHIFT] &   (1<<(i & MASK))

void init_bmp(void);

#endif