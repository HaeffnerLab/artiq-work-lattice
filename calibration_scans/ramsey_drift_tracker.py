import numpy as np
import labrad
import artiq.dashboard.drift_tracker.client_config as cl
from labrad.units import WithUnit as U 
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class RamseyDriftTracker(PulseSequence):
    PulseSequence.accessed_params = {
        "DriftTrackerRamsey.line_1_amplitude",
        "DriftTrackerRamsey.line_1_pi_time",
        "DriftTrackerRamsey.line_1_att",
        "DriftTrackerRamsey.line_2_amplitude",
        "DriftTrackerRamsey.line_2_pi_time",
        "DriftTrackerRamsey.line_2_att",
        "DriftTrackerRamsey.line_selection_1",
        "DriftTrackerRamsey.line_selection_2",
        "DriftTrackerRamsey.gap_time_1",
        "DriftTrackerRamsey.gap_time_2",
        "DriftTrackerRamsey.submit",
        "DriftTrackerRamsey.ion_number",
        "DriftTrackerRamsey.first_run",
        "DriftTrackerRamsey.channel_729",

    }

    PulseSequence.scan_params["TrackLine1"] = ("DriftTrackerRamsey1",
            [("DriftTrackerRamsey.phase_1", 90., 270., 2, "deg")])
    PulseSequence.scan_params["TrackLine2"] = ("DriftTrackerRamsey2",
            [("DriftTrackerRamsey.phase_2", 90., 270., 2, "deg")])

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["TrackLine1"] = self.set_subsequence_trackline1
        self.set_subsequence["TrackLine2"] = self.set_subsequence_trackline2
        self.run_after["TrackLine1"] = self.analyze_trackline1
        self.run_after["TrackLine2"] = self.analyze_trackline2

    @kernel
    def set_subsequence_trackline1(self):
        self.rabi.duration = self.DriftTrackerRamsey_line_1_pi_time / 2
        self.rabi.amp_729 = self.DriftTrackerRamsey_line_1_amplitude
        self.rabi.att_729 = self.DriftTrackerRamsey_line_1_att
        self.rabi.freq_729 = self.calc_frequency(
                    self.DriftTrackerRamsey_line_selection_1, 
                    dds=self.DriftTrackerRamsey_Ramsey_channel_729
                )
        self.wait_time = self.DriftTrackerRamsey_gap_time_1

    @kernel
    def TrackLine1(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.phase_729 = 0.
        self.rabi.run(self)
        delay(self.wait_time)
        self.rabi.phase_729 = self.get_variable_parameter("DriftTrackerRamsey_phase_1") * 0.01745329251
        self.rabi.run(self)
    
    @kernel
    def set_subsequence_trackline2(self):
        self.rabi.duration = self.DriftTrackerRamsey_line_2_pi_time / 2
        self.rabi.amp_729 = self.DriftTrackerRamsey_line_2_amplitude
        self.rabi.att_729 = self.DriftTrackerRamsey_line_2_att
        self.rabi.freq_729 = self.calc_frequency(
                    self.DriftTrackerRamsey_line_selection_2, 
                    dds=self.DriftTrackerRamsey_Ramsey_channel_729
                )
        self.wait_time = self.DriftTrackerRamsey_gap_time_2
        self.line_2_phase = self.get_variable_parameter("DriftTrackerRamsey_phase_2")

    @kernel
    def TrackLine1(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.phase_729 = 0.
        self.rabi.run(self)
        delay(self.wait_time)
        self.rabi.phase_729 = self.get_variable_parameter("DriftTrackerRamsey_phase_2") * 0.01745329251
        self.rabi.run(self)



       