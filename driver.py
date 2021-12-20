import os
import pprint
import random
import sys
from matplotlib.pyplot import ylabel
import wx
import time

import matplotlib
from wx.core import Size
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab

TIMER_ID1 = 2000

class RandomDataGen(object):
    def __init__(self, init=50):
        self.data = self.init = init

    def next(self):
        self._recalc_data()
        return self.data

    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8:
            delta += (0.5 if self.init > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta


class BoundControlBox(wx.Panel):
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.radio_auto = wx.RadioButton(self, -1, label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1, label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, size=(35,-1), value=str(initval), style=wx.TE_PROCESS_ENTER)
        

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

        
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())

    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()

    def is_auto(self):
        return self.radio_auto.GetValue()

    def manual_value(self):
        return self.value
    
class Values(wx.Panel):
    def __init__(self, parent, ID, label, color):
        wx.Panel.__init__(self, parent, ID)
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.expected = wx.StaticText(self, label ="Expected Value:")
        self.expected.SetForegroundColour(color)
        # self.actual = wx.StaticText(self, label ="Actual Value:")
        
        sizer.Add(self.expected, 0, wx.ALL, 10)
        # sizer.Add(self.actual, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def update_values(self, expected, actual):
        self.expected.SetLabel(expected)
        # self.actual.SetLabel("Actual Value:"+actual)
        
    def set_textColor(self, color):
        self.expected.SetForegroundColour(color)



class GraphFrame(wx.Frame):
    """ 
    The main frame of the application
    """
    title ='Telecon Module'

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title, size=(600,500))      
        self.data = []  
        self.color =[]
        self.name = []
        
    def add_plots(self, color, name):
        self.datagen = RandomDataGen()
        self.color.append(color)
        self.data.append([self.datagen.next()])
        self.name.append(name)
        

    def create_menu(self):
        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
        self.val_box = []
        for i,x in enumerate(self.name):
            self.val_box.append(Values(self.panel, -1, x, self.color[i]))

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)

        self.cb_grid = wx.CheckBox(self.panel, -1,  "Show Grid", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)

        self.cb_xlab = wx.CheckBox(self.panel, -1, "Show X labels", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)
        self.cb_xlab.SetValue(True)
        
                
        self.refresh = {"1 Sec":1000, "100 MSec":100, "10 MSec":10, "1 MSec":1} 
        print(self.refresh.keys())
        self.combo = wx.ComboBox(self.panel,choices = list(self.refresh.keys()), value="Refresh Rate", style=wx.CB_READONLY)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        # self.sld.Bind(wx.EVT_SLIDER, self.OnSliderScroll)
        self.hbox1.Add(self.combo,1,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.TOP, border = 5) 

        self.vbox1 = wx.BoxSizer(wx.VERTICAL)
        for x in self.val_box:
            self.vbox1.Add(x, border=5, flag=wx.ALL)
        
        self.vbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox2.Add(self.canvas, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox2.Add(self.vbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.vbox2, 1, flag=wx.LEFT | wx.TOP | wx.GROW, border = 10)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP, border = 10)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP, border = 10)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.combo.Bind(wx.EVT_COMBOBOX, self.OnCombo)
      
    def OnCombo(self, event): 
        self.redraw_timer.Start(self.refresh[self.combo.GetValue()])
        
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((6.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Encoder Data', size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        self.plot_data = []
        for i,data in enumerate(self.data):
            self.plot_data.append(self.axes.plot( data, linewidth=1, color=self.color[i], )[0])

    def draw_plot(self):
        """ Redraws the plot
        """
        if self.xmax_control.is_auto():
            xmax = len(self.data[0]) if len(self.data[0]) > 50 else 50
        else:
            xmax = int(self.xmax_control.manual_value())

        if self.xmin_control.is_auto():
            xmin = xmax - 50
        else:
            xmin = int(self.xmin_control.manual_value())

        if self.ymin_control.is_auto():
            ymin = round(min(self.data[0]), 0) - 1
        else:
            ymin = int(self.ymin_control.manual_value())

        if self.ymax_control.is_auto():
            ymax = round(max(self.data[0]), 0) + 1
        else:
            ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        pylab.setp(self.axes.get_xticklabels(),
            visible=self.cb_xlab.IsChecked())

        for i,plot in enumerate(self.plot_data):
            plot.set_xdata(np.arange(len(self.data[i])))
            plot.set_ydata(np.array(self.data[i]))
            self.val_box[i].update_values(str( round(self.data[i][len(self.data[i])-1],3)), "0")
        # self.st.SetLabel("Value: "+str( round(self.data[0][len(self.data[0])-1],3)))

        self.canvas.draw()

    def on_pause_button(self, event):
        self.paused = not self.paused

    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog( self, message="Save plot as...", defaultDir=os.getcwd(), defaultFile="plot.png", wildcard=file_choices, style=wx.FC_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)

    def on_redraw_timer(self, event):
        if not self.paused:
            for x in self.data:
                x.append(self.datagen.next())

        self.draw_plot()

    def on_exit(self, event):
        self.Destroy()

    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(  wx.EVT_TIMER, self.on_flash_status_off, self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)

    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')
        
    def set_chart_params(self, ylabel):
        self.paused = False

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(1000)
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlabel("Time")


if __name__ == '__main__':
    app = wx.App()
    app.frame = GraphFrame()
    app.frame.add_plots("blue", name="Force")
    app.frame.add_plots("red", name="Tension")
    app.frame.set_chart_params("Values")
    app.frame.Show()
    app.MainLoop()