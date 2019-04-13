import labrad
import numpy as np
import time
from artiq.experiment import *


class MgmtTutorial(EnvExperiment):
    """Management tutorial"""
    def build(self):
        cxn = labrad.connect()
        p = cxn.parametervault
        val = int(p.get_parameter(["SidebandCooling",
            "sideband_cooling_cycles"]).real)
        self.setattr_argument("count", NumberValue(val, ndecimals=0, step=1))

    def run(self):
        self.set_dataset("parabola", np.full(self.count, np.nan),
                broadcast=True)
        for i in range(self.count):
            self.mutate_dataset("parabola", i, i*i)
            time.sleep(0.5)
