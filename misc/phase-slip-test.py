from artiq.experiment import *
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS


class phase_slip_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.SP_729G = self.get_device("SP_729G")
        self.SP_729L1 = self.get_device("SP_729L1")
        self.trigger = self.get_device("SP_729G_bichro")

    def run(self):
        #-----------------------------------------------------------
        #    TEST OPTIONS

        # number of phase steps
        pstep = 1. / 100

        # phase mode
        pmodes = [
                PHASE_MODE_CONTINUOUS, # 0
                PHASE_MODE_ABSOLUTE,   # 1
                PHASE_MODE_TRACKING    # 2
            ]
        pmode = pmodes[0]

        # toggle trigger to run every loop iteration or just once
        trigger_every_iteration = False

        #-----------------------------------------------------------

        self.loop(pstep, pmode, trigger_every_iteration)

    @kernel
    def loop(self, pstep, pmode, trigger_every_iteration):
        self.core.reset()
        self.core.break_realtime()

        self.SP_729G.cpld.init()
        self.SP_729L1.cpld.init()
        self.trigger.cpld.init()

        self.SP_729G.sw.off()
        self.SP_729L1.sw.off()
        self.trigger.sw.off()

        self.SP_729G.set_phase_mode(pmode)
        self.SP_729L1.set_phase_mode(pmode)
        self.trigger.set_phase_mode(PHASE_MODE_CONTINUOUS)

        ref_time = now_mu()
        set_freq = 10*MHz

        self.SP_729G.set(set_freq, ref_time_mu=ref_time)
        self.SP_729L1.set(set_freq, ref_time_mu=ref_time)
        self.trigger.set(set_freq)

        self.SP_729G.set_att(5*dB)
        self.SP_729L1.set_att(5*dB)
        self.trigger.set_att(5*dB)

        delay(10*us)

        self.trigger.sw.on()
        rel_phase = 0.
        while True:
            rel_phase = rel_phase + pstep
            if rel_phase > 1: rel_phase -= 1
            self.SP_729L1.set(set_freq, phase=rel_phase)
            delay(10*us)

            if trigger_every_iteration:
                self.trigger.sw.on()
            
            with parallel:
                self.SP_729G.sw.on()
                self.SP_729L1.sw.on()
            
            
            delay(100*us)
            
            with parallel:
                self.SP_729G.sw.off()
                self.SP_729L1.sw.off()
                self.trigger.sw.off()
            
            delay(1*ms)