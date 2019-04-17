from artiq import *
from artiq.language import *

class change_cw11(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("397")
        self.dds1 = self.get_device("866")
        self.cpld = self.get_device("urukul0_cpld")

    @kernel
    def run(self):
        self.core.reset()
        #self.cpld.init()
        self.dds.init()
        self.dds1.init()
        self.dds.set(80*MHz)
        self.dds.set_att(25*dB)
        self.dds.sw.on()
        self.dds1.set(100*MHz)
        self.dds1.set_att(25*dB)
        self.dds1.sw.on()
        #self.set_dds(self.dds, False, 80*MHz, 20)

    @kernel
    def set_dds(self, dds, state, frequency, att):
        self.core.break_realtime()
        dds.init()
        if state:
            dds.sw.on()
        else:
            dds.sw.off()
        dds.set(frequency)
        dds.set_att(att*dB)
