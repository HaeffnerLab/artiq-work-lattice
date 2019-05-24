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
from artiq.experiment import *


class CalibSideband(PulseSequence):
    PulseSequence.accessed_params.update(
        {"CalibrationScans.calibration_channel_729",
         "CalibrationScans.sideband_calibration_amp",
         "CalibrationScans.sideband_calibration_att",
         "CalibrationScans.selection_sideband",
         "Spectrum.manual_excitation_time",
         "CalibrationScans.sideband_calibration_line",
         "Display.relative_frequencies",
         "CalibrationScans.readout_mode"}
    )

    PulseSequence.scan_params.update(
        CalibSideband=("Spectrum",
                [("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz")])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.kernel_invariants.update({"sideband"})
        selection = self.p.CalibrationScans.selection_sideband
        self.sideband = self.p["TrapFrequencies"][selection]

    @kernel
    def CalibSideband(self):
        delta = self.get_variable_parameter("Spectrum_sideband_detuning")
        opc_line = self.opc.line_selection
        opc_dds = self.opc.channel_729
        rabi_line = self.CalibrationScans_sideband_calibration_line
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.CalibrationScans_sideband_calibration_amp
        self.rabi.att_729 = self.CalibrationScans_sideband_calibration_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.opc.freq_729 = self.calc_frequency(opc_line, dds=opc_dds)
        self.rabi.freq_729 = self.calc_frequency(rabi_line, delta, sideband=self.sideband, order=1, 
            dds=rabi_dds, bound_param="Spectrum_sideband_detuning")

        # while True:
        #     try:
        #         self.repump854.run(self)
        #         break
        #     except RTIOUnderflow:
        #         delay(25*us)

        self.repump854.run(self)
        
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.rabi.run(self)

    def run_finally(self):
        x = self.data.CalibSideband.x
        y = self.data.CalibSideband.y
        global_max = x[np.argmax(y)]
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
            self.line2_peak = popt[1]
        except:
            raise FitError
        if self.p.Display.relative_frequencies:
            peak = popt[1]
        else:
            line = self.carrier_values[self.carrier_dict[self.p.CalibrationScans.sideband_calibration_line]]
            peak = popt[1] - line

        cxn = labrad.connect()
        p = cxn.parametervault
        p.set_parameter(
                ["TrapFrequencies", self.p.CalibrationScans.selection_sideband, peak]
            )
        cxn.disconnect() 

def gaussian(x, A, x0, sigma):
    return A * np.exp((-(x - x0)**2) / (2*sigma**2))
