from artiq import *
from artiq.experiment import *

class testterm(EnvExperiment):
    
    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")

    #@kernel
    #def test(self):
    #    print("we here")
    #    delay(.5*s)
    
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        while True:
            if not self.scheduler.check_pause():
                print("we here")
                delay(.5*s)
            else:
                print("we gone")
                break
