from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *
import numpy as np


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
        "RabiFlopping.noise"
    }

    PulseSequence.scan_params = dict(
        RabiFlopping=[
            ("Rabi", ("RabiFlopping.duration", 0., 100e-6, 20, "us")),
            ("Rabi", ("RabiFlopping.att_729", 0*dB, 32*dB, 1*dB, "dB"))
            #("Rabi", ("StatePreparation.post_delay", 0., 10*ms, 20, "ms"))
        ])

    def run_initially(self):
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["RabiFlopping"] = self.set_subsequence_rabiflopping

    @kernel
    def set_subsequence_rabiflopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        #self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            detuning=self.RabiFlopping_detuning,
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )

    @kernel
    def RabiFlopping(self):
        self.rabi.phase_ref_time = now_mu()
        self.rabi.phase_729 = 10.
        self.rabi.run(self)
       

