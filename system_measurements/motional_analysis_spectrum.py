from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from subsequences.motional_analysis import MotionalAnalysis
from artiq.experiment import *


class MotionalAnalysisSpectrum(PulseSequence):
    PulseSequence.accessed_params.update(
        {"MotionAnalysis.pulse_width_397",
         "MotionAnalysis.amplitude_397",
         "MotionAnalysis.sideband_selection",
         "RabiFlopping.duration",
         "RabiFlopping.amplitude_729",
         "RabiFlopping.line_selection",
         "RabiFlopping.selection_sideband",
         "RabiFlopping.att_729",
         "RabiFlopping.order",
         "RabiFlopping.channel_729",
         "StatePreparation.sideband_cooling_enable"}
    )

    PulseSequence.scan_params.update(
        MotionalSpectrum=("Spectrum",
        [("MotionAnalysis.detuning", 0., 50e3, 25, "kHz"),
         ("MotionAnalysis.amplitude_397", 0., 1., 25)])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.motional_analysis = self.add_subsequence(MotionalAnalysis)
        self.set_subsequence["MotionalSpectrum"] = self.set_subsequence_motionalspectrum
        self.sideband = self.p.TrapFrequencies[self.p.RabiFlopping.selection_sideband]

    @kernel
    def set_subsequence_motionalspectrum(self):
        self.rabi.duration = self.RabiFlopping_duration
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )
        self.motional_analysis.amp_397 = self.get_variable_parameter("MotionAnalysis_amplitude_397")
        detuning = self.sideband + self.get_variable_parameter("MotionAnalysis_detuning")
        n = int(detuning * self.MotionAnalysis_pulse_width_397)
        duration = 1 / detuning
        self.record(n, duration)


    @kernel
    def MotionalSpectrum(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.motional_analysis.run(self)
        delay_mu(77580736149080)
        self.opc.run(self)
        self.rabi.run(self)

    @kernel
    def record(self, n, duration):
        with self.core_dma.record("pulses"):
            for i in range(n):
                self.dds_397.sw.pulse(duration)
                delay(duration)