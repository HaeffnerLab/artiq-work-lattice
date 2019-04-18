from artiq import *
from artiq.experiment import *

class testpause(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.setattr_device("led0")

    def run(self):
        self.core.reset()
        self.core.break_realtime()
        print("got here")
        self.do_something()
        print("and here")

    @kernel
    def do_something(self):
        self.core.reset()
        self.core.break_realtime()
        self.led0.on()
        delay(1*s)
        self.led0.off()
