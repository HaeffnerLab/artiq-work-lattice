from artiq.experiment import *

from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS
import numpy as np

class phase_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")

        # Get all 4 DDS channels on Urukul1
        self.dds1 = self.get_device("SP_729G")
        self.dds2 = self.get_device("SP_729G_bichro")
        self.dds_sum = self.get_device("729L1")
        self.dds4 = self.get_device("729L2")

        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")

    @kernel
    def run(self):
        self.core.reset()

        self.dds1.sw.off()
        self.dds2.sw.off()
        self.dds_sum.sw.off()

        # This calibration needs to be done only once to find good values.
        # The rest is happening at each future init() of the DDS.
        if True: # self.dds1.sync_delay_seed == -1:
            delay(100*us)
            d0, w0 = self.dds1.tune_sync_delay()
            t0 = self.dds1.tune_io_update_delay()
            d1, w1 = self.dds2.tune_sync_delay()
            t1 = self.dds2.tune_io_update_delay()
            d2, w2 = self.dds_sum.tune_sync_delay()
            t2 = self.dds_sum.tune_io_update_delay()
            d3, w3 = self.dds4.tune_sync_delay()
            t3 = self.dds4.tune_io_update_delay()
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
            print("sync_delay_seed", [d0, d1, d2, d3])
            print("io_update_delay", [t0, t1, t2, t3])
            # As long as the values don't differ too much between the channels,
            # using the mean for them is also fine.
            # This one is for information purposes only:
            print("validation delays", [w0, w1, w2, w3])
            #
            # then run this script again
            return

        self.dds1.set_phase_mode(PHASE_MODE_ABSOLUTE)
        self.dds2.set_phase_mode(PHASE_MODE_ABSOLUTE)
        self.dds_sum.set_phase_mode(PHASE_MODE_TRACKING)

        ref_time = np.int64(-1)
        # print(ref_time)
        # self.core.break_realtime()

        delay(100*us)

        sp_freq = 80.3*MHz
        trap_freq = 830*kHz * 4
        detuning = 5*kHz
        bichro_blue_freq = sp_freq + trap_freq + detuning
        bichro_red_freq = sp_freq - trap_freq - detuning

        # print("sp_freq =", sp_freq)
        # print("bichro_blue_freq =", bichro_blue_freq)
        # print("bichro_red_freq =", bichro_red_freq)
        # self.core.break_realtime()

        delay(100*us)

        # turn on the two bichro frequencies
        self.dds1.set(bichro_blue_freq) #, ref_time_mu=ref_time)
        self.dds1.set_att(5*dB)

        # self.core.break_realtime()

        self.dds2.set(bichro_red_freq) #, ref_time_mu=ref_time)
        self.dds2.set_att(5*dB)

        with parallel:
            self.dds1.sw.on()
            self.dds2.sw.on()
            ref_time = now_mu()

        # on the third channel, first set to the bichro, then change to the default
        self.dds_sum.set(bichro_blue_freq*2., ref_time_mu=ref_time)
        self.dds_sum.set_att(5*dB)

        self.dds_sum.sw.on()
        delay(10*us)
        self.dds_sum.sw.off()

        delay(120*us)
        phase_degrees = 0.
        self.dds_sum.set_att(5*dB)
        pow = self.dds_sum.set(sp_freq*2., ref_time_mu=ref_time) #, phase=phase_degrees/360.)
        # print("phase offset:", pow)
        # self.core.break_realtime()
        #delay(100*us)

        self.dds_sum.sw.on()

        # leave each DDS on so that we can measure

        # turn on the 397 and 866 so we don't lose our ions
        self.dds_397.set(78*MHz)
        self.dds_397.set_att(5*dB)
        self.core.break_realtime()
        self.dds_866.set(80*MHz)
        self.dds_866.set_att(5*dB)
        self.core.break_realtime()
        self.dds_397.sw.on()
        self.dds_866.sw.on()
