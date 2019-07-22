from artiq.experiment import *


class rf_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("729G")
        self.dds2 = self.get_device("729L1")

    @kernel
    def run(self):
        self.core.reset()
        
        self.dds.set(2*MHz, amplitude=1.)
        self.dds.set_att(5*dB)

        self.core.break_realtime()

        self.dds2.set(2*MHz, amplitude=1.)
        self.dds2.set_att(5*dB)

        self.core.break_realtime()

        with parallel:
            self.dds.sw.on()
            self.dds2.sw.on()

        delay(2*us)
        self.dds.sw.off()
        delay(1*us)

        #delay(20*ns)

        self.dds.set(10*MHz, amplitude=1.)
        self.dds.sw.on()
        delay(2*us)
        self.dds.sw.off()
        delay(1*us)
        #delay(20*ns)

        self.dds.set(2*MHz, amplitude=1.)
        self.dds.sw.on()
        delay(1*us)

        with parallel:
            self.dds.sw.off()
            self.dds2.sw.off()
