from artiq import *
from artiq.language import *

class change_cw(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.specs = self.get_argument("specs", PYONValue())
        # self.frequency = self.get_argument("frequency", NumberValue(80, unit="MHz"))
        # self.amplitude = self.get_argument("amplitude", NumberValue(30, unit="dB"))
        # self.state = self.get_argument("state", BooleanValue())
        # urukul_number = self.get_argument("urukul_number", StringValue("0"))
        # dds_name = self.get_argument("dds_name", StringValue("397"))
        # self.ddss = {dds_name: self.get_device(dds_name) for dds_name in self.specs.keys()}
        self.dds_dict = dict()
        try:
            for name in self.specs.keys():
                self.setattr_device(name)
                self.dds_dict[name] = self.get_device(name)
        except AttributeError:
            pass

    def prepare(self):
        self.archive = False
        self.dds_list = []
        self.freq_list = []
        self.att_list = []
        self.state_list = []
        for dds, settings in self.specs.items():
            self.dds_list.append(self.dds_dict[dds])
            self.freq_list.append(settings["frequency"])
            self.att_list.append(settings["att"])
            self.state_list.append(settings["state"])

    @kernel
    def run(self):
        self.core.reset()
        if self.scheduler.check_pause():
            return
        self.core.break_realtime()
        with parallel:
            for i in range(len(self.dds_list)):
                self.dds_list[i].init()
                self.dds_list[i].set(self.freq_list[i])
                self.dds_list[i].set_att(self.att_list[i]*dB)
                if self.state_list[i]:
                    self.dds_list[i].sw.on()
                else:
                    self.dds_list[i].sw.off()

        # self.core.break_realtime()
        # for dds in list(self.ddss.values())[0:1]:
        #     # self.core.break_realtime()
        #     self.init_dds(dds)
        # for dds in list(self.ddss.keys())[0:1]:
        #     self.set_dds(self.ddss[dds], 
        #                 self.specs[dds]["state"], 
        #                 self.specs[dds]["frequency"], 
        #                 float(self.specs[dds]["att"]))
            # if self.specs[dds][self.state]:
            #     self.ddss[dds].sw.on()
            # else:
            #     self.ddss[dds].sw.off()
            # self.ddss[dds].set(self.specs[dds]["frequency"])
            # self.ddss[dds].set_att(self.specs[dds]["att"])        

    # def run(self):
    #     if self.scheduler.check_pause():
    #         return
    #     self.core.reset()
    #     for cpld in self.cplds:
    #         cpld.init()
    #     for dds in self.ddss.values():
    #         dds.init()
    #     for dds 
        # for dds in self.ddss.keys():
        #     if self.specs[dds][self.state]:
        #         self.ddss[dds].sw.on()
        #     else:
        #         self.ddss[dds].sw.off()
        #     self.ddss[dds].set(self.specs[dds]["frequency"])
        #     self.ddss[dds].set_att(self.specs[dds]["att"])
        
        
        # if self.state:
        #     self.dds.sw.on()
        # else:
        #     self.dds.sw.off()
        # self.dds.set(self.frequency)
        # self.dds.set_att(self.amplitude)

    # def analyze(self):
    #     pass
    #     #print(self.frequency)
    #     #print(self.frequency*MHz)
    #     #print(self.amplitude)
    #     #print(self.amplitude*dB)

    # @kernel
    # def set_dds(self, dds, state, frequency, att):
    #     dds.set(frequency)
    #     dds.set_att(att*dB)
    #     if state:
    #         dds.sw.on()
    #     else:
    #         dds.sw.off()

    # @kernel
    # def init_dds(self, dds):
    #     dds.init()

    # @kernel
    # def init_cpld(self, cpld):
    #     cpld.init()
