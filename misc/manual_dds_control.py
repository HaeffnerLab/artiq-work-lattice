from artiq import *
from artiq.language import *

class change_cw(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        #self.setattr_device("scheduler")
        self.specs = self.get_argument("specs", PYONValue())
        self.dds_dict = dict()
        try:
            for name in self.specs.keys():
                self.setattr_device(name)
                self.dds_dict[name] = self.get_device(name)
        except AttributeError:
            pass
        self.cpld_list = [self.get_device("urukul{}_cpld".format(i)) for i in range(3)]

    def prepare(self):
        self.archive = False
        self.dds_list = []
        self.freq_list = []
        self.att_list = []
        self.state_list = []
        self.amp_list = []
        self.dds_name_list = []
        for dds, settings in self.specs.items():
            self.dds_name_list.append(dds)
            print(dds)
            self.dds_list.append(self.dds_dict[dds])
            self.freq_list.append(settings["frequency"])
            self.att_list.append(settings["att"])
            self.state_list.append(settings["state"])
            self.amp_list.append(settings["amplitude"])

    @kernel
    def run(self):
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        self.core.break_realtime()
        with parallel:
            for i in range(len(self.dds_list)):
               # print(self.dds_name_list[i])
                self.dds_list[i].init()
                delay(1*ms)
                self.dds_list[i].set(self.freq_list[i],
                                     amplitude=self.amp_list[i])
                self.dds_list[i].set_att(self.att_list[i]*dB)
                if self.state_list[i]:
                    self.dds_list[i].sw.on()
                else:
                    self.dds_list[i].sw.off()
