from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from artiq.experiment import *

class RabiFlopping(PulseSequence):
    # accessed_params.update : put the parameters you want to show here.
    # We will add state readout mode, doppoler cooling, sideband cooling, aux op....
    # so it will be more like old ways or we can just go to parameters, not a big deal.
    PulseSequence.accessed_params.update(
        {"RabiFlopping.rabi_excitation_frequency",
         "RabiFlopping.rabi_excitation_amplitude",
         "RabiFlopping.rabi_excitation_att",
         "RabiFlopping.rabi_excitation_phase",
         "RabiFlopping.channel_729",
         "RabiFlopping.rabi_excitation_duration",
         "RabiFlopping.line_selection",
         }
    )
    PulseSequence.scan_params.update(
        RabiFlopping=("Rabi",
            [("RabiFlopping.duration", 0*us, 100, 20)])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.rabi = self.add_subsequence(RabiExcitation)

    @kernel
    def RabiFlopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")*us
        opc_line = self.opc.line_selection
        opc_dds = self.opc.channel_729
        rabi_line = self.rabi.line_selection
        rabi_dds = self.rabi.channel_729
        self.opc.freq_729 = self.calc_frequency(opc_line, dds=opc_dds)
        self.rabi.freq_729 = self.calc_frequency(rabi_line, 0., dds=rabi_dds)

        delay(1*ms)

        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.rabi.run(self)
        # how do we specify the readout mode?
