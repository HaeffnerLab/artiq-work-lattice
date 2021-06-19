from artiq.experiment import *
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS


class phase_slip_test2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.blue = self.get_device("SP_729L2_bichro")
        self.SP_729G = self.get_device("SP_729G")
        self.SP_729L1 = self.get_device("SP_729L1")
        self.SP_729L2 = self.get_device("SP_729L2")
        self.trigger = self.get_device("SP_729G_bichro")

    def run(self):
        #-----------------------------------------------------------
        #    TEST OPTIONS

        # phase mode
        pmodes = [
                PHASE_MODE_CONTINUOUS, # 0
                PHASE_MODE_ABSOLUTE,   # 1
                PHASE_MODE_TRACKING    # 2
            ]
        pmode = pmodes[2]

        base_freq = 11.343*MHz
        freq1 = 1.323*MHz
        freq2 = 8.276*MHz
        delay_time = 403.13*us
        trigger_before=True
        phase1 = 0.08
        phase2 = 0.15

        #-----------------------------------------------------------
        self.loop(
                pmode, base_freq, freq1, freq2, delay_time,
                trigger_before, phase1, phase2
            )

    @kernel
    def loop(
                self, pmode, base_freq, freq1, freq2, delay_time,
                trigger_before, phase1, phase2
            ):
        self.core.reset()
        self.core.break_realtime()

        self.blue.cpld.init()
        self.SP_729G.cpld.init()
        self.SP_729L1.cpld.init()
        self.SP_729L2.cpld.init()
        self.trigger.cpld.init()

        self.SP_729G.sw.off()
        self.SP_729L1.sw.off()
        self.SP_729L2.sw.off()
        self.trigger.sw.off()

        self.SP_729G.set_phase_mode(pmode)
        self.SP_729L1.set_phase_mode(pmode)
        self.SP_729L2.set_phase_mode(pmode)
        self.trigger.set_phase_mode(PHASE_MODE_CONTINUOUS)

        # self.SP_729G.set_phase_mode(PHASE_MODE_TRACKING)
        # self.SP_729L1.set_phase_mode(PHASE_MODE_TRACKING)
        # self.SP_729L2.set_phase_mode(PHASE_MODE_ABSOLUTE)
        # self.trigger.set_phase_mode(PHASE_MODE_CONTINUOUS)

        ref_time = now_mu()

        self.SP_729G.set(base_freq, ref_time_mu=ref_time)
        self.SP_729L1.set(base_freq, ref_time_mu=ref_time, phase=phase1)
        self.SP_729L2.set(base_freq, ref_time_mu=ref_time, phase=phase2)
        self.trigger.set(base_freq)

        self.SP_729G.set_att(5*dB)
        self.SP_729L1.set_att(5*dB)
        self.SP_729L2.set_att(5*dB)
        self.trigger.set_att(5*dB)

        while True:
            with parallel:
                self.SP_729G.sw.on()
                self.SP_729L1.sw.on()
                self.SP_729L2.sw.on()
                if trigger_before:
                    self.trigger.sw.on()

            delay(10*us)

            # with parallel:
            self.SP_729L1.set(freq1, ref_time_mu=ref_time, amplitude=0.05)
            self.SP_729L2.set(freq2, amplitude=0.05)

            delay(delay_time)

            # with parallel:
            if not trigger_before:
                self.trigger.sw.on()
            self.SP_729L1.set(base_freq, ref_time_mu=ref_time, amplitude=1.0, phase=phase1)
            self.SP_729L2.set(base_freq, amplitude=1.0, phase=phase2)

            delay(delay_time)

            with parallel:
                self.SP_729G.sw.off()
                self.SP_729L1.sw.off()
                self.SP_729L2.sw.off()
                self.trigger.sw.off()

            delay(1*ms)
