from artiq.experiment import *

from artiq.coredevice.ad9910 import (
    PHASE_MODE_TRACKING, PHASE_MODE_CONTINUOUS,PHASE_MODE_ABSOLUTE,  RAM_MODE_CONT_RAMPUP, 
    RAM_DEST_ASF, RAM_DEST_FTW, RAM_MODE_RAMPUP
)

import numpy as np


class test_noise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        # self.dds = self.get_device("SP_729G_bichro")
        self.dds = self.get_device("urukul1_ch2")
        self.ttl = self.get_device("blue_PIs")

    # def prepare(self):
    #     start_index = 0
    #     end_index = 1
    #     self.n_steps = end_index - start_index
    #     # ramp = [i*MHz for i in range(n_steps)]
    #     # ramp = [0.2 * (i%2) + 0.1 for i in range(self.n_steps)]
    #     ramp = [1.]
    #     # print(ramp)
    #     self.ramp_data = [0] * self.n_steps

    #     self.dds.amplitude_to_ram(ramp, self.ramp_data)
    #     # self.dds.frequency_to_ram(ramp, self.ramp_data)


    # @kernel
    # def run(self):
    #     self.core.reset()
    #     self.dds.cpld.init()
    #     self.dds.init()
        
    #     self.core.break_realtime()

    #     self.dds.set_phase_mode(PHASE_MODE_ABSOLUTE)
        
    #     ref_time = now_mu()
    #     self.dds.set(80*MHz, ref_time_mu=ref_time, amplitude=0., profile=0)
    #     self.dds.set(80*MHz, ref_time_mu=ref_time, amplitude=0.5, profile=1)
    #     self.dds.set(80*MHz, ref_time_mu=ref_time, amplitude=1.0, profile=2)
    #     self.dds.set_att(5*dB)

    #     delay(5*us)
    #     self.dds.set_cfr1(ram_enable=0)
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     # self.dds.cpld.set_profile(0)
    #     # self.dds.cpld.io_update.pulse_mu(8)

    #     clock_cycles_per_step = 500
    #     start_address = 0
    #     self.dds.set_profile_ram(
    #                 start=start_address,
    #                 end=start_address + self.n_steps - 1,
    #                 step=clock_cycles_per_step,
    #                 profile=0,
    #                 # mode=RAM_MODE_CONT_RAMPUP
    #             )
    #     self.dds.cpld.set_profile(0)
    #     delay(10*us)
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     delay(10*us)
    #     self.dds.write_ram(self.ramp_data)
    #     delay(10*us)
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     self.dds.cpld.set_profile(0)
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     # self.dds.set_cfr1(ram_enable=1, ram_destination=RAM_DEST_ASF)#, internal_profile=0)
    #     # self.dds.cpld.io_update.pulse_mu(8)

    #     while True:
    #         # self.dds.set(10*MHz, profile=0)
    #         self.dds.cpld.set_profile(0)
    #         self.dds.cpld.io_update.pulse_mu(8)
    #         delay(10*us)
    #         self.dds.set_profile_ram(
    #                 start=start_address,
    #                 end=start_address + self.n_steps - 1,
    #                 step=clock_cycles_per_step,
    #                 profile=0,
    #                 # mode=RAM_MODE_CONT_RAMPUP
    #             )0.


    #         self.dds.set_cfr1(internal_profile=0, ram_enable=1, ram_destination=RAM_DEST_ASF)
    #         self.dds.sw.on()
    #         delay(10*us)
    #         self.dds.cpld.io_update.pulse_mu(8)
    #         self.ttl.on()
    #         delay(100*us)
    #         self.dds.set_cfr1(ram_enable=0)
    #         self.dds.cpld.set_profile(1)
    #         self.dds.cpld.io_update.pulse_mu(8)
    #         delay(100*us)
    #         self.dds.sw.off()
    #         self.ttl.off()
    #         delay(100*us)

    # def prepare(self):
    #     # prepare frequency array
    #     freq1 = [10e6, 30e6, 90e6]
    #     self.data1 = [0] * 3
    #     self.dds.frequency_to_ram(freq1,self.data1)
    #     # prepare time step array
    #     # in units of 4ns: 100us, 200us, 1ms, 100ms, 10s
    #     # for a 16-bit integer, the last 3 values should be max value of around 260us
    #     self.steps = np.array([100] * 5)


    # @kernel
    # def run(self):
    #     self.core.break_realtime()
    #     self.dds.cpld.init()
    #     self.dds.init()
    #     self.dds.sw.off()
    #     # ref_time = now_mu()
    #     # self.dds.set(80*MHz)
    #     self.dds.set_amplitude(1.0)
    #     self.dds.set_att(0.0)
    #     while True:
    #         for t in range(len(self.steps)):
    #             self.run_ram(self.steps[t])
        
       
    # @kernel
    # def run_ram(self, timestep_mu):
    #     # prepare ram
    #     delay(5 * us)
    #     self.dds.set_cfr1(ram_enable=0)
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     self.dds.set_profile_ram(start=0, end=2, step=timestep_mu,
    #                              profile=0, mode=RAM_MODE_CONT_RAMPUP)
    #     self.dds.cpld.set_profile(0)
    #     delay(10 * us) 
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     delay(10 * us)
    #     self.dds.write_ram(self.data1)
    #     # prepare to enable ram and set frequency as target
    #     delay(10 * us)
    #     self.dds.set_cfr1(
    #                 internal_profile=0, 
    #                 ram_enable=1, 
    #                 ram_destination=RAM_DEST_FTW, 
    #                 osk_enable=1,
    #                 manual_osk_external=0,
    #                 select_auto_osk=0
    #             )
    #     self.dds.set_amplitude(1.)
    #     # sent trigger and ramp for 1ms
    #     with parallel:
    #         self.dds.sw.on()
    #         self.ttl.pulse(5 * us)
    #     self.dds.cpld.io_update.pulse_mu(8)
    #     delay(1 * ms)
    #     self.dds.set_cfr1(ram_enable=0)
    #     self.dds.sw.off()
 

    def prepare(self):
        # prepare frequency array
        amp1 = [0.01, 0.25, 0.5, 0.75, 0.95]
        self.data1 = [0] * len(amp1)
        self.dds.amplitude_to_ram(amp1, self.data1)
        # for i in range(len(amp1)):
        #         self.data1[i] = np.int32((np.int32(round(amp1[i]*0xffff)) << 16))
        # prepare time step array
        # in units of 4ns: 100us, 200us, 1ms, 100ms, 10s
        # for a 16-bit integer, the last 3 values should be max value of around 260us
        self.steps = np.array([1000])

        # n = len(amp1)                                                              #defines variable n for list length exponent
        # self.data1 = [0]*(1 << n)                                                 #declares list as 2^n integer values
        # for i in range(len(self.data1)//2):                                       #splits list into 2 halves and defines each separately
        #     self.data1[i] = i << (32 - (n - 1))                                   #first half ramps up to maximum amplitude in machine units
        #     self.data1[i + len(amp1)//2] = 0xffff << 16                           #second half holds maximum amplitude


    @kernel
    def run(self):
        self.core.reset()
        self.dds.cpld.init()
        self.dds.init()
        self.dds.sw.off()
        self.dds.set(100*MHz, profile=0, amplitude=0.1)
        self.dds.set_amplitude(1.0)
        self.dds.set_att(5 * dB)
        self.core.break_realtime()
        while True:
            for t in range(len(self.steps)):
                self.run_ram(self.steps[t])
                delay(1*ms)
       
    @kernel
    def run_ram(self, timestep_mu):
        self.dds.cpld.io_update.pulse_mu(8)
        # prepare ram
        delay(5 * us)
        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse_mu(8)
        self.dds.set_profile_ram(
                        start=0, 
                        end=4, 
                        step=timestep_mu,
                        profile=0, 
                        mode=2
                    )
        self.dds.cpld.set_profile(0)
        # self.dds.set_frequency(100*MHz)
        delay(10 * us) 
        self.dds.cpld.io_update.pulse_mu(8)
        delay(10 * us)
        self.dds.write_ram(self.data1)
        # prepare to enable ram and set frequency as target
        delay(10 * us)
        self.dds.set_cfr1(
                    internal_profile=0, 
                    ram_enable=1, 
                    ram_destination=RAM_DEST_ASF, 
                    # osk_enable=1,
                    manual_osk_external=0,
                    # select_auto_osk=0
                )
        # self.dds.set_amplitude(1.)
        # sent trigger and ramp for 1ms
        with parallel:
            self.dds.sw.on()
            self.ttl.pulse(5 * us)
        self.dds.cpld.io_update.pulse_mu(8)
        # self.dds.set_amplitude(0.)
        delay(500 * us)
        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse_mu(8)
        self.dds.sw.off()
 