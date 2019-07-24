from artiq.experiment import *

from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE

class rf_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("729G")
        self.dds2 = self.get_device("729L1")

    @kernel
    def run(self):
        self.core.reset()

        self.dds.set_phase_mode(PHASE_MODE_TRACKING)
        self.dds2.set_phase_mode(PHASE_MODE_TRACKING)

        ref_time = 0 #now_mu()

        delay(100*us)

        self.dds.set(0.5*MHz, amplitude=1., ref_time_mu=ref_time)
        self.dds.set_att(5*dB)

        self.core.break_realtime()

        self.dds2.set(0.5*MHz, amplitude=1., ref_time_mu=ref_time)
        self.dds2.set_att(5*dB)

        self.core.break_realtime()

        #with parallel:
        self.dds.sw.on()
        self.dds2.sw.on()

        delay(10*us)
        self.dds.sw.off()

        #self.dds.set_phase_mode(PHASE_MODE_TRACKING)

        self.dds.set(1.0*MHz, amplitude=1., ref_time_mu=ref_time)
        self.dds.sw.on()
        delay(5*us)
        self.dds.sw.off()

        self.dds.set(0.5*MHz, amplitude=1., ref_time_mu=ref_time)
        self.dds.sw.on()
        delay(10*us)

        #with parallel:
        self.dds.sw.off()
        self.dds2.sw.off()
