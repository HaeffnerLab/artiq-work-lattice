import time
import numpy as np
from artiq.experiment import *
from artiq.protocols.pc_rpc import Client


class FloppingF(EnvExperiment):

    def run(self):
        self.c = Client("::1", 3286, "rcg")
        i = 0
        self.set_dataset("x", [])
        self.set_dataset("y", [])
        while True:
            self.append_to_dataset("x", i)
            self.append_to_dataset("y", i)#np.sin(2*np.pi/10 * i))
            x = self.get_dataset("x")
            y = self.get_dataset("y")
            self.send_to_rcg(x, y)
            time.sleep(.5)
            i+=1

    @rpc(flags={"async"})
    def send_to_rcg(self, x, y):
        self.c.plot(x, y)
