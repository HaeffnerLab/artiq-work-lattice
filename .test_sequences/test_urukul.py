from artiq.experiment import *

class TestUrukul(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.cpld = self.get_device("urukul2_cpld")
        self.channel = self.get_device("urukul2_ch0")


    @kernel
    def run(self):
        self.core.reset()
        self.cpld.init()
        self.core.break_realtime()
        self.channel.init()
        self.channel.set(220*MHz)
        self.channel.sw.on()
        i=50
        while True:
            delay(1*ms)
            self.channel.sw.off()
            delay(1*us)
            self.channel.sw.on()
            delay_mu(i)
            self.channel.sw.off()
            #print(self.core.mu_to_seconds(i))

