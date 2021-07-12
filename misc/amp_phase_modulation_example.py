from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP, RAM_DEST_FTW, RAM_DEST_POWASF,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, RAM_MODE_CONT_BIDIR_RAMP
    )
import numpy as np

class RAMAmpPhaseExample(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul3_ch1")
        # self.u = self.get_device("urukul2_ch0")
        self.ttl = self.get_device("blue_PIs")

    def run(self):
        n = 1024
        max_ = 1.
        min_ = 0.

        rng = np.random.default_rng()
        self.data_amp = 0.1 * rng.standard_normal(n) + 0.5
        self.data_amp = [i%2 * 0.5 + 0.5 for i in range(n)]
        self.data_phase = [0.5 * i%2 for i in range(n)]

        for i, val in enumerate(self.data_amp):
            if val > max_:
                self.data_amp[i] = max_
            elif val < min_:
                self.data_amp[i] = min_

        self.data = [0] * len(self.data_amp)
        self.u.turns_amplitude_to_ram(self.data_phase, self.data_amp, self.data)
        self.data = np.int32(self.data)

        self.krun()

    @kernel
    def krun(self):
        data = self.data

        self.core.reset()
        self.u.cpld.init()
        self.u.init()
        self.u.set_cfr1(ram_enable=0)
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)

        self.u.set_profile_ram(
                                start=0,
                                end=len(data) - 1,
                                step=100,
                                profile=0,
                                mode=RAM_MODE_CONT_RAMPUP,
                                # nodwell_high=1
                            )

        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)
        self.u.write_ram(data)
        delay(1*ms)
        self.u.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_POWASF,
                    phase_autoclear=1,
                    internal_profile=0,
                )
        self.u.cpld.io_update.pulse_mu(8)
        self.u.set_frequency(30*MHz)
        self.u.set_att(10*dB)
        self.u.sw.on()

        self.core.break_realtime()
        while True:
            delay(1*ms)
            with parallel:
                self.u.sw.on()
                self.ttl.on()
                self.u.cpld.io_update.pulse_mu(8)
            delay(4*us)
            self.ttl.off()
            self.u.sw.off()
