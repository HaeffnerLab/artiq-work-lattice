from artiq import *
from artiq.language import *

class change_cw(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.specs = self.get_argument("specs", PYONValue())
        for key in self.specs.keys():
            print(self.specs[key]["state"])
        # self.frequency = self.get_argument("frequency", NumberValue(80, unit="MHz"))
        # self.amplitude = self.get_argument("amplitude", NumberValue(30, unit="dB"))
        # self.state = self.get_argument("state", BooleanValue())
        # urukul_number = self.get_argument("urukul_number", StringValue("0"))
        # dds_name = self.get_argument("dds_name", StringValue("397"))
        self.ddss = {dds_name: self.get_device(dds_name) for dds_name in self.specs.keys()}
        self.cplds = [self.get_device("urukul{}_cpld".format(i)) for i in range(3)]


    def prepare(self):
        self.archive = False

    @kernel
    def run(self):
        if self.scheduler.check_pause():
            return
        self.core.reset()
        for cpld in self.cplds:
            cpld.init()
        for dds in self.ddss.values():
            dds.init()
        for dds in self.ddss.keys():
            if self.specs[dds]["state"]:
                self.ddss[dds].sw.on()
            else:
                self.ddss[dds].sw.off()
            self.ddss[dds].set(self.specs[dds]["frequency"])
            self.ddss[dds].set_att(self.specs[dds]["att"])
        
        
        # if self.state:
        #     self.dds.sw.on()
        # else:
        #     self.dds.sw.off()
        # self.dds.set(self.frequency)
        # self.dds.set_att(self.amplitude)

    def analyze(self):
        pass
        #print(self.frequency)
        #print(self.frequency*MHz)
        #print(self.amplitude)
        #print(self.amplitude*dB)


