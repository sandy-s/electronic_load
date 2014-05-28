#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
import time
import Array3700

x_margin = 30
y_margin = 0.3

class BatteryTester:
    def __init__(self):
        self.instrument = Array3700.Array3700('/dev/ttyUSB13', 19200, 1) # TODO: make configurable from GUI
        self.instrument.update_status()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(800, 600);
        self.window.connect("destroy", lambda wid: gtk.main_quit())
        self.window.connect("delete_event", lambda a1,a2:gtk.main_quit())

        vbox1 = gtk.VBox(False, 10)
        hbox1 = gtk.HBox(False, 10);
        vbox1.pack_start(hbox1, False, False)
        self.window.add(vbox1)

        vbox2 = gtk.VBox(False, 10)
        vbox3 = gtk.VBox(False, 10)
        vbox4 = gtk.VBox(False, 10)
        vbox5 = gtk.VBox(False, 10)

        self.voltage = gtk.Label()
        frame = gtk.Frame("Voltage, V")
        frame.add(self.voltage)
        vbox2.pack_start(frame, False, False, 10)

        self.current = gtk.Label()
        frame = gtk.Frame("Current, A")
        frame.add(self.current)
        vbox2.pack_start(frame, False, False, 10)

        self.power = gtk.Label()
        frame = gtk.Frame("Power, W")
        frame.add(self.power)
        vbox2.pack_start(frame, False, False, 10)

        halign1 = gtk.Alignment(0, 1, 0, 0)
        halign1.add(vbox2)
        hbox1.pack_start(halign1)

        self.resistance = gtk.Label()
        frame = gtk.Frame("Resistance, Ohm")
        frame.add(self.resistance)
        vbox3.pack_start(frame, False, False, 10)

        self.max_current = gtk.Label()
        frame = gtk.Frame("Max Current, A")
        frame.add(self.max_current)
        vbox3.pack_start(frame, False, False, 10)

        self.max_power = gtk.Label()
        frame = gtk.Frame("Max Power, W")
        frame.add(self.max_power)
        vbox3.pack_start(frame, False, False, 10)

        halign1 = gtk.Alignment(0, 1, 0, 0)
        halign1.add(vbox3)
        hbox1.pack_start(halign1)

        self.local = gtk.Label()
        frame = gtk.Frame("Control")
        frame.add(self.local)
        vbox4.pack_start(frame)

        self.on = gtk.Label()
        frame = gtk.Frame("Output")
        frame.add(self.on)
        vbox4.pack_start(frame)

        halign2 = gtk.Alignment(0, 1, 0, 0)
        halign2.add(vbox4)
        hbox1.pack_start(halign2)

        start_button = gtk.Button("Start")
        start_button.connect("clicked", self.start_button_clicked)
        vbox5.pack_start(start_button)

        stop_button = gtk.Button("Stop")
        stop_button.connect("clicked", self.stop_button_clicked)
        vbox5.pack_start(stop_button)

        halign3 = gtk.Alignment(0, 1, 0, 0)
        halign3.add(vbox5)
        hbox1.pack_start(halign3)

        fig, ax = plt.subplots()
        self.axes = ax
        self.figure = fig
        self.clear_plot()
        fc = FigureCanvas(fig)
        vbox1.pack_start(fc)

        self.started = False
        gtk.timeout_add(1000, self.update)
        self.window.show_all()

    def update(self):
        self.instrument.update_status()
        voltage = self.instrument.get_voltage_mv() / 1000.0
        current = self.instrument.get_current_ma() / 1000.0
        power = self.instrument.get_power_mw() / 1000.0
        resistance = self.instrument.get_resistance_mohm() / 1000.0
        max_current = self.instrument.get_max_current_ma() / 1000.0
        max_power = self.instrument.get_max_power_mw() / 1000.0
        state = self.instrument.get_output_state()
        self.voltage.set_label('{:.3f}'.format(voltage))
        self.current.set_label('{:.3f}'.format(current))
        self.power.set_label('{:.1f}'.format(power))
        self.resistance.set_label('{:.2f}'.format(resistance))
        self.max_current.set_label('{:.3f}'.format(max_current))
        self.max_power.set_label('{:.1f}'.format(max_power))

        if state & 1:
            self.local.set_label('remote')
        else:
            self.local.set_label('local')

        if state & 2:
            self.on.set_label('on')
        else:
            if self.on.get_label() == 'on':
                self.stop()
            self.on.set_label('off')

        if not(self.started):
            return True

        self.file.write(','.join([str(time.time()), str(voltage), str(current), str(power)]))
        self.file.write('\n')
        self.file.flush()

        secs = time.time() - self.starttime
        self.x.append(secs)
        self.y.append(voltage)
        if voltage > self.max_y:
            self.max_y = voltage
        self.data.set_data(self.x, self.y)
        xlim = x_margin * (int(secs) / x_margin + 1)
        self.axes.set_xlim(0, xlim);
        self.axes.set_ylim(0, self.max_y + y_margin);
        self.figure.canvas.draw()
        return True

    def clear_plot(self):
        self.axes.clear()
        self.axes.set_xlabel("Time, sec");
        self.axes.set_ylabel("Voltage, V");


    def start_button_clicked(self, widget, data=None):
        self.x = [0]
        self.y = [self.instrument.get_voltage_mv() / 1000.0]
        self.max_y = 0;
        self.starttime = time.time()
        self.clear_plot()
        self.data = self.axes.plot(self.x, self.y , 'r-', linewidth = 2)[0]
        self.file = open('battery_tester.csv', 'w') # TODO: add a dialog for file name
        self.started = True

    def stop_button_clicked(self, widget, data=None):
        self.stop()

    def stop(self):
        if self.started:
            self.file.close()
            self.started = False

    def main(self):
        gtk.main()

print __name__
if __name__ == "__main__":
    app = BatteryTester()
    app.main()
