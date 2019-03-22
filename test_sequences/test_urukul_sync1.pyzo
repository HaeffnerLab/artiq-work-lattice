from artiq.language import *

from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING


class UrukulSync(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.d0 = self.get_device("urukul2_ch0")
        self.d1 = self.get_device("urukul2_ch1")
        self.d2 = self.get_device("urukul2_ch2")
        self.d3 = self.get_device("urukul2_ch3")
        self.t = self.get_device("ttl4")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.d0.cpld.init()
        self.d0.init()
        self.d1.init()
        self.d2.init()
        self.d3.init()

        # This calibration needs to be done only once to find good values.
        # The rest is happening at each future init() of the DDS.
        if self.d0.sync_delay_seed == -1:
            delay(100*us)
            d0, w0 = self.d0.tune_sync_delay()
            t0 = self.d0.tune_io_update_delay()
            d1, w1 = self.d1.tune_sync_delay()
            t1 = self.d0.tune_io_update_delay()
            d2, w2 = self.d2.tune_sync_delay()
            t2 = self.d0.tune_io_update_delay()
            d3, w3 = self.d3.tune_sync_delay()
            t3 = self.d0.tune_io_update_delay()
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
            # print("validation delays", [w0, w1, w2, w3])
            #
            # then run this script again
            return

        self.d0.set_phase_mode(PHASE_MODE_TRACKING)
        self.d1.set_phase_mode(PHASE_MODE_TRACKING)
        self.d2.set_phase_mode(PHASE_MODE_TRACKING)
        self.d3.set_phase_mode(PHASE_MODE_TRACKING)

        self.d0.set_att(1*dB)
        self.d1.set_att(1*dB)
        self.d2.set_att(1*dB)
        self.d3.set_att(1*dB)

        t = now_mu()
        self.d0.set(80*MHz, phase=0., ref_time_mu=t)
        self.d1.set(80*MHz, phase=.5, ref_time_mu=t)
        self.d2.set(80*MHz, phase=.25, ref_time_mu=t)
        self.d3.set(80*MHz, phase=.75, ref_time_mu=t)

        self.t.on()
        self.d0.sw.on()
        self.d1.sw.on()
        self.d2.sw.on()
        self.d3.sw.on()

