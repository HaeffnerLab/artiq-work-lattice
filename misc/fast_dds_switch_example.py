from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING
    )
import numpy as np

class FastDDSSwitchExample(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul1_ch2")
        self.ttl = self.get_device("blue_PIs")

    @kernel
    def run(self):
        self.core.reset()
        self.u.cpld.init()
        self.u.init()
        self.u.sw.off()
        self.core.break_realtime()

        self.u.set(20*MHz, amplitude=1., profile=0)
        self.u.set(10*MHz, amplitude=1., profile=1)
        self.u.set_att(10*dB)
        self.u.cpld.set_profile(0)

        while True:
            self.u.cpld.set_profile(1)
            with parallel:
                self.u.sw.on()
                self.ttl.on()
            delay(1*us)
            with parallel:
                self.ttl.off()
                self.u.cpld.set_profile(0)
            delay(3*us)
            with parallel:
                self.u.sw.off()
            delay(1*ms)
