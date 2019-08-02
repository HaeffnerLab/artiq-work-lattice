from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_BIDIR_RAMP, RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, RAM_DEST_ASF, RAM_DEST_FTW, RAM_MODE_DIRECTSWITCH


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

        n_steps = 30
        data = [0]*n_steps

        #amps = [1./n_steps * i for i in range(1, n_steps+1)]
        #self.dds.amplitude_to_ram(amps, data)
        # or - calculate manually:
        #for i in range(len(amps)):
        #    data[i] = self.dds.amplitude_to_asf(amps[i])

        freqs = [(i+n_steps)*80300000./(2.*n_steps) for i in range(i, n_steps+1)]
        self.dds.frequency_to_ram(freqs, data)

        print(data)
        self.core.break_realtime()

        # self.core.break_realtime()

        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse_mu(8)

        self.dds.set(80.3*MHz, amplitude=1., profile=0)
        self.dds.set_att(8*dB)
        
        self.dds.sw.on()

        start_address = 200
        delay(1*ms)
        self.dds.set_profile_ram(
               start=start_address, end=start_address + n_steps - 1,
               step=1, nodwell_high=0,
               profile=0, mode=RAM_MODE_RAMPUP)
        delay(1*ms)
        self.dds.cpld.set_profile(0)
        self.dds.cpld.io_update.pulse_mu(8)
        delay(1*ms)
        self.dds.write_ram(data)

        self.dds.set_cfr1(ram_enable=1,
            #ram_destination=RAM_DEST_ASF)
            ram_destination=RAM_DEST_FTW)
        self.dds.cpld.io_update.pulse_mu(8)
        #delay(1*ms)

        self.dds.set(80.3*MHz, amplitude=1., profile=0)

        delay(1000*ms)
        self.dds.sw.off()

        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse_mu(8)

        # turn on the 397 and 866 so we don't lose our ions
        self.dds_397.set(78*MHz)
        self.dds_397.set_att(5*dB)
        self.core.break_realtime()
        self.dds_866.set(80*MHz)
        self.dds_866.set_att(5*dB)
        self.core.break_realtime()
        self.dds_397.sw.on()
        self.dds_866.sw.on()