from artiq.experiment import *

from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE

class phase_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.dds1 = self.get_device("729G")
        self.dds2 = self.get_device("729L1")
        self.dds_sum = self.get_device("SP_729G")

    @kernel
    def run(self):
        self.core.reset()

        self.dds1.sw.off()
        self.dds2.sw.off()
        self.dds_sum.sw.off()

        self.dds1.set_phase_mode(PHASE_MODE_TRACKING)
        self.dds2.set_phase_mode(PHASE_MODE_TRACKING)
        self.dds_sum.set_phase_mode(PHASE_MODE_TRACKING)

        ref_time = now_mu()
        print(ref_time)
        self.core.break_realtime()

        delay(100*us)

        self.dds1.set(25*MHz, ref_time_mu=ref_time)
        self.dds1.set_att(5*dB)

        self.core.break_realtime()

        self.dds2.set(25*MHz+76.9*Hz, ref_time_mu=ref_time)
        self.dds2.set_att(5*dB)

        # turn on the two frequencies
        self.dds1.sw.on()
        self.dds2.sw.on()

        # delay(10*us)

        # self.dds_sum.set(20*MHz, ref_time_mu=ref_time)
        # self.dds_sum.set_att(5*dB)

        # self.core.break_realtime()

        # delay(10*us)

        # self.dds_sum.set(40*MHz, ref_time_mu=ref_time)
        # self.dds_sum.set_att(5*dB)

        # self.core.break_realtime()

        # self.dds_sum.sw.on()

        # leave each DDS on so that we can measure
