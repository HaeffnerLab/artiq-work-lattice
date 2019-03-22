from itertools import count

from artiq.experiment import *
from artiq.master.worker_db import DeviceError
from artiq.coredevice.ad9910 import AD9910, PHASE_MODE_TRACKING
from artiq.coredevice.ad9912 import AD9912

class TestUrukulSync(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        
        self.cplds = []
        self.channels = []
        
        for i in [1, 2]:
            try:
                cpld = self.get_device("urukul{}_cpld".format(i))
            except DeviceError:
                raise
            channel = self.get_device("urukul{}_ch0".format(i))
            if isinstance(channel, AD9910):
                self.cplds.append(cpld)
                self.channels.append(channel)
                self.channels += [self.get_device("urukul{}_ch{}".format(i, j)) for j in range(1, 2)]
            
        print("found {} Urukul AD9910 cards".format(len(self.cplds)))
        print([channel.sync_delay_seed for channel in self.channels])
        print([channel.io_update_delay for channel in self.channels])

    @kernel
    def run(self):
        self.core.reset()
        for cpld in self.cplds:
            cpld.init()
        for channel in self.channels:
            self.core.break_realtime()
            channel.init()
            channel.set(9*MHz, phase_mode=PHASE_MODE_TRACKING, ref_time_mu=42)
            channel.sw.on()
            channel.set_att(6.)
            delay(1*ms)
            channel.set_frequency(20*MHz) 
           # delay(50*us)
           # channel.set(9*MHz)
           # delay(50*us)
           # channel.sw.off()
