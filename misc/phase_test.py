from artiq.experiment import *

from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE
import numpy as np

class phase_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        #self.dds1 = self.get_device("729G")
        self.dds1 = self.get_device("SP_729G")
        self.dds2 = self.get_device("SP_729G_bichro")
        self.dds_sum = self.get_device("729L1")

        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")

    @kernel
    def run(self):
        self.core.reset()

        self.dds1.sw.off()
        self.dds2.sw.off()
        self.dds_sum.sw.off()

        self.dds1.set_phase_mode(PHASE_MODE_TRACKING)
        self.dds2.set_phase_mode(PHASE_MODE_TRACKING)
        self.dds_sum.set_phase_mode(PHASE_MODE_TRACKING)

        #ref_time = np.int64(-1)
        ref_time = now_mu()
        print(ref_time)
        self.core.break_realtime()

        delay(100*us)

        sp_freq = 80.3*MHz
        trap_freq = 830*kHz
        detuning = 5*kHz
        bichro_blue_freq = sp_freq + trap_freq + detuning
        bichro_red_freq = sp_freq - trap_freq - detuning

        print("sp_freq =", sp_freq)
        print("bichro_blue_freq =", bichro_blue_freq)
        print("bichro_red_freq =", bichro_red_freq)
        self.core.break_realtime()

        # turn on the two bichro frequencies
        self.dds1.set(bichro_blue_freq, ref_time_mu=ref_time)
        self.dds1.set_att(5*dB)

        self.core.break_realtime()

        self.dds2.set(bichro_red_freq, ref_time_mu=ref_time)
        self.dds2.set_att(5*dB)

        self.dds1.sw.on()
        self.dds2.sw.on()

        delay(10*us)

        # on the third channel, first set to the bichro, then change to the default
        self.dds_sum.set(bichro_blue_freq, ref_time_mu=ref_time)
        self.dds_sum.set_att(5*dB)

        self.core.break_realtime()
        delay(10*us)

        phase_degrees = 0.
        self.dds_sum.set(sp_freq, ref_time_mu=ref_time, phase=phase_degrees/360.)
        self.dds_sum.set_att(5*dB)

        self.core.break_realtime()

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
