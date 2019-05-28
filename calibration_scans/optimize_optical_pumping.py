from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class OptimizeOpticalPumping(PulseSequence):
    PulseSequence.accessed_params.update(
        {"RabiFlopping.amplitude_729",
         "RabiFlopping.att_729",
         "RabiFlopping.channel_729",
         "RabiFlopping.line_selection",
         "RabiFlopping.duration",
         "StatePreparation.sideband_cooling_enable",
         "StatePreparation.number_of_cycles",
         "StatePreparation.pulsed_854_duration",
         "StatePreparation.pi_time",
         "StatePreparation.channel_729",
         "StatePreparation.pulsed_amplitude",
         "StatePreparation.pulsed_att",
         "OpticalPumping.optical_pumping_frequency_854",
         "OpticalPumping.optical_pumping_amplitude_854",
         "OpticalPumping.optical_pumping_att_854",
         "OpticalPumping.line_selection"}
    )

    PulseSequence.scan_params["krun"] = ("Current",
        [("OpticalPumping.optical_pumping_frequency_854", -2*MHz, 2*MHz, 20, "MHz"),
         ("OpticalPumping.optical_pumping_amplitude_854", 0., 1., 20),
         ("StatePreparation.number_of_cycles", 0, 20, 20),
         ("StatePreparation.pulsed_amplitude", 0., 1., 20),
         ("StatePreparation.pulsed_854_duration", 1*us, 100*us, 20, "us")        
        ]
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
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
        self.opc.number_of_cycles = self.get_variable_parameter("StatePreparation_number_of_cycles")
        self.opc.frequency_854 = self.get_variable_parameter("OpticalPumping_optical_pumping_frequency_854")
        self.opc.amplitude_854 = self.get_variable_parameter("OpticalPumping_optical_pumping_amplitude_854")
        self.opc.amplitude_729 = self.get_variable_parameter("StatePreparation_pulsed_amplitude")
        self.opc.duration_854 = self.get_variable_parameter("StatePreparation_pulsed_854_duration")

        print(self.opc.number_of_cycles)
        print(self.opc.frequency_854)
        print(self.opc.amplitude_854)#
        print(self.opc.amplitude_729)
        print(self.oopc.duration_854)

    @kernel
    def krun(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
        self.rabi.run(self)
    