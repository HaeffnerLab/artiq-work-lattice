from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_BIDIR_RAMP, RAM_MODE_RAMPUP, RAM_DEST_ASF, RAM_MODE_DIRECTSWITCH


class RampTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("729G")
        self.cpld = self.get_device("urukul0_cpld")

        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")

    @kernel
    def run(self):
        self.core.reset()
        self.cpld.init()
        self.dds.init()
        self.core.break_realtime()

        n_steps = 10
        amps = [.1 * i for i in range(1, n_steps+1)]
        data = [0]*n_steps
        #self.dds.amplitude_to_ram(amps, data)

        for i in range(len(data)):
            amplitude_step_size = 0x00
            amplitude_scale_factor = self.dds.amplitude_to_asf(amps[i])
            amplitude_ramp_rate = 10   # clock cycles per step
            data[i] = (amplitude_step_size |
                       amplitude_scale_factor << 2 |
                       amplitude_ramp_rate << 16)

        print(data)
        self.core.break_realtime()

        self.dds.set_profile_ram(
               start=0, end=n_steps - 1, step=100,
               profile=0, mode=RAM_MODE_DIRECTSWITCH)
        self.dds.cpld.set_profile(0)
        #self.dds.cpld.io_update.pulse_mu(8)
        #delay(1*ms)
        self.dds.write_ram(data)
        self.dds.set_cfr1(ram_enable=1, ram_destination=RAM_DEST_ASF)
        self.dds.cpld.io_update.pulse_mu(8)
        delay(1*ms)

        self.core.break_realtime()

        #self.dds.set(220*MHz, amplitude=1., profile=0)
        self.dds.set_frequency(220*MHz)
        #self.dds.cpld.io_update.pulse_mu(8)
        self.dds.set_att(5*dB)
        
        #self.dds.cpld.set_profile(0)
        self.dds.sw.on()
        delay(10000*ms)
        self.dds.sw.off()

        # turn on the 397 and 866 so we don't lose our ions
        self.dds_397.set(78*MHz)
        self.dds_397.set_att(5*dB)
        self.core.break_realtime()
        self.dds_866.set(80*MHz)
        self.dds_866.set_att(5*dB)
        self.core.break_realtime()
        self.dds_397.sw.on()
        self.dds_866.sw.on()