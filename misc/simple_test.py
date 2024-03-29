from artiq.experiment import *
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS


class phase_slip_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("397")
        self.dds1 = self.get_device("866")
        self.dds2 = self.get_device("397")
        self.dds3 = self.get_device("397")
        # self.dds = self.get_device("729G")
        self.ttl = self.get_device("pmt")
        self.led0 = self.get_device("led0")
        self.led1 = self.get_device("led1")

    @kernel
    def run(self):
        self.core.reset()
        self.dds.cpld.init()
        self.dds.init()
        self.dds1.cpld.init()
        self.dds1.init()
        self.dds2.cpld.init()
        self.dds2.init()
        self.dds3.cpld.init()
        self.dds3.init()
        self.core.break_realtime()
        self.dds.set(80*MHz, amplitude=1.0)
        self.dds.set_att(5.)
        self.dds.sw.on()
        self.dds1.sw.on()
        self.dds2.sw.on()
        self.dds3.sw.on()
        #self.led1.off()
        #self.dds.init()
        #self.dds.set(20*MHz, amplitude=1.0)
        #self.dds.set_att(5*dB)

