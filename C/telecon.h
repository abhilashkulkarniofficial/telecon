#include <stdio.h>
#include<math.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <gtk/gtk.h>
#include <pthread.h>
#include "widgetlist.h"

typedef struct rec {
    float x,y,z,a,b,c,d,e,f,g,h,i;
} Received;


int generateData(){
    float data = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    printf("%f\n",data);
   return data;
}

FILE *fp = NULL, *plotfp = NULL;

char *GNUCommands [] = {
    "set title \"Demo\"",
    "set xrange [0:100]",
    "set style line 1 linecolor rgb '#0060ad' linetype 1 linewidth 3" ,
    "plot 'data.tmp' t 'Activation 1' with lines linestyle 1"
};

FILE *gnupipe = NULL;

int counter;

Received *rtb_receiveMsg(){
    Received *received = (Received*) malloc(sizeof(Received));
    received->x = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->y = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->z = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->a = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->b = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->c = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->d = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->e = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->f = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->g = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->h = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    received->i = (float)(0.1+((1.0*(rand() % 8000))/10000.0));
    return received;
}

static
void init_data_stream(){
    counter = 1;
    fp = fopen("activation.tmp", "w");
    plotfp = fopen("data.tmp", "w");
    gnupipe = _popen("gnuplot -persist", "w");
}

static
void update_data_stream(float* data){
    fprintf(fp, "%d\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\t%2.2f\n",
        counter,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11]
    );

    fprintf(plotfp, "%d %2.2f\n", counter, data[0]);
    counter++;
}

static
void update_plot(int plot_id, float *data){
    update_data_stream(data);
}

static
void terminate_data_stream(){
    fclose(fp);
    fclose(plotfp);
}

static
void plot_data(){
    int j;
    for(j=0; j<4; j++){
        fprintf(gnupipe, "%s\n", GNUCommands[j]);
    }
}

/* This is where the telecon library starts */

GtkWidget *window, *box, *buttonbox;
pthread_t mainthread;
int mainret;
WidgetList *wlist;


typedef struct gtkobj {
    int id;
    GtkWidget *widget;
} GtkObject;

static
void destroy(GtkWidget *widget, gpointer data)
{
    gtk_main_quit();
}


static
void initgui(int argc, char *argv[], int height, int width, char *title){
    printf("\n Initializing GUI\n");

    init_data_stream();

    gtk_init(&argc, &argv);
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), title);
    gtk_window_set_default_size(GTK_WINDOW(window), height, width);
    g_signal_connect(window, "destroy", G_CALLBACK(destroy), NULL);

    box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    gtk_container_add(GTK_CONTAINER(window), box);

    buttonbox = gtk_button_box_new(GTK_ORIENTATION_HORIZONTAL);
    gtk_box_set_spacing(GTK_BOX(buttonbox), 5);
    gtk_box_pack_start(GTK_BOX(box), buttonbox, TRUE, TRUE, 0);

}

static
void startgui(){
    printf("\n Starting GUI\n");
    gtk_widget_show_all(window);
    gtk_main();
    printf("\nEnding\n");
}

static
void addbutton(int btn_id, char *button_type, int btn_window_id, void (*func), pthread_t thread){
    printf("\n Adding a button to GUI \n");
    GtkObject *newObject = (GtkObject*) malloc(sizeof(GtkObject));

    newObject->id = btn_id;
    newObject->widget = gtk_button_new_with_label(button_type);
    g_signal_connect(GTK_BUTTON(newObject->widget), "clicked", G_CALLBACK(func), thread);

    gtk_container_add(GTK_CONTAINER(buttonbox), newObject->widget);

    /*WidgetListAppend(wlist, (void*)newObject);
    printf("Number of widgets added: %d\n", wlist->num_widgets);*/
}

void init_plot(int plot_id, char * plot_type, int plot_window_id){}

void init_slider(int slider_id, char * slider_type, int slider_window_id){}



