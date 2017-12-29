#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "bitmap.h"

#define TESTTIME 10
#define NUMSIZE  1000000

void BitSort(char *filepath)
{
    int i;
    FILE *ifp, *ofp;

    if ((ifp = fopen(filepath, "r")) == NULL) {
        fprintf(stderr, "can't open file %s\n", filepath);
        return;
    } else if ((ofp = fopen("BitSort_numbers.txt", "w")) == NULL) {
        fprintf(stderr, "can't open file BitSort_numbers.txt\n");
        return;
    }

    init_bmp();
    while (fscanf(ifp, "%d", &i) != EOF)
        set(i);
    for (i = 0; i < UPPERBOUND; i++)
        if (test(i))
            fprintf(ofp, "%07d\n", i);
    fclose(ifp);
    fclose(ofp);
}

int intcmp(const void *p1, const void *p2)
{
    return *((int*) p1) - *((int*) p2);
}

void QuickSort(char *filepath)
{
    int i, *Nums;
    FILE *ifp, *ofp;

    if ((Nums = (int*) malloc(sizeof(int) * (NUMSIZE + 1))) == NULL) {
        fprintf(stderr, "Out of space\n");
        return;
    }

    if ((ifp = fopen(filepath, "r")) == NULL) {
        fprintf(stderr, "can't open file %s\n", filepath);
        return;
    } else if ((ofp = fopen("QSort_numbers.txt", "w")) == NULL) {
        fprintf(stderr, "can't open file QSort_numbers.txt\n");
        return;
    }

    i = 0;
    for (i = 0; fscanf(ifp, "%d", &Nums[i]) != EOF; i++)
        ;
    qsort(Nums, NUMSIZE, sizeof(int), intcmp);
    for (i = 0; i < NUMSIZE; i++)
        fprintf(ofp, "%07d\n", Nums[i]);
    free(Nums);
    fclose(ifp);
    fclose(ofp);
}

double FnTime(char *filepath, void (*fn)(char*))
{
    int i;
    double TotalClocks = 0, Start, End;

    for (i = 0; i < TESTTIME; i++) {
        Start = clock();
        fn(filepath);
        End = clock();
        TotalClocks += End - Start;
    }

    return TotalClocks / TESTTIME / CLOCKS_PER_SEC;
}

static char *filepath = "random_numbers.txt";

int main()
{
    printf("+---------+----------+\n");
    printf("|  Tool   | run time |\n");
    printf("+---------+----------+\n");
    printf("| BitSort | %.5fs |\n", FnTime(filepath, BitSort));
    printf("| QSort   | %.5fs |\n", FnTime(filepath, QuickSort));
    printf("+---------+----------+\n");
}
