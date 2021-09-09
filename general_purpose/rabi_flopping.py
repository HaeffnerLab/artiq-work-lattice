from pulse_sequence import PulseSequence
from subsequences.rabi_excitation_with_stark_shift import RabiExcitationWithStarkShift
from subsequences.composite_pi import CompositePi #added for composite_pi 02/20/2020
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *


class RabiFlopping(PulseSequence):
    PulseSequence.accessed_params = {
        "RabiFlopping.line_selection",
        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.channel_729",
        "RabiFlopping.duration",
        "RabiFlopping.selection_sideband",
        "RabiFlopping.order",
        "RabiFlopping.detuning",
        "RabiFlopping.composite_pi_rotation",
        "RabiFlopping.noise",
        "Excitation_729.stark_shift_on",
        "Excitation_729.stark_shift_detuning",
        "Excitation_729.stark_shift_amplitude",
        "Excitation_729.stark_shift_att"
    }#

    PulseSequence.scan_params = dict(
        RabiFlopping=[
            ("Rabi", ("RabiFlopping.duration", 0., 100e-6, 20, "us")),
            ("Rabi", ("RabiFlopping.att_729", 0*dB, 32*dB, 1*dB, "dB")),
            ("Rabi", ("RabiFlopping.detuning", -100*kHz, 100*kHz, 1, "kHz")),
            ("Rabi", ("RabiFlopping.amplitude_729", 0.0, 1.0, 20))
        ])

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitationWithStarkShift)
        self.composite = self.add_subsequence(CompositePi)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.composite.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["RabiFlopping"] = self.set_subsequence_rabiflopping

    @kernel
    def set_subsequence_rabiflopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")
        self.rabi.amp_729 = self.get_variable_parameter("RabiFlopping_amplitude_729")
        self.rabi.freq_729 = self.calc_frequency(
                                self.RabiFlopping_line_selection, 
                                detuning=self.get_variable_parameter("RabiFlopping_detuning"),
                                sideband=self.RabiFlopping_selection_sideband,
                                order=self.RabiFlopping_order, 
                                dds=self.RabiFlopping_channel_729
                            )

        # self.composite.duration = self.get_variable_parameter("RabiFlopping_duration")
        # self.composite.att_729 = self.get_variable_parameter("RabiFlopping_att_729")
        # self.composite.amp_729 = self.RabiFlopping_amplitude_729
        # self.composite.freq_729 = self.calc_frequency(
        #                         self.RabiFlopping_line_selection, 
        #                         detuning=self.get_variable_parameter("RabiFlopping_detuning"),
        #                         sideband=self.RabiFlopping_selection_sideband,
        #                         order=self.RabiFlopping_order, 
        #                         dds=self.RabiFlopping_channel_729
        #                     )

        # Uncomment this to enable ramping for RabiFlopping sequence
        #if self.rabi.duration > 0:
        #    self.rabi.setup_ramping(self)

        self.rabi.att_729=self.get_variable_parameter("RabiFlopping_att_729")
        #self.stateprep.post_delay=self.get_variable_parameter("StatePreparation_post_delay")

    @kernel
    def RabiFlopping(self):
        self.stateprep.run(self)
        if self.RabiFlopping_noise:
            self.mod397.on()
        if self.RabiFlopping_composite_pi_rotation:
            self.composite.run(self)
        else:    
            #delay(1*ms)
            self.rabi.run(self)
        if self.RabiFlopping_noise:
            self.mod397.off()
        
