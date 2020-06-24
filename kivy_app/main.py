from kivy.app import App

from kivy.core.window import Window
from kivy.core.window import WindowBase

from kivy.clock import Clock

from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty

from kivy.uix.boxlayout import BoxLayout

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.bubble import Bubble
from kivy.uix.bubble import BubbleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup

from math import sin, nan, cos
import time
import serial

from kivy_garden.graph import Graph, LinePlot

class GraphWidget(Graph):
    plotColor = ListProperty([1, 0, 0, 1])
    
    def __init__(self, **kwargs):
        super(GraphWidget, self).__init__(**kwargs)
        
        # if 'plotColor' in kwargs:
        #     self.plotColor = kwargs['plotColor']
        # else:
        #     self.plotColor = [1, 0, 0, 1]
        self.plot = LinePlot(color=self.plotColor, line_width=1)
        self.plot.points = [(x/50, nan) for x in range(0, 500)]
        self.insertIndex = 0
        self.add_plot(self.plot)
        self.filter = None
        
    def addPoints(self, points):
        blankOutInt = 25
        
        for p in points:
            if not self.filter:
                self.filter = [p for x in range(10)]
            self.filter.append(p)
            self.filter = self.filter[1:]
            p2 = sum(self.filter) / len(self.filter)
            
            self.plot.points[self.insertIndex] = (self.plot.points[self.insertIndex][0], p2)
            try:
                self.plot.points[self.insertIndex+blankOutInt] = (self.plot.points[self.insertIndex+blankOutInt][0], nan)
            except:
                self.plot.points[self.insertIndex+blankOutInt-len(self.plot.points)] = (self.plot.points[self.insertIndex+blankOutInt-len(self.plot.points)][0], nan)
            
            self.insertIndex += 1
            if self.insertIndex >= len(self.plot.points):
                self.insertIndex -= len(self.plot.points)
        
        # numPts = len(points)
        # curr = self.plot.points[self.insertIndex:self.insertIndex+numPts]
        # xRange = [curr[x][0] for x in range(len(curr))]
        # newPts = list(zip(xRange, points))
        # self.plot.points[self.insertIndex:self.insertIndex + numPts] = newPts
        # self.insertIndex = self.insertIndex + numPts
        
    def reset(self):
        self.plot.points = [(x/50, nan) for x in range(0, 500)]
        self.insertIndex = 0
        
class SettingView(ToggleButton):
    parameter = StringProperty("Parameter")
    formatStr = StringProperty("%d")
    value = NumericProperty(0)
    minVal = NumericProperty(0)
    maxVal = NumericProperty(0)
    delta = NumericProperty(1)
    unit = StringProperty("unit")
    
    def __init__(self, **kwargs):
        super(SettingView, self).__init__(**kwargs)
        
        self.register_event_type('on_change')
        
        self.text = ("[size=60]"+self.formatStr+"[/size][size=15]%s[/size]\n[size=20]%s[/size]") % (self.value, self.unit, self.parameter)
        self.valign = 'bottom'
        self.halign = 'center'
        self.markup = True

    def decr(self, evt):
        if self.value > self.minVal:
            self.value = self.value - self.delta
            self.text = ("[size=60]"+self.formatStr+"[/size][size=15]%s[/size]\n[size=20]%s[/size]") % (self.value, self.unit, self.parameter)
    
    def incr(self, evt):
        if self.value < self.maxVal:
            self.value = self.value + self.delta
            self.text = ("[size=60]"+self.formatStr+"[/size][size=15]%s[/size]\n[size=20]%s[/size]") % (self.value, self.unit, self.parameter)
    
    def on_state(self, widget, state):
        # super(SettingView, self).on_state(**kwargs)
        
        if self.state == 'down':
            bubbleHeight = 50
            self.bubble = Bubble(size_hint=(None,None), size=(self.width, bubbleHeight), center_x=self.center_x, y=self.height-bubbleHeight)
            b1 = BubbleButton(text="-", font_size=40)
            b1.bind(on_press = self.decr)
            b2 = BubbleButton(text="+", font_size=40)
            b2.bind(on_press = self.incr)
            self.text_size = self.size
            self.text_size[1] -= 10
            self.valign='bottom'
            self.bubble.add_widget(b1)
            self.bubble.add_widget(b2)

            self.add_widget(self.bubble)
        else:
            self.remove_widget(self.bubble)
            self.valign='center'
            self.dispatch('on_change', self.value)
            
    def on_change(self, event):
        pass

