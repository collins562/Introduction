#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "bitmap.h"

#define TESTTIME    10
#define NUMSIZE     1000000

typedef unsigned long ULONG;

ULONG ulrand(void)
{
    return ((((ULONG) rand() << 24) & 0xff000000ul) |
            (((ULONG) rand() << 12) & 0x00fff000ul) |
            (((ULONG) rand()      ) & 0x00000ffful));
}

// exploit bitmap to check duplicate
void GenRn1(void)
{
    int i, rn;
    FILE *ofp;

    ofp = fopen("Random_Nums_1.txt", "w");
    if (ofp == NULL) {
        fprintf(stderr, "can't open file Random_Nums_1.txt\n");
        return;
    }

    init_bmp();
    for (i = 0; i < NUMSIZE; ) {
        rn = ulrand() % UPPERBOUND;
        if (test(rn))
            continue;
        set(rn);
        i++;
        fprintf(ofp, "%07d\n", rn);
    }
    fclose(ofp);
}

void Swap(int *x, int *y)
{
    int tmp = *x;
    *x = *y;
    *y = tmp;
}

// create a buf array to shuffle in place
void GenRn2(void)
{
    int i;
    FILE *ofp;
    int *Buf;

    if ((Buf = (int*) malloc(sizeof(int) * UPPERBOUND)) == NULL) {
        fprintf(stderr, "Out of space\n");
        return;
    } else if ((ofp = fopen("Random_Nums_3.txt", "w")) == NULL) {
        fprintf(stderr, "can't open file Random_Nums_3.txt\n");
        return;
    }

    for (i = 0; i < UPPERBOUND; i++)
        Buf[i] = i;
    for (i = 0; i < UPPERBOUND; i++)
        Swap(&Buf[i], &Buf[ulrand() % UPPERBOUND]);
    for (i = 0; i < NUMSIZE; i++)
        fprintf(ofp, "%07d\n", Buf[i]);
    free(Buf);
    fclose(ofp);
}

double FnTime(void (*fn)(void))
{
    double TotalClocks = 0, Start, End;
    int i;

    for (i = 0; i < TESTTIME; i++) {
        Start = clock();
        fn();
        End = clock();
        TotalClocks += End - Start;
    }
    return TotalClocks / TESTTIME / CLOCKS_PER_SEC;
}

int main()
{
    srand(time(NULL));
    printf("+--------+----------+\n");
    printf("|  Tool  | run time |\n");
    printf("+--------+----------+\n");
    printf("| GenRn1 | %.5fs |\n", FnTime(GenRn1));
    printf("| GenRn2 | %.5fs |\n", FnTime(GenRn2));
    printf("+--------+----------+\n");
    
}