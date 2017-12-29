#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "bitmap.h"

#define TESTTIME 1
#define NUMSIZE  1000000

#define OK           0
#define FOPEN_ERROR  1
#define FSEEK_ERROR  2
#define REMOVE_ERROR 3
#define ARG_ERROR    4

#define TEMPFILE1 "filesort_temp_1.txt"
#define TEMPFILE2 "filesort_temp_2.txt"

int TwoPass(char *filepath);

void print_help(void);
void process_args(char *first);
void process_error(int err_code);

int Pass(FILE *ifp, FILE *ofp, int index)
{
    int i, Low = UPPERBOUND * index, High = Low + UPPERBOUND;

    init_bmp();
    while (fscanf(ifp, "%d", &i) != EOF)
        if (i >= Low && i < High)   // [Low, High)
            set(i - Low);
    for (i = 0; i < UPPERBOUND; i++)
        if (test(i))
            fprintf(ofp, "%07d\n", i + Low);
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

int TwoPass(char *filepath)
{
    int err_code;
    FILE *ifp, *ofp, *tmp1, *tmp2;

    if ((ifp = fopen(filepath, "r")) == NULL) {
        return FOPEN_ERROR;
    } else if ((ofp = fopen("FileSort_Result.txt", "w")) == NULL) {
        return FOPEN_ERROR;
    } else if ((tmp1 = fopen(TEMPFILE1, "w+")) == NULL) {
        return FOPEN_ERROR;
    } else if ((tmp2 = fopen(TEMPFILE2, "w+")) == NULL) {
        return FOPEN_ERROR;
    }

    if ((err_code = Pass(ifp, tmp1, 0)) != OK || 
        (err_code = Pass(ifp, tmp2, 1)) != OK)
        return err_code;

    ReadAndCloseTmp(tmp1, ofp);
    ReadAndCloseTmp(tmp2, ofp);

    if (remove(TEMPFILE1) != 0 || remove(TEMPFILE2) != 0)
        return REMOVE_ERROR;
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
        TwoPass(filepath);
        End = clock();
        TotalClocks += End - Start;
    }

    return TotalClocks / TESTTIME / CLOCKS_PER_SEC;
}

static char *filepath = "Random_Nums.txt";

void test_twopass(void)
{
    printf("+-----------+----------+\n");
    printf("|   Tool    | run time |\n");
    printf("+-----------+----------+\n");
    printf("| MultiPass | %.3f s |\n", FnTime(filepath));
    printf("+-----------+----------+\n");
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
        test_twopass();
    else
        process_error(TwoPass(first));
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
        default:
            fprintf(stderr, "Unknown Error.\n");
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