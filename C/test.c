
#include <stdio.h>
#include<math.h>
#include <stdint.h>
#include <stdlib.h>
#include "telecon.h"
#include <Windows.h>
#include <stdbool.h>
#include <pthread.h>

bool run = true;
char * globalargv;
typedef struct guiparams {
    int argc;
    char *argv;
} GUIParams;

static
void *run_main_program(void *ptr){
    printf("\nIO timeout is\n");
    float LCV[12] = { 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 };
    const unsigned aiAddr[7] = { 1, 9, 2, 8, 0, 10, 11};
    float MTR[12] = { 0.0,0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0, 0.0,0.0, 0.0 };
    float CI[8] = { 0,0,0,0,0,0,0,0 };
    const float muscleTone = 0.1;
    uint32_t DO1 = 0x000000ff;

    float LCoffset[7] = { 0,0,0.1396, -0.0595, 0.078, 0, 0 };
    float lcMult[7] = { 0,0,37.21, 43.006, 35.44, 37, 0 };
    float AIoffset[7] = { 0,0,.0072,.0329,.0232, 0, 0 };
    float mtrMult[7] = { 0.1829, 0.1582, 0.2025, 0.3, 0.3,0.3,0.3 };
    float mtrOffset[7] = { 0.0585, 0.0686, 0.0519,0.055,0.055,0.055,0.055 };
    float forces[7] = { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0 };
    int maxNewt = 3;
    int counter = 20;

    float x = 0.0;
    float y = 0.0;
    float z = 0.0;
    float a = 0.0;
    int i;
    float AI;

    printf("\n\nPress enter to start DAQ\n\n");
    printf("Motor Enabled\n");

    for (i = 0; i < 12; i++) {
        MTR[i] = muscleTone;
    }
    printf("Motor Wound up\n");

    printf("\n\n\n");

    while (run)
    {
        Received *received =  rtb_receiveMsg();

            MTR[0] = received->x;
            MTR[1] = received->y;
            MTR[2] = received->z;
            MTR[3] = received->a;
            MTR[4] = received->b;
            MTR[5] = received->c;
            MTR[6] = received->d;
            MTR[7] = received->e;
            MTR[8] = received->f;
            MTR[9] = received->g;
            MTR[10] = received->h;
            MTR[11] = received->i;
            int j;
            for (j = 0; j < 12; j++) {
                MTR[j] = (MTR[j] * maxNewt) + muscleTone;
            }

            printf("Motors: %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f %2.2f\r", MTR[0], MTR[1], MTR[2], MTR[3], MTR[4], MTR[5], MTR[6], MTR[7], MTR[8], MTR[9], MTR[10], MTR[11]);
            update_plot(1, MTR);


        for (i = 0; i < 8; i++) {
            LCV[i] = CI[i];
        }
        Sleep(1);
    }

    printf("\nClosing out\n");
    for (i = 0; i < 12; i++) {
        MTR[i] = 0;
    }
    printf("\nMotor wound down\n");


    DO1 = 0x00000000;
    printf("Motor disabled\n\n");

}

static
void startup(GtkWidget *widget, gpointer callback_data){
    printf("Startup clicked Here\n");

    pthread_create((pthread_t)&callback_data, NULL, run_main_program, (void*) 0);
}

static
void terminate(GtkWidget *widget, gpointer callback_data){
    printf("Terminate clicked Here\n");

    run = false;

    terminate_data_stream();

    plot_data();
}

/*static
void *run_gui(void *ptr){
    char **arguments = (char**)ptr;
    printf("args[0] =%s\n", arguments[0]);
    initgui(1, arguments, 300, 300, "Telecon");
    addbutton(1, "Start program", 1, button_clicked, mainthread);
    startgui();

}*/



int main(int argc, char *argv[]){
    pthread_t mainthread;

    initgui(argc, argv, 300, 300, "Telecon");

    addbutton(1, "Start program", 1, startup, mainthread);

    addbutton(1, "End program", 1, terminate, mainthread);

    startgui();

    pthread_join(mainthread, NULL);

}
