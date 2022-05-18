"""Real time plotting of Microphone level using kivy
    Notes: 
        the MeshLinePlot plots at the scale of the graph, in pixels
        With the current settings, the max height (y axis max) is 500
        So the mic level (to set at the OS / system level, not in the present code) has to be adapted
        Also scale the rms can be done here.
        When computing the signal level power with audioop.rms, the arguments are (fragment, width) width being the sample width in bytes, either 1, 2, 3 or 4
        audioop.rms Return the root-mean-square of the fragment, i.e. sqrt(sum(S_i^2)/n). This is a measure of the power in an audio signal.
        https://docs.python.org/3/library/audioop.html
"""

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph,MeshLinePlot
#from kivy.garden.graph import MeshLinePlot
from kivy.clock import Clock
from threading import Thread
import audioop
import pyaudio

def get_microphone_level():
    """
    source: http://stackoverflow.com/questions/26478315/getting-volume-levels-from-pyaudio-for-use-in-arduino
    audioop.max alternative to audioop.rms
    """
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()

    s = p.open(format=FORMAT,
               channels=CHANNELS,
               rate=RATE,
               input=True,
               frames_per_buffer=chunk)
    global levels
    while True:
        data = s.read(chunk) # len(data): 2048
        mx = audioop.rms(data, 2) #- 300
        #mx = 500 # plots a constant level line
        if len(levels) >= 100:
            levels = []
        levels.append(mx)


class Logic(BoxLayout):
    def __init__(self, **kwargs): 
        super(Logic, self).__init__(**kwargs)
    #def __init__(self,):
    #    super(Logic, self).__init__()
    #    graph = Graph(xlabel='X', ylabel='Y', x_ticks_minor=5,
    #        x_ticks_major=25, y_ticks_major=1,
    #        y_grid_label=True, x_grid_label=True, padding=5,
    #        x_grid=True, y_grid=True, xmin=-0, xmax=400, 
    #        ymin=-1, ymax=1000)

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        #graph.add_plot(plot)
        #self.add_widget(self.graph)


    def start(self):
        self.ids.graph.add_plot(self.plot)
        Clock.schedule_interval(self.get_value, 0.001)

    def stop(self):
        Clock.unschedule(self.get_value)

    def get_value(self, dt):
        #print([(i, j/9) for i, j in enumerate(levels)])
        # scale the level below, original was j/5 but out of scale
        self.plot.points = [(i, j/100) for i, j in enumerate(levels)]


class RealTimeMicrophone(App):
    def build(self):
        return Builder.load_file("look.kv")

if __name__ == "__main__":
    levels = []  # store levels of microphone
    get_level_thread = Thread(target = get_microphone_level)
    get_level_thread.daemon = True
    get_level_thread.start()
    RealTimeMicrophone().run()
    
