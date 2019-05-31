from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class MotionalAnalysisSpectrum(PulseSequence):
    PulseSequence.accessed_params.update(
        {"MotionAnalysis.pulse_width_397",
         "MotionAnalysis.amplitude_397",
         "MotionAnalysis.sideband_selection",
         "MotionAnalysis.att_397",
         "RabiFlopping.duration",
         "RabiFlopping.amplitude_729",
         "RabiFlopping.line_selection",
         "RabiFlopping.selection_sideband",
         "RabiFlopping.att_729",
         "RabiFlopping.order",
         "RabiFlopping.channel_729",
         "StatePreparation.sideband_cooling_enable",
         "DopplerCooling.doppler_cooling_frequency_397",
         "DopplerCooling.doppler_cooling_frequency_866",
         "DopplerCooling.doppler_cooling_amplitude_866",
         "DopplerCooling.doppler_cooling_att_866"}
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
        self.set_subsequence["MotionalSpectrum"] = self.set_subsequence_motionalspectrum
        self.sideband = self.p.TrapFrequencies[self.p.RabiFlopping.selection_sideband]
        self.duration = 0.
        self.detuning = 0.
        self.amp_397 = 0.
        self.n = 1

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
        self.detuning = self.sideband + self.get_variable_parameter("MotionAnalysis_detuning")
        self.n = int(self.detuning * self.MotionAnalysis_pulse_width_397)
        # self.n = 50
        self.duration = .5 / self.detuning
        # self.duration = 10*ns
        self.amp_397 = self.get_variable_parameter("MotionAnalysis_amplitude_397")

    @kernel
    def MotionalSpectrum(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)

        self.dds_397.set(self.DopplerCooling_doppler_cooling_frequency_397,
                         amplitude=self.amp_397)
        self.dds_397.set_att(self.MotionAnalysis_att_397)
        self.dds_866.set(self.DopplerCooling_doppler_cooling_frequency_866,
                         amplitude=self.DopplerCooling_doppler_cooling_amplitude_866)
        self.dds_866.set_att(self.DopplerCooling_doppler_cooling_att_866)
        self.dds_866.sw.on()
        for i in range(self.n):
            self.dds_397.sw.pulse(self.duration)
            delay(100*us)#self.duration)
        self.opc.run(self)

        self.rabi.run(self)
