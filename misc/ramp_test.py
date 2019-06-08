from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_BIDIR_RAMP, RAM_DEST_ASF


class RampTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("SP_729L2")
        self.cpld = self.get_device("urukul2_cpld")

    @kernel
    def run(self):
        self.core.reset()
        self.cpld.init()
        self.dds.init()
        self.core.break_realtime()

        amps = [.1 * i for i in range(1, 10)]
        r = [0]*10
        print(self.dds.amplitude_to_ram(amps, r))


        n = 10
        data = [0]*(1 << n)
        for i in range(len(data)//2):
            data[i] = i << (32 - (n - 1))
            data[i + len(data)//2] = 0xffff << 16
        self.dds.cpld.get_att_mu()
        self.core.break_realtime()

        self.dds.set_profile_ram(
                start=0, end=0 + len(data) - 1, step=1,
                profile=0, mode=RAM_MODE_BIDIR_RAMP
            )
        self.dds.cpld.set_profile(0)
        self.dds.cpld.io_update.pulse_mu(8)
        delay(1*ms)
        self.dds.write_ram(data)
        delay(1*ms)
        self.dds.set_cfr1(ram_enable=1, ram_destination=RAM_DEST_ASF)

        self.core.break_realtime()

        self.dds.set(80*MHz, amplitude=1., profile=0)
        self.dds.cpld.io_update.pulse_mu(8)
        self.dds.set_att(5*dB)
        self.dds.sw.on()

        r = [0]*len(data)
        self.dds.read_ram(r)
        #for i in range(len(data)):
        #    assert r[i] == data[i]
        self.core.break_realtime()
        while True:
            self.dds.cpld.set_profile(0)
            self.dds.sw.on()
            delay(1*ms)
            self.dds.sw.off()
