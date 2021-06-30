from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP, RAM_DEST_FTW,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, RAM_MODE_CONT_BIDIR_RAMP
    )
import numpy as np

class RamModeNoiseExample(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul1_ch2")
        # self.u = self.get_device("urukul2_ch0")
        self.ttl = self.get_device("blue_PIs")

    def run(self):
        # noise: [0, 1, 2] = [white amplitude, white frequency, Lorentzian amplitude]
        noise = 1

        rng = np.random.default_rng()
        n = 1024
        if noise in [0, 1]:
            if noise == 0:
                std = 0.25
                mean = 0.5
                min_ = 0.
                max_ = 1.
            else:
                std = 5 * MHz
                mean = 10 * MHz
                min_ = 0 * MHz
                max_ = 100 * MHz
            self.dataf = std * rng.standard_normal(n) + mean
        else:
            std = 0.25
            mean = 0.5
            min_ = 0.
            max_ = 1.
            self.dataf = std * rng.standard_cauchy(n) + mean

        for i, val in enumerate(self.dataf):
            if val > max_:
                self.dataf[i] = max_
            elif val < min_:
                self.dataf[i] = min_

        self.noise = noise
        self.krun()

    @kernel
    def krun(self):
        dataf = self.dataf
        data = [0] * len(dataf)
        if self.noise in [0, 2]:
            self.u.amplitude_to_ram(dataf, data)
        else:
            self.u.frequency_to_ram(dataf, data)

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
                                mode=RAM_MODE_CONT_RAMPUP,
                                # nodwell_high=1
                            )

        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)
        self.u.write_ram(data)
        delay(1*ms)
        if self.noise in [0, 2]:
            dest = RAM_DEST_ASF
        else:
            dest = RAM_DEST_FTW
        self.u.set_cfr1(
                    ram_enable=1,
                    ram_destination=dest,
                    phase_autoclear=1,
                    internal_profile=0,
                    # the following parameters are a hack as described in
                    # https://github.com/m-labs/artiq/issues/1554
                    manual_osk_external=0,
                    osk_enable=1 if self.noise == 1 else 0,
                    select_auto_osk=0
                )
        self.u.cpld.io_update.pulse_mu(8)
        if self.noise in [0, 2]:
            self.u.set_frequency(125*MHz)
        else:
            self.u.set_amplitude(1.)
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