class VentilatorApp(App):
    rawData1 = [300*(sin(x / 10)+1) for x in range(0, 10000)]
    rawData2 = [20*(cos(x / 10)+1) for x in range(0, 10000)]
    idx = 0
    running = False
    serialBuffer = b""
    PMax = -10000
    VMax = -10000
    alert = None
    
    # Pressure = (AIN-A0) * (5/1023) * (30.6/3);
    # Volume = (1033/(1033+P)) * K (AIN - A0);
    
    def plotCallback(self, dt):
        if self.running:
            self.VtGraph.addPoints(self.rawData1[self.idx:self.idx+5])
            self.PawGraph.addPoints(self.rawData2[self.idx:self.idx+5])
            self.idx += 5
            
    def dismissAlert(self, event):
        if self.alert:
            self.alert.dismiss()
            self.alert = None
            
    def setAlert(self, message):
        if self.alert is None:
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=message, font_size=20))
            b = Button(text='Dismiss', font_size=20, size_hint_y=0.4)
            content.add_widget(b)
            self.alert = Popup(title="ALERT!", title_color=[1,1,0,1], 
                        title_size=25, title_align='center',
                        separator_color=[1,0,0,1],
                        content=content, auto_dismiss=False, 
                        size_hint=(0.5,0.3),
                        background = 'red_background.png')
            b.bind(on_press=self.dismissAlert)
            self.alert.open()
            
    def serialCallback(self, dt):
        # Read all available data from the serial port
        rawData = self.serial.read(self.serial.in_waiting)
        self.serialBuffer += rawData
        dataPoints = self.serialBuffer.split(b'\r\n')
        self.serialBuffer = dataPoints[-1]
        dataPoints = dataPoints[:-1]
        
        VtData = []
        PawData = []
        
        for pt in dataPoints:
            try:
                vals = [int(x) for x in pt.split(b',')]
            except:
                continue
            
            if len(vals) != 3:
                continue
            
            # Still need to calibrate the volume measurement
            Paw = (vals[1]-216) * (5.0/1023.0) * (30.6/3.0)
            
            X = vals[0] - 400   # Switch zero point is at approx 240
            if X < 0:
                X = 0

            # Curve fit of bag volume vs arm position
            Volume = (-0.0001*X*X*X +0.0323*X*X -0.2624*X +1.0506)
            if Volume < 0:
                Volume = 5
            
            # Fudging with values for display
            Paw = 1*Paw + 0
            
            # State tracking
            if vals[2] == 4:
                self.PMax = 0
                self.VMax = 0
            if vals[2] == 1:
                if Paw > self.PMax:
                    self.PMax = Paw
                if Volume > self.VMax:
                    self.VMax = Volume
            if vals[2] == 2:
                if self.PMax != -10000:
                    print("PMax on last cycle:", self.PMax)
                    print("VMax on last cycle:", self.VMax)
                    
                    if self.running:
                        if self.PMax < 0.75 * self.params['PS'].value:
                            self.setAlert("Low Pressure")
                        if self.VMax < 0.5 * self.params['Vt'].value:
                            self.setAlert("Low Tidal Volume")
                    
                    self.PMax = -10000
                    self.VMax = -10000
                    
            VtData.append(Volume)
            PawData.append(Paw)
        
        if self.running:
            self.VtGraph.addPoints(VtData)
            self.PawGraph.addPoints(PawData)
        
    def startCallback(self, event):
        if not self.running:
            self.running = True
            self.modeButton.text = "Running"
            self.modeButton.disabled = True
            self.modeButton.color = [0, 1, 0, 1]
            self.startButton.text = "Stop"
            self.startButton.background_color = [1, 0, 0, 1]
            self.VtGraph.reset()
            self.PawGraph.reset()
            self.serial.write(b"R001")
        else:
            self.running = False
            self.modeButton.text = "Modes"
            self.modeButton.disabled = False
            self.modeButton.color = [1, 1, 1, 1]
            self.startButton.text = "Start"
            self.startButton.background_color = [0, 1, 0, 1]
            self.serial.write(b"R000")
            
    def paramUpdateCallback(self, event, value):
        IER = self.params['IER'].value
        RR = self.params['RR'].value
        PS = self.params['PS'].value
        
        breathTime = 60.0 / RR
        expTime = (IER/(IER + 1.0)) * breathTime * 100
        inhTime = (1.0/(IER + 1.0)) * breathTime * 100
        presRaw = PS * (1023.0/5.0) * (3.0 / 30.6) + 216
        
        self.serial.write(b"E%03u" % expTime)
        self.serial.write(b"I%03u" % inhTime)
        self.serial.write(b"P%03u" % presRaw)
    
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        titleLayout = BoxLayout(orientation='horizontal', height=50, size_hint_y=None)

        self.modeLabel = Label(text="PCV", markup=True, font_size=20)

        self.modeDropdown = DropDown()
        btn = Button(text='CMV', size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.modeDropdown.select(btn.text))
        self.modeDropdown.add_widget(btn)
        btn = Button(text='PCV', size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.modeDropdown.select(btn.text))
        self.modeDropdown.add_widget(btn)
        btn = Button(text='SIMV', size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.modeDropdown.select(btn.text))
        self.modeDropdown.add_widget(btn)
        
        self.modeButton = Button(text='Modes', font_size=20, size_hint_x = 0.25)
        self.modeButton.bind(on_release=self.modeDropdown.open)
        self.modeButton.disabled_color = [1, 1, 0, 1]
        # self.modeButton.background_disabled_normal = ''
        self.modeDropdown.bind(on_select=lambda instance, x: setattr(self.modeLabel, 'text', x))
        
        self.startButton = Button(text="Start", font_size=20, background_color=[0,1,0,1], size_hint_x = 0.25)
        self.startButton.bind(on_press=self.startCallback)

        titleLayout.add_widget(self.modeButton)
        titleLayout.add_widget(self.modeLabel)
        titleLayout.add_widget(self.startButton)

        layout.add_widget(titleLayout)
        
        self.VtGraph = GraphWidget(xlabel='', ylabel='Tidal Volume [ml]', x_ticks_minor=5,
        x_ticks_major=1, y_ticks_major=200, plotColor=[0, 1, 0, 1],
        y_grid_label=True, x_grid_label=True, padding=5,
        x_grid=False, y_grid=False, xmin=-0, xmax=10, ymin=0, ymax=1000)

        self.PawGraph = GraphWidget(xlabel='Time [s]', ylabel='Airway Pressure [cm H2O]', x_ticks_minor=5,
        x_ticks_major=1, y_ticks_major=10, plotColor=[0, 0, 1, 1],
        y_grid_label=True, x_grid_label=True, padding=5,
        x_grid=False, y_grid=False, xmin=-0, xmax=10, ymin=0, ymax=50)
        
        layout.add_widget(self.VtGraph)
        layout.add_widget(self.PawGraph)
        
        settingsLayout = ScrollView(width=Window.width, height=150, size_hint_y=None)
        settings = BoxLayout(orientation="horizontal", size_hint=(None, 1))
        settings.bind(minimum_width=settings.setter('width'))

        self.params = {}
        self.params['RR'] = SettingView(parameter="Respiratory Rate", 
                                        value=15, unit="bpm",
                                        minVal=4, maxVal=20, delta=1,
                                        width=250, size_hint_x=None, group='X')
        self.params['Vt'] = SettingView(parameter="Tidal Volume", 
                                        value=350, unit="ml",
                                        minVal=75, maxVal=1500, delta=10,
                                        width=250, size_hint_x=None, group='X')
        self.params['IER'] = SettingView(parameter="I:E Ratio", formatStr="1:%.1f",
                                        value=1.5, unit="",
                                        minVal=1.0, maxVal=2.5, delta=0.1,
                                        width=250, size_hint_x=None, group='X')
        self.params['PS'] = SettingView(parameter="Pressure Support", 
                                        value=25, unit="cm H2O",
                                        minVal=10, maxVal=40, delta=2,
                                        width=250, size_hint_x=None, group='X')
        
        for p in self.params:
            self.params[p].bind(on_change=self.paramUpdateCallback)
            settings.add_widget(self.params[p])
        
        settingsLayout.add_widget(settings)
        layout.add_widget(settingsLayout)

        # Open the serial port
        self.serial = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.01)

        #Clock.schedule_interval(lambda dt: self.plotCallback(dt), 0.1)
        Clock.schedule_interval(self.serialCallback, 0.1)
        
        return layout
    
if __name__ == "__main__":
    Window.fullscreen = 'auto'
    VentilatorApp().run()
