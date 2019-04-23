from artiq.pulse_sequence import PulseSequence

from artiq.experiment import *

class pstest(PulseSequence):

    @kernel
    def sequence(self):
        self.core.break_realtime()
        self.dds_729L1.sw.on()
        delay(1*ms)
        self.dds_729L1.sw.off()
