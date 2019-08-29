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
        "StatePreparation.number_of_cycles",
        "StatePreparation.pulsed_854_duration",
        "StatePreparation.pi_time",
        "StatePreparation.channel_729",
        "StatePreparation.pulsed_amplitude",
        "StatePreparation.pulsed_att",
        "OpticalPumping.optical_pumping_frequency_854",
        "OpticalPumping.optical_pumping_amplitude_854",
        "OpticalPumping.optical_pumping_att_854",
        "OpticalPumping.line_selection",
        "OpticalPumping.amplitude_729",
        "OpticalPumping.amplitude_729",
        "OpticalPumping.att_729",
        "OpticalPumpingContinuous.optical_pumping_continuous_duration",
    #    "DopplerCooling.doppler_cooling_amplitude_866"
    }

    PulseSequence.scan_params["krun"] = [
        ("Current", ("OpticalPumping.optical_pumping_frequency_854", -2*MHz, 2*MHz, 20, "MHz")),
        ("Current", ("OpticalPumping.optical_pumping_amplitude_854", 0., 1., 20)),
        #("Current", ("DopplerCooling.doppler_cooling_amplitude_866", 0., 1., 20)),
        ("Current", ("StatePreparation.number_of_cycles", 0, 20, 20)),
        ("Current", ("StatePreparation.pulsed_amplitude", 0., 1., 20)),
        ("Current", ("StatePreparation.pulsed_854_duration", 1*us, 100*us, 20, "us")),
        ("Current", ("OpticalPumping.amplitude_729", 0., 1., 20)),
        ("Current", ("OpticalPumpingContinuous.optical_pumping_continuous_duration", 0, 100*us, 20, "us"))        
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
        self.stateprep.op.opp.number_of_cycles = self.get_variable_parameter("StatePreparation_number_of_cycles")
        self.stateprep.op.opp.frequency_854 = self.get_variable_parameter("OpticalPumping_optical_pumping_frequency_854")
        self.stateprep.op.opp.amplitude_854 = self.get_variable_parameter("OpticalPumping_optical_pumping_amplitude_854")
        self.stateprep.op.opp.amplitude_729 = self.get_variable_parameter("StatePreparation_pulsed_amplitude")
        self.stateprep.op.opp.duration_854 = self.get_variable_parameter("StatePreparation_pulsed_854_duration")
        #self.stateprep.op.opp.amplitude_866 = self.get_variable_parameter("DopplerCooling_doppler_cooling_amplitude_866")
        self.stateprep.op.opc.amplitude_729 = self.get_variable_parameter("OpticalPumping_amplitude_729")
        self.stateprep.op.opc.duration = self.get_variable_parameter("OpticalPumpingContinuous_optical_pumping_continuous_duration")

    @kernel
    def krun(self):
        self.stateprep.run(self)
        self.rabi.run(self)
    