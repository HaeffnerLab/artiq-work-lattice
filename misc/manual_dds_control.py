from artiq import *
from artiq.language import *

class change_cw(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.frequency = self.get_argument("frequency", NumberValue(80, unit="MHz"))
        self.amplitude = self.get_argument("amplitude", NumberValue(30, unit="dB"))
        self.state = self.get_argument("state", BooleanValue())
        urukul_number = self.get_argument("urukul_number", StringValue("0"))
        dds_name = self.get_argument("dds_name", StringValue("397"))
        self.dds = self.get_device(dds_name)
        self.cpld = self.get_device("urukul{}_cpld".format(urukul_number))

    def prepare(self):
        self.archive = False

    @kernel
    def run(self):
        if self.scheduler.check_pause():
            return
        self.core.reset()
        # self.core.break_realtime()
        # self.cpld.init()
        self.dds.init()
        if self.state:
            self.dds.sw.on()
        else:
            self.dds.sw.off()
        self.dds.set(self.frequency)
        self.dds.set_att(self.amplitude)

    def analyze(self):
        pass
        #print(self.frequency)
        #print(self.frequency*MHz)
        #print(self.amplitude)
        #print(self.amplitude*dB)


