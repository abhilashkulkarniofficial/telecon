# C Telecon

Telecon library in C

## Installation

Minimum requirements:

1. GTK3
2. Gnuplot

Suggested requirements:

1. Codeblocks

## Usage

Keep the files in root directory and include telecon in your file:

```
#include "telecon.h"
```

### GUI

Create a new user interface

```
initgui(int argc, char* argv, int height, int width, char* title);
```

Start user interface

```
startgui();
```

Add buttons:

```
addbutton(int btn_id, char* button_type, int btn_window, void (*func), pthread_t thread);
```

### Plot

Initialize Data Stream

```
init_data_stream()
```

Update Data Stream

```
update_data_stream(float* data)
```

Terminate Data Stream

```
terminate_data_stream()
```