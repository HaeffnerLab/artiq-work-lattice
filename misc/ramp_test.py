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
        # Start by disabling ramping and resetting to profile 0.
        #
        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse(1*us)
        self.dds.cpld.set_profile(0)
        self.dds.cpld.io_update.pulse(1*us)

        #
        # Create the list of amplitudes for the ramp and corresponding
        # register values.
        # NOTE: AD9910 plays back the amplitudes in the reverse order
        #       of how they are written. So for a ramp-up, one must
        #       construct the list from largest to smallest.
        #
        n_steps = 50
        max_amplitude = 1.0
        amps = [max_amplitude/n_steps * (float(n_steps)-i) for i in range(n_steps+1)]
        data = [0]*(n_steps+1)
        # NOTE: The built-in amplitude_to_ram() method does not
        #       comply with the AD9910 specification. Doing this
        #       manually instead, until amplitude_to_ram() is fixed.
        # self.dds.amplitude_to_ram(amps, data)
        for i in range(len(amps)):
            data[i] = (np.int32(round(amps[i]*0x3fff)) << 18)

        #
        # Print the list of amplitudes and corresponding register values.
        #
        print("amps:", amps)
        print("data:", data)
        self.core.break_realtime()

        #
        # Program the RAM with the ramp-up waveform and ramp mode.
        #
        ramp_up_profile = 3  # arbitrary choice, must be 0 to 7
        start_address = 100  # arbitrary choice, must be 0 to (1024-n_steps-1)
        delay(1*ms) # to avoid RTIO underflow
        self.dds.set_profile_ram(
               start=start_address,
               end=start_address + n_steps,
               step=4,
               nodwell_high=0,
               profile=ramp_up_profile,
               mode=RAM_MODE_RAMPUP)
        delay(1*ms) # to avoid RTIO underflow
        self.dds.cpld.set_profile(ramp_up_profile)
        self.dds.cpld.io_update.pulse(1*us)
        delay(1*ms) # to avoid RTIO underflow
        self.dds.write_ram(data)

        #
        # Program the RAM with the ramp-down waveform.
        #
        ramp_down_profile = 5  # arbitrary choice, must be 0 to 7
        start_address = 200  # arbitrary choice, must be 0 to (1024-n_steps-1)
        delay(1*ms) # to avoid RTIO underflow
        self.dds.set_profile_ram(
               start=start_address,
               end=start_address + n_steps,
               step=4,
               nodwell_high=0,
               profile=ramp_down_profile,
               mode=RAM_MODE_RAMPUP)
        delay(1*ms) # to avoid RTIO underflow
        self.dds.cpld.set_profile(ramp_down_profile)
        self.dds.cpld.io_update.pulse(1*us)
        delay(1*ms) # to avoid RTIO underflow
        reversed_data = [0]*(n_steps+1) # reverse the ramp-up data for this ramp-down waveform
        for i in range(len(data)):
            reversed_data[i] = data[len(data)-i-1]
        self.dds.write_ram(reversed_data)
        
        #
        # Now set the desired initial parameters and turn on the DDS.
        #
        self.dds.set_frequency(80.3*MHz)
        self.dds.set_amplitude(0.)
        self.dds.set_att(8*dB)
        self.dds.sw.on()

        #
        # Set the current profile to the ramp-up profile constructed above.
        #
        self.dds.cpld.set_profile(ramp_up_profile)
        self.dds.cpld.io_update.pulse(1*us)

        #
        # Finally, enable the ramping. This immediately starts
        # playing back the waveform programmed above.
        #
        self.dds.set_cfr1(ram_enable=1, ram_destination=RAM_DEST_ASF)
        self.dds.cpld.io_update.pulse(1*us)

        #
        # Wait for some time. The output should remain at the high level.
        #
        delay(5*us)

        #
        # Activate the ramp-down profile. This immediately starts
        # playing back the ramp-down waveform.
        #
        self.dds.cpld.set_profile(ramp_down_profile)
        self.dds.cpld.io_update.pulse(1*us)

        #
        # Wait for some time. The output should remain at the low level.
        #
        delay(2*us)

        #
        # Turn off the DDS.
        #
        self.dds.sw.off()

        #
        # Disable ramping so we don't affect the next experiment.
        # Also reset to profile 0.
        #
        self.dds.set_cfr1(ram_enable=0)
        self.dds.cpld.io_update.pulse(1*us)
        self.dds.cpld.set_profile(0)
        self.dds.cpld.io_update.pulse(1*us)

        #
        # Turn on the 397 and 866 so we don't lose our ions.
        #
        self.dds_397.set(78*MHz)
        self.dds_397.set_att(5*dB)
        self.core.break_realtime()
        self.dds_866.set(80*MHz)
        self.dds_866.set_att(5*dB)
        self.core.break_realtime()
        self.dds_397.sw.on()
        self.dds_866.sw.on()