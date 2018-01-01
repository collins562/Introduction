#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "bitmap.h"

#define TESTTIME 1
#define MaxPath  20

#define TRIALS 1
#define M(op)                                       \
    printf("+------------+----------+\n");          \
    printf("| TRIALS: %2d | run time |\n", TRIALS);  \
    printf("+------------+----------+\n");          \
    printf("| %-10s |", #op);                       \
    timesum = 0;                                    \
    for (ex = 0; ex < TRIALS; ex++) {               \
        start = clock();                            \
        op(filepath);                               \
        t = clock()-start;                          \
        timesum += t;                               \
    }                                               \
    nans = timesum / (TRIALS * CLOCKS_PER_SEC);     \
    printf(" %.4fs |\n", nans);                     \
    printf("+------------+----------+\n");

#define OK           0
#define FOPEN_ERROR  1
#define FSEEK_ERROR  2
#define REMOVE_ERROR 3
#define ARG_ERROR    4

int MultiPass(char *filepath);

void print_help(void);
void process_args(char *first);
void process_error(int err_code);

char *TempFiles[10];
FILE *TempPtr[10];

int Pass(FILE *ifp, int index)
{
    int i, j, Low = UPPERBOUND * index, High = Low + UPPERBOUND;
    char *tmppath = malloc(sizeof(char) * MaxPath);
    FILE *tmp;

    sprintf(tmppath, "temp%d", index);
    TempFiles[index] = tmppath;

    if ((tmp = fopen(tmppath, "w+")) == NULL)
        return FOPEN_ERROR;
    TempPtr[index] = tmp;

    init_bmp();
    while (fscanf(ifp, "%d", &i) != EOF)
        if (i >= Low && i < High)
            set(i - Low);
    for (i = 0; i < UPPERBOUND; i++)
        for (j = test(i); j > 0; j--)
            fprintf(tmp, "%d\n", i + Low);

    if (fseek(ifp, 0, SEEK_SET) != 0)
        return FSEEK_ERROR;
    return OK;
}

void ReadAndCloseTmp(FILE *ifp, FILE *ofp)
{
    int i;

    fseek(ifp, 0, SEEK_SET);
    while (fscanf(ifp, "%d", &i) != EOF)
        fprintf(ofp, "%07d\n", i);
    fclose(ifp);
}

int LoadAllTmpFiles(FILE *ofp)
{
    int i, j;
    FILE *ifp;

    for (i = 0; i < 5; i++) {
        ifp = TempPtr[i];
        if (fseek(ifp, 0, SEEK_SET) != 0)
            return FSEEK_ERROR;
        while (fscanf(ifp, "%d", &j) != EOF)
            fprintf(ofp, "%07d\n", j);
        fclose(ifp);
        if (remove(TempFiles[i]) != 0)
            return REMOVE_ERROR;
    }
    return OK;
}

int MultiPass(char *filepath)
{
    int i, err_code;
    FILE *ifp, *ofp, *tmp1, *tmp2;

    if ((ifp = fopen(filepath, "r")) == NULL)
        return FOPEN_ERROR;
    else if ((ofp = fopen("FileSort_Result.txt", "w")) == NULL)
        return FOPEN_ERROR;

    for (i = 0; i < 5; i++)
        if ((err_code = Pass(ifp, i)) != OK)
            return err_code;

    if ((err_code = LoadAllTmpFiles(ofp)) != OK)
        return err_code;

    fclose(ifp);
    fclose(ofp);
    return OK;
}

double FnTime(char *filepath)
{
    int i;
    double TotalClocks = 0, Start, End;

    for (i = 0; i < TESTTIME; i++) {
        Start = clock();
        process_error(MultiPass(filepath));
        End = clock();
        TotalClocks += End - Start;
    }

    return TotalClocks / TESTTIME / CLOCKS_PER_SEC;
}

void test_filesort(void)
{
    int ex, t, start;
    double timesum, nans;
    char *filepath = "random_numbers.txt";

    M(MultiPass);
}

/* for user interface */
void print_help(void)
{  
    puts("\nFile contents sort.\n");
    puts(" FileSort [/h]");
    puts(" FileSort [/t]\n");
    puts(" FileSort <filepath>");
    puts("  /h\tdisplay help info");
    puts("  /t\ttest FileSort implementation");
    puts("  <filepath>\t to sort the contents in file");
}

void process_args(char *first)
{
    if (strcmp(first, "/h") == 0 || strcmp(first, "/?") == 0)
        print_help();
    else if (strcmp(first, "/t") == 0)
        test_filesort();
    else
        process_error(MultiPass(first));
}

void process_error(int err_code)
{
    switch (err_code) {
        case FOPEN_ERROR:
            fprintf(stderr, "Failed to open file.\n"); break;
        case REMOVE_ERROR:
            fprintf(stderr, "Failed to remove file.\n"); break;
        case FSEEK_ERROR:
            fprintf(stderr, "Failed to seek file position.\n"); break;
        case ARG_ERROR:
            fprintf(stderr, "Invalid Argument.\n"); break;
    }
}

int main(int argc, char *argv[])
{
    switch (argc) {
        case   1: print_help(); break;
        case   2: process_args(argv[1]); break;
        default : process_error(ARG_ERROR);
    }
    return OK;
}