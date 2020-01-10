from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *


class OptimizeOpticalPumping(PulseSequence):
    PulseSequence.accessed_params = {
        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.channel_729",
        "RabiFlopping.line_selection",
        "RabiFlopping.duration",
        "StatePreparation.aux_optical_pumping_enable",
        "OpticalPumpingAux.channel_729",
        "OpticalPumpingAux.line_selection",
        "OpticalPumpingAux.duration",
        "OpticalPumpingAux.amp_729",
        "OpticalPumpingAux.amp_854",
        "OpticalPumpingAux.att_729",
        "OpticalPumpingAux.att_854",
    }

    PulseSequence.scan_params["krun"] = [
        ("Current", ("OpticalPumpingAux.duration", 10*us, 200*us, 20, "us")),
        ("Current", ("OpticalPumpingAux.amp_729", 0., 1., 20)),
        ("Current", ("OpticalPumpingAux.amp_854", 0., 1., 20)),
    ]

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["krun"] = self.set_subsequence_krun
        

    @kernel
    def set_subsequence_krun(self):
        self.rabi.duration = self.RabiFlopping_duration
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            detuning=0.,
            dds=self.RabiFlopping_channel_729
        )
        self.stateprep.op.aux_opc.amplitude_729 = self.get_variable_parameter("OpticalPumpingAux_duration")
        self.stateprep.op.aux_opc.amplitude_854 = self.get_variable_parameter("OpticalPumpingAux_amp_729")
        self.stateprep.op.aux_opc.duration = self.get_variable_parameter("OpticalPumpingAux_amp_854")

    @kernel
    def krun(self):
        self.stateprep.run(self)
        self.rabi.run(self)
    