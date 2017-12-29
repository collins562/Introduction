#ifndef BitMap_H

#define BITSPERWORD 32
#define MASK        7
#define DOMAINMASK  0xF
#define DOMAINSIZE  4
#define SHIFT       3
#define UPPERBOUND  2000000

int BitMap[1 + UPPERBOUND * DOMAINSIZE / BITSPERWORD];

void set(int i);
#define clr(i)  (BitMap[i>>SHIFT] &= ~(DOMAINMASK<<((i & MASK) * DOMAINSIZE)))
#define test(i) ((BitMap[i>>SHIFT]>>((i & MASK) * DOMAINSIZE)) & DOMAINMASK)

void init_bmp(void);

#endif