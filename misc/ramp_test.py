from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_BIDIR_RAMP, RAM_MODE_CONT_BIDIR_RAMP, RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, RAM_DEST_ASF, RAM_DEST_FTW, RAM_MODE_DIRECTSWITCH
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS
import numpy as np


class RampTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("SP_729G_bichro")

        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")

    @kernel
    def run(self):
        self.core.reset()
        self.dds.cpld.init()
        self.dds.init()
        self.core.break_realtime()

        #
        # start by disabling ramping and resetting to profile 0
        #
        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse(1*us)
        self.dds.cpld.set_profile(0)
        self.dds.cpld.io_update.pulse(1*us)
        #
        # first, try some naive ramping.
        # each set() call takes a little over 1us,
        # so this isn't fast enough for us.
        #
        self.dds.set(80.3*MHz, amplitude=0., profile=0)
        self.dds.set_att(8*dB)

        self.dds.sw.on()

        # self.dds.set(80.3*MHz, amplitude=0.2)
        # self.dds.set(80.3*MHz, amplitude=0.4)
        # self.dds.set(80.3*MHz, amplitude=0.6)
        # self.dds.set(80.3*MHz, amplitude=0.8)
        # self.dds.set(80.3*MHz, amplitude=1.)

        delay(5*us)
        self.dds.sw.off()

        #
        # use the auto OSK on the AD9910
        # -- unfortunately, OSK is not currently supported through Urukul.
        #
        # self.dds.set(80.3*MHz, amplitude=0., profile=0)
        # self.dds.sw.on()

        # self.dds.set_cfr1(auto_osk=1, osk_enable=1)
        # amplitude_step_size = 0
        # amplitude_ramp_rate = 1
        # asf_reg_value = (
        #     amplitude_step_size |
        #     (self.amplitude_to_asf(1.) << 2) |
        #     (amplitude_ramp_rate << 16)
        # )


        #
        # now, try to use built-in RAM ramping
        # on the AD9910
        #
        #self.dds.cpld.set_profile(0)
        #self.dds.cpld.io_update.pulse(1*us)

        n_steps = 10
        amps = [1./n_steps * i for i in range(1, n_steps+1)]
        data = [0]*n_steps
        #self.dds.amplitude_to_ram(amps, data)
        # or - calculating manually seems to work better:
        for i in range(len(amps)):
            data[i] = (np.int32(round(amps[i]*0x3fff)) << 18)

        # freqs = [1*MHz, 5*MHz, 20*MHz, 40*MHz, 80*MHz] #[40*MHz + ((80*MHz/n_steps) * i) for i in range(i, n_steps+1)]
        # n_steps = len(freqs)
        # self.dds.frequency_to_ram(freqs, data)

        print("amps:", amps)
        print("data:", data)
        self.core.break_realtime()

        ram_profile = 3
        start_address = 100
        delay(1*ms)
        self.dds.set_profile_ram(
               start=start_address, end=start_address + n_steps - 1,
               step=100, nodwell_high=0,
               profile=ram_profile, mode=RAM_MODE_RAMPUP)
        delay(1*ms)

        self.dds.cpld.set_profile(ram_profile)
        self.dds.cpld.io_update.pulse(1*us)
        delay(1*ms)
        self.dds.write_ram(data)
        
        #self.dds.set(80.3*MHz, amplitude=1., profile=0)
        self.dds.set_frequency(80.3*MHz)
        self.dds.sw.on()

        self.dds.set_cfr1(ram_enable=1, ram_destination=RAM_DEST_ASF)
        self.dds.cpld.io_update.pulse(1*us)

        #self.dds.set(80.3*MHz, amplitude=1., profile=ram_profile,
        #             phase_mode=PHASE_MODE_CONTINUOUS)

        #self.dds.set(80.3*MHz, amplitude=0., profile=0)
        #delay(5*us)
        #self.dds.set(80.3*MHz, amplitude=1., profile=0)

        delay(100*us)
        
        self.dds.sw.off()

        #
        # disable ramping again so we don't affect the next experiment
        #
        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse(1*us)
        self.dds.cpld.set_profile(0)
        self.dds.cpld.io_update.pulse(1*us)

        #
        # turn on the 397 and 866 so we don't lose our ions
        #
        self.dds_397.set(78*MHz)
        self.dds_397.set_att(5*dB)
        self.core.break_realtime()
        self.dds_866.set(80*MHz)
        self.dds_866.set_att(5*dB)
        self.core.break_realtime()
        self.dds_397.sw.on()
        self.dds_866.sw.on()