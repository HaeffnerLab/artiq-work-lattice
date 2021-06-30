from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP, RAM_DEST_FTW,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, RAM_MODE_CONT_BIDIR_RAMP
    )
import numpy as np

class NoiseSwitch(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul1_ch2")
        self.u1 = self.get_device("urukul2_ch0")
        self.ttl = self.get_device("blue_PIs")

    def run(self):
        rng = np.random.default_rng()
        n = 1024

        std = 0.25
        mean = 0.5
        min_ = 0.
        max_ = 1.
        self.data = std * rng.standard_normal(n) + mean
        self.data1 = std * rng.standard_normal(n) + mean
        for i, val in enumerate(self.data):
            if val > max_:
                self.data[i] = max_
            elif val < min_:
                self.data[i] = min_
        for i, val in enumerate(self.data1):
            if val > max_:
                self.data1[i] = max_
            elif val < min_:
                self.data1[i] = min_

        self.krun()

    @kernel
    def krun(self):
        datar = [0] * len(self.data)
        datar1 = [0] * len(self.data1)
        self.u.amplitude_to_ram(self.data, datar)
        self.u1.amplitude_to_ram(self.data1, datar1)

        self.core.reset()

        self.u.cpld.init()
        self.u.init()
        self.u.set_cfr1(ram_enable=0)
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)

        self.u1.cpld.init()
        self.u1.init()
        self.u1.set_cfr1(ram_enable=0)
        self.u1.cpld.set_profile(0)
        self.u1.cpld.io_update.pulse_mu(8)
        
        self.u.set_profile_ram(
                                start=0,
                                end=len(datar) - 1,
                                step=1,
                                profile=0,
                                mode=RAM_MODE_CONT_RAMPUP,
                                # nodwell_high=1
                            )
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)
        self.u.write_ram(datar)
        delay(1*ms)
        self.u.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_ASF,
                    phase_autoclear=1,
                )
        self.u.cpld.io_update.pulse_mu(8)
        self.u.set_frequency(125*MHz)
        self.u.set_att(10*dB)

        self.u1.set_profile_ram(
                                start=0,
                                end=len(datar1) - 1,
                                step=1,
                                profile=0,
                                mode=RAM_MODE_CONT_RAMPUP,
                                # nodwell_high=1
                            )
        self.u1.cpld.set_profile(0)
        self.u1.cpld.io_update.pulse_mu(8)
        self.u1.write_ram(datar1)
        delay(1*ms)
        self.u1.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_ASF,
                    phase_autoclear=1,
                )
        self.u1.cpld.io_update.pulse_mu(8)
        self.u1.set_frequency(125*MHz)
        self.u1.set_att(10*dB)

        self.core.break_realtime()
        while True:
            delay(1*ms)
            with parallel:
                self.u1.sw.off()
                self.u.sw.on()
                self.ttl.on()
                self.u.cpld.io_update.pulse_mu(8)
            delay(4*us)
            self.u1.sw.on()
            delay(90*ns)
            with parallel:
                self.ttl.off()
                self.u.sw.off()
                self.u1.cpld.io_update.pulse_mu(8)
            delay(4*us)
            self.u1.sw.off()

