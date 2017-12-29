#include <stdio.h>
#include <stdlib.h>
#include "bitmap.h"

#define NUMSIZE     1000000

typedef unsigned long ULONG;

ULONG ulrand(void)
{
    return ((((ULONG) rand() << 24) & 0xff000000ul) |
            (((ULONG) rand() << 12) & 0x00fff000ul) |
            (((ULONG) rand()      ) & 0x00000ffful));
}

int main()
{
    int i, rn;
    FILE *ofp;

    ofp = fopen("random_numbers.txt", "w");
    if (ofp == NULL) {
        fprintf(stderr, "can't open file random_numbers\n");
        return 1;
    }
    for (i = 0; i < NUMSIZE; i++) {
        fprintf(ofp, "%07d\n", ulrand() % UPPERBOUND);
    }
    fclose(ofp);
    printf("Finish generate random number set.\n");
    return 0;
}