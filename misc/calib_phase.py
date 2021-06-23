from artiq.experiment import *

from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS
import numpy as np

class phase_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")

        self.urukul0 = [self.get_device("urukul0_ch{}".format(i)) for i in range(4)]
        self.urukul1 = [self.get_device("urukul1_ch{}".format(i)) for i in range(4)]
        self.urukul2 = [self.get_device("urukul2_ch{}".format(i)) for i in range(4)]
        self.urukul3 = [self.get_device("urukul3_ch{}".format(i)) for i in range(4)]

    @kernel
    def run(self):
        self.core.reset()

        self.urukul0[0].cpld.init()
        self.urukul1[0].cpld.init()
        self.urukul2[0].cpld.init()
        self.urukul3[0].cpld.init()

        self.core.break_realtime()
        
        for urukul in self.urukul0:
            urukul.init()
        for urukul in self.urukul1:
            urukul.init()
        for urukul in self.urukul2:
            urukul.init()
        for urukul in self.urukul3:
            urukul.init()

        delay(1*ms)

        # This calibration needs to be done only once to find good values.
        # The rest is happening at each future init() of the DDS.
        d00, w00 = self.urukul0[0].tune_sync_delay()
        t00 =      self.urukul0[0].tune_io_update_delay()
        d01, w01 = self.urukul0[1].tune_sync_delay()
        t01 =      self.urukul0[1].tune_io_update_delay()
        d02, w02 = self.urukul0[2].tune_sync_delay()
        t02 =      self.urukul0[2].tune_io_update_delay()
        d03, w03 = self.urukul0[3].tune_sync_delay()
        t03 =      self.urukul0[3].tune_io_update_delay()

        d10, w10 = self.urukul1[0].tune_sync_delay()
        t10 =      self.urukul1[0].tune_io_update_delay()
        d11, w11 = self.urukul1[1].tune_sync_delay()
        t11 =      self.urukul1[1].tune_io_update_delay()
        d12, w12 = self.urukul1[2].tune_sync_delay()
        t12 =      self.urukul1[2].tune_io_update_delay()
        d13, w13 = self.urukul1[3].tune_sync_delay()
        t13 =      self.urukul1[3].tune_io_update_delay()

        d20, w20 = self.urukul2[0].tune_sync_delay()
        t20 =      self.urukul2[0].tune_io_update_delay()
        d21, w21 = self.urukul2[1].tune_sync_delay()
        t21 =      self.urukul2[1].tune_io_update_delay()
        d22, w22 = self.urukul2[2].tune_sync_delay()
        t22 =      self.urukul2[2].tune_io_update_delay()
        d23, w23 = self.urukul2[3].tune_sync_delay()
        t23 =      self.urukul2[3].tune_io_update_delay()

        d30, w30 = self.urukul3[0].tune_sync_delay()
        t30 =      self.urukul3[0].tune_io_update_delay()
        d31, w31 = self.urukul3[1].tune_sync_delay()
        t31 =      self.urukul3[1].tune_io_update_delay()
        d32, w32 = self.urukul3[2].tune_sync_delay()
        t32 =      self.urukul3[2].tune_io_update_delay()
        d33, w33 = self.urukul3[3].tune_sync_delay()
        t33 =      self.urukul3[3].tune_io_update_delay()

        # Add the values found to each of the four channels in your
        # device_db.py so that e.g. for urukul0_ch0 it looks like:
        #    "urukul0_ch0": {
        #       ...
        #        "class": "AD9910",
        #        "arguments": {
        #            "pll_n": 32,
        #            "chip_select": 4,
        #           "sync_delay_seed": D,
        #           "io_update_delay": T,
        #           "cpld_device": "urukul0_cpld",
        #           ...
        #       }
        # where T is the io_update_delay of the channel and
        # D is the sync_delay_seed of the channel below:
        print("sync_delay_seeds = [", [d00, d01, d02, d03], ",")
        print("                    ",     [d10, d11, d12, d13], ",")
        print("                    ",     [d20, d21, d22, d23], ",")
        print("                    ",     [d30, d31, d32, d33], "]")
        print("io_update_delays = [", [t00, t01, t02, t03], ",")
        print("                   ",    [t10, t11, t12, t13], ",")
        print("                   ",    [t20, t21, t22, t23], ",")
        print("                   ",    [t30, t31, t32, t33], "]")
        # As long as the values don't differ too much between the channels,
        # using the mean for them is also fine.
        # This one is for information purposes only:
        print("validation delays") 
        print([w00, w01, w02, w03])
        print([w10, w11, w12, w13])
        print([w20, w21, w22, w23])
        print([w30, w31, w32, w33])

        
       
