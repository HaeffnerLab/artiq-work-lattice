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
        {"RabiFlopping.line_selection",
         "RabiFlopping.amplitude_729",
         "RabiFlopping.att_729",
         "RabiFlopping.channel_729",
         "RabiFlopping.duration",
         }
    )
    PulseSequence.scan_params.update(
        RabiFlopping=("Rabi",
            [("RabiFlopping.duration", 0*us, 100*us, 20*us, "us")])#
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.rabi = self.add_subsequence(RabiExcitation)

    @kernel
    def RabiFlopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        opc_line = self.opc.line_selection
        opc_dds = self.opc.channel_729
        self.opc.freq_729 = self.calc_frequency(opc_line, dds=opc_dds)
        self.rabi.freq_729 = self.calc_frequency(self.RabiFlopping_line_selection, 0., 
                dds=self.RabiFlopping_channel_729)

        delay(1*ms)

        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.rabi.run(self)
        # how do we specify the readout mode?
