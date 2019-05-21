from artiq.pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from artiq.experiment import *


class CalibAllLines(PulseSequence):
    PulseSequence.accessed_params.update(
        {"CalibrationScans.calibration_channel_729",
         "Spectrum.car1_amp",
         "Spectrum.car2_amp",
         "Spectrum.manual_excitation_time",
         "DriftTracker.line_selection_1",
         "DriftTracker.line_selection_2",
         "Display.relative_frequencies",
         "CalibrationScans.readout_mode"}
    )

    PulseSequence.scan_params.update(
        CalibLine1=("CalibLine1",
                [("Spectrum.carrier_detuning", -5*kHz, 5*kHz, 15)]),
        CalibLine2=("CalibLine2",
                [("Spectrum.carrier_detuning", -5*kHz, 5*kHz, 15)])
    )

    def __init__(self):
        self.run_after["CalibLine1"] = self.analyze_calibline1
        self.run_after["CalibLine2"] = self.analyze_calibline2

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.rabi = self.add_subsequence(RabiExcitation)

    @kernel
    def CalibLine1(self):
        delta = self.get_variable_parameter("Spectrum_carrier_detuning")
        opc_line = self.opc.line_selection
        opc_dds = self.opc.channel_729
        rabi_line = self.DriftTracker_line_selection_1
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.Spectrum_car1_amp
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.opc.freq_729 = self.calc_frequency(opc_line, dds=opc_dds)
        self.rabi.freq_729 = self.calc_frequency(rabi_line, delta, dds=rabi_dds,
                bound_param="Spectrum_carrier_detuning")

        delay(1*ms)

        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.rabi.run(self)
    
    def analyze_calibline1(self):
        print("DATA: ", self.data.CalibLine1.x)

    @kernel
    def CalibLine2(self):
        delta = self.get_variable_parameter("Spectrum_carrier_detuning")
        opc_line = self.opc.line_selection
        opc_dds = self.opc.channel_729
        rabi_line = self.DriftTracker_line_selection_2
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.Spectrum_car2_amp
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.opc.freq_729 = self.calc_frequency(opc_line, dds=opc_dds)
        self.rabi.freq_729 = self.calc_frequency(rabi_line, delta, dds=rabi_dds,
                bound_param="Spectrum_carrier_detuning")

        delay(1*ms)

        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.rabi.run(self)

    def analyze_calibline2(self):
        print("DATA: ", self.data.CalibLine2.x)

    # def run_finally(self):
    #     print("DATA: ", self.data.CalibLine1.x)