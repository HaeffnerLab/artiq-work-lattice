from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, RAM_MODE_CONT_BIDIR_RAMP
    )
import numpy as np

class SineRamp(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul1_ch2")
        #self.u = self.get_device("urukul2_ch0")
        self.ttl = self.get_device("blue_PIs")

    def run(self):
        n = 1024
        datar = np.sin([(np.pi / 2)* (i / (n-1)) for i in range(n)])**2
        self.dataf = np.flip(datar)
        self.krun()

    @kernel
    def krun(self):
        dataf = self.dataf
        data = [0] * len(dataf)
        self.u.amplitude_to_ram(dataf, data)

        self.core.reset()
        self.u.cpld.init()
        self.u.init()
        self.u.set_cfr1(ram_enable=0)
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)

        self.u.set_profile_ram(
                                start=0,
                                end=len(data) - 1,
                                step=1,
                                profile=0,
                                mode=RAM_MODE_CONT_BIDIR_RAMP,
                                # nodwell_high=1
                            )
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)
        self.u.write_ram(data)
        delay(1*ms)
        self.u.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_ASF,
                    phase_autoclear=1,
                    #internal_profile=0,
                )
        self.u.cpld.io_update.pulse_mu(8)
        self.u.set_frequency(125*MHz)
        self.u.set_att(10*dB)
        self.u.sw.on()

        self.core.break_realtime()
        while True:
            delay(1*ms)
            with parallel:
                self.u.sw.on()
                self.ttl.on()
                self.u.cpld.io_update.pulse_mu(8)
            delay(10*us)
            self.ttl.off()
            self.u.sw.off()

