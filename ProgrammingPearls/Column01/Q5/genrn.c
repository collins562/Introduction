#include <stdio.h>
#include <stdlib.h>

#define NUMSIZE     10000000

typedef unsigned long ULONG;

ULONG ulrand(void)
{
    return ((((ULONG) rand() << 24) & 0xff000000ul) |
            (((ULONG) rand() << 12) & 0x00fff000ul) |
            (((ULONG) rand()      ) & 0x00000ffful));
}

void Swap(int *x, int *y)
{
    int tmp = *x;
    *x = *y;
    *y = tmp;
}

// create a buf array to shuffle in place
void GenRn(void)
{
    int i;
    FILE *ofp;
    int *Buf;

    if ((Buf = (int*) malloc(sizeof(int) * NUMSIZE)) == NULL) {
        fprintf(stderr, "Out of space\n");
        return;
    } else if ((ofp = fopen("Random_Nums_3.txt", "w")) == NULL) {
        fprintf(stderr, "can't open file Random_Nums_3.txt\n");
        return;
    }

    for (i = 0; i < NUMSIZE; i++)
        Buf[i] = i;
    for (i = 0; i < NUMSIZE; i++)
        Swap(&Buf[i], &Buf[ulrand() % NUMSIZE]);
    for (i = 0; i < NUMSIZE; i++)
        fprintf(ofp, "%07d\n", Buf[i]);
    free(Buf);
    fclose(ofp);
}

int main()
{
    GenRn();
    printf("Random Numbers Generation Finished.\n");
}