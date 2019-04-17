from artiq import *
from artiq.language import *


class change_cw11(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("397")
        self.dds1 = self.get_device("866")
        self.cpld = self.get_device("urukul0_cpld")

    def run(self):
        self.core.reset()
        #self.cpld.init()
        #self.dds_init([self.dds, self.dds1])
        #self.dds.set(80*MHz)
        #self.dds.set_att(25*dB)
        #self.dds.sw.on()
        #self.dds1.set(100*MHz)
        #self.dds1.set_att(25*dB)
        #self.dds1.sw.on()
        self.set_dds([self.dds, self.dds1], [False, False], [100*MHz, 80*MHz], [10, 20])
        #self.set_dds(self.dds1, True, 80*MHz, 20)

    @kernel
    def set_dds(self, dds_list, state_list, frequency_list, att_list):
        self.core.break_realtime()
        with parallel:
            for i in range(len(dds_list)):
                dds_list[i].init()
                dds_list[i].set(frequency_list[i])
                dds_list[i].set_att(att_list[i]*dB)
                if state_list[i]:
                    dds_list[i].sw.on()
                else:
                    dds_list[i].sw.off()
        #dds.init()
        #dds.set(frequency)
        #dds.set_att(att*dB)
        #if state:
        #    dds.sw.on()
        #else:
        #    dds.sw.off()

    @kernel
    def dds_init(self, dds_list):
        self.core.break_realtime()
        for dds in dds_list:
            dds.init()
