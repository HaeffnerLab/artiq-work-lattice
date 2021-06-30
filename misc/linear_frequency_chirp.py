from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_DEST_FTW, RAM_MODE_BIDIR_RAMP,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, RAM_MODE_CONT_BIDIR_RAMP
    )
import numpy as np

class LinearFrequencyChirp(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.u = self.get_device("urukul1_ch2")
        #self.u = self.get_device("urukul2_ch0")
        self.ttl = self.get_device("blue_PIs")

    def run(self):
        n = 1024
        datar = [5*MHz + 15*MHz * i/(n-1) for i in range(n)]
        self.dataf = np.flip(datar)
        self.krun()

    @kernel
    def krun(self):
        dataf = self.dataf
        data = [0] * len(dataf)
        self.u.frequency_to_ram(dataf, data)

        self.core.reset()
        self.u.cpld.init()
        self.u.init()
        self.u.set_cfr1(ram_enable=0)
        self.u.cpld.set_profile(0)
        self.u.cpld.io_update.pulse_mu(8)
        delay(1*ms)

        self.u.set_profile_ram(
                                start=0,
                                end=len(data) - 1,
                                step=1,
                                profile=0,
                                mode=RAM_MODE_CONT_RAMPUP,
                                # nodwell_high=1
                            )
        self.u.write_ram(data)
        delay(10*ms)
        self.u.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_FTW,
                    phase_autoclear=1,
                    internal_profile=0,
                    # the following parameters are a hack as described in
                    # https://github.com/m-labs/artiq/issues/1554
                    manual_osk_external=0, 
                    osk_enable=1, 
                    select_auto_osk=0
                )
        self.u.set_amplitude(1.)
        self.u.cpld.io_update.pulse_mu(8)
        self.u.set_att(10*dB)
        self.u.sw.on()

        self.core.break_realtime()
        while True:
            delay(1*ms)
            with parallel:
                self.u.sw.on()
                self.ttl.on()
                self.u.cpld.io_update.pulse_mu(8)
            delay(5*us)
            self.ttl.off()
            self.u.sw.off()


