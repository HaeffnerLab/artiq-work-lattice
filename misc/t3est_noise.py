from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING
    )
import numpy as np

class AD9910RAM(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul3_ch2")
        self.u1 = self.get_device("urukul3_ch0")
        self.ttl = self.get_device("blue_PIs")

    @kernel
    def run(self):
        dataf = [i%2 *1. for i in range(1,7)]
        # print(dataf)
        data = [0] * len(dataf)
        self.u.amplitude_to_ram(dataf, data)
        # print(data)

        self.core.reset()

        self.u.cpld.init()
        self.u1.cpld.init()
        self.u.init()
        self.u1.init()
        delay(1*ms)

        self.u.set_profile_ram(
            start=0, end=len(data) - 1, step=500,
            profile=0, mode=RAM_MODE_RAMPUP,
            nodwell_high=1
            )
        self.u1.set_profile_ram(
            start=0, end=len(data) - 1, step=1,
            profile=0, mode=RAM_MODE_RAMPUP,
            nodwell_high=1
            )
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)
        self.u1.cpld.set_profile(0)
        self.u1.cpld.io_update.pulse_mu(8)
        delay(1*ms)
        self.u.write_ram(data)
        self.u1.write_ram(data)
        delay(1*ms)
        self.u.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_ASF,
                    phase_autoclear=1,
                    #internal_profile=0,
                )
        self.u1.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_ASF,
                    phase_autoclear=1,
                    #internal_profile=0,
                )
        self.u.set_frequency(125*MHz)
        self.u.cpld.io_update.pulse_mu(8)
        self.u.set_att(10*dB)
        self.u.sw.on()
        self.u1.set_frequency(125*MHz)
        self.u1.cpld.io_update.pulse_mu(8)
        self.u1.set_att(10*dB)
        self.u1.sw.on()

        r = [0]*len(data)
        self.u.read_ram(r)
        for i in range(len(data)):
            assert r[i] == data[i]
        # print(r)

        self.core.break_realtime()
        while True:
            delay(1*ms)
            with parallel:
                self.u.sw.on()
                self.u1.sw.off()
            self.ttl.on()
            with parallel:
                self.u.cpld.io_update.pulse_mu(8)
            delay(10*us)
            self.ttl.off()
            with parallel:
                self.u.sw.off()
                self.u1.sw.on()
            self.u1.cpld.io_update.pulse_mu(8)




















