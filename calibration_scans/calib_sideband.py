import numpy as np
import labrad
import artiq.dashboard.drift_tracker.client_config as cl
from labrad.units import WithUnit as U 
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class CalibSideband(PulseSequence):
    PulseSequence.accessed_params = {
        "CalibrationScans.calibration_channel_729",
        "CalibrationScans.sideband_calibration_amp",
        "CalibrationScans.sideband_calibration_att",
        "CalibrationScans.selection_sideband",
        "CalibrationScans.order",
        "Spectrum.manual_excitation_time",
        "CalibrationScans.sideband_calibration_line",
        "Display.relative_frequencies",
        "CalibrationScans.readout_mode",
        "StatePreparation.sideband_cooling_enable"
    }

    PulseSequence.scan_params.update(
        CalibSideband=("Spectrum",
            [("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz")])
    )

    def run_initially(self):
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.kernel_invariants.update({"sideband"})
        self.sideband = self.p.CalibrationScans.selection_sideband
        self.set_subsequence["CalibSideband"] = self.set_subsequence_calibsideband
        rt = self.rcg_tabs
        if self.p.CalibrationScans.order < 0:
            rt["CalibSideband"] = "CalibRed"
        else:
            rt["CalibSideband"] = "CalibBlue"

    @kernel
    def set_subsequence_calibsideband(self):
        delta = self.get_variable_parameter("Spectrum_sideband_detuning")
        rabi_line = self.CalibrationScans_sideband_calibration_line
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.CalibrationScans_sideband_calibration_amp
        self.rabi.att_729 = self.CalibrationScans_sideband_calibration_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(
                rabi_line, delta, sideband=self.sideband, order=self.CalibrationScans_order, 
                dds=rabi_dds, bound_param="Spectrum_sideband_detuning"
            )
   
    @kernel
    def CalibSideband(self):
        delay(1*ms)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.run(self)

    def run_finally(self):
        x = self.data.CalibSideband.x
        y = self.data.CalibSideband.y[-1]
        print("x: ", x)
        global_max = x[np.argmax(y)]
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
        except:
            raise FitError
        if self.p.Display.relative_frequencies:
            peak = popt[1] + self.p["TrapFrequencies"][self.p.CalibrationScans.selection_sideband]
        else:
            line = self.carrier_values[self.carrier_dict[self.p.CalibrationScans.sideband_calibration_line]]
            peak = popt[1] - (line + self.p["TrapFrequencies"][self.p.CalibrationScans.selection_sideband])

        cxn = labrad.connect()
        p = cxn.parametervault
        p.set_parameter(
            "TrapFrequencies", self.p.CalibrationScans.selection_sideband, U(peak * 1e-6, "MHz")
        )
        cxn.disconnect() 

def gaussian(x, A, x0, sigma):
    return A * np.exp((-(x - x0)**2) / (2*sigma**2))
