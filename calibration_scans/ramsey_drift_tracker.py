import numpy as np
import labrad
import artiq.dashboard.drift_tracker.client_config as cl
import logging
from labrad.units import WithUnit as U 
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


logger = logging.getLogger(__name__)


class RamseyDriftTracker(PulseSequence):
    PulseSequence.accessed_params = {
        "DriftTrackerRamsey.line1_amplitude",
        "DriftTrackerRamsey.line_1_pi_time",
        "DriftTrackerRamsey.line_1_att",
        "DriftTrackerRamsey.line_2_amplitude",
        "DriftTrackerRamsey.line_2_pi_time",
        "DriftTrackerRamsey.line_2_att",
        "DriftTracker.line_selection_1",
        "DriftTracker.line_selection_2",
        "DriftTrackerRamsey.gap_time_1",
        "DriftTrackerRamsey.gap_time_2",
        "DriftTrackerRamsey.ion_number",
        "DriftTrackerRamsey.first_run",
        "DriftTrackerRamsey.channel_729",
        "DriftTrackerRamsey.auto_schedule"

    }

    PulseSequence.scan_params["TrackLine1"] = ("DriftTrackerRamsey1",
            [("DriftTrackerRamsey.phase_1", 90., 270., 2, "deg")])
    PulseSequence.scan_params["TrackLine2"] = ("DriftTrackerRamsey2",
            [("DriftTrackerRamsey.phase_2", 90., 270., 2, "deg")])

    def run_initially(self):
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["TrackLine1"] = self.set_subsequence_trackline1
        self.set_subsequence["TrackLine2"] = self.set_subsequence_trackline2
        self.run_after["TrackLine1"] = self.analyze_trackline1
        self.run_after["TrackLine2"] = self.analyze_trackline2
        self.max_gap = 500*us
        self.min_gap = 25*us
        self.expid = {
            "arguments": {
                    "CalibLine1-Scan_Selection": "Spectrum.carrier_detuning",
                    "CalibLine2-Scan_Selection": "Spectrum.carrier_detuning"
                },
            "class_name": "CalibAllLines",
            "file": "calibration_scans/calib_all_lines.py",
            "priority": 100,
            "log_level": 30,
            "repo_rev": None
        }
        if self.p.DriftTrackerRamsey.first_run:
            cxn = labrad.connect()
            cxn.parametervault.set_parameter("DriftTrackerRamsey", "first_run", False)
            cxn.disconnect()
            self.scheduler.submit("main", self.expid, priority=100)

    @kernel
    def set_subsequence_trackline1(self):
        self.rabi.duration = self.DriftTrackerRamsey_line_1_pi_time / 2
        self.rabi.amp_729 = self.DriftTrackerRamsey_line1_amplitude
        self.rabi.att_729 = self.DriftTrackerRamsey_line_1_att
        self.rabi.freq_729 = self.calc_frequency(
                    self.DriftTracker_line_selection_1, 
                    dds=self.DriftTrackerRamsey_channel_729
                )

    @kernel
    def TrackLine1(self):
        delay(1*ms)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.phase_729 = 0.
        self.rabi.run(self)
        delay(self.DriftTrackerRamsey_gap_time_1)
        self.rabi.phase_729 = self.get_variable_parameter("DriftTrackerRamsey_phase_1")
        self.rabi.run(self)

    def analyze_trackline1(self):
        cxn = labrad.connect()
        pv = cxn.parametervault
        ramsey_time = self.p.DriftTrackerRamsey.gap_time_1
        duration = self.p.DriftTrackerRamsey.line_1_pi_time
        if self.StateReadout_readout_mode == "pmt":
            p1, p2 = self.data.TrackLine1.y[-1]
        else:
            p1, p2 = self.data.TrackLine1.y[self.p.DriftTrackerRamsey.ion_number]
        if p1 == p2 == 0 or p1 == p2 == 1:
            logger.error("Abnormal populations, something isn't right.")
            raise TerminationRequested

        pstar =  abs((p1 - p2) / (p1 + p2))  
        if pstar > .8:
            new_ramsey_time = ramsey_time / 2
            if new_ramsey_time >= self.min_gap:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_1", U(new_ramsey_time, "s"))
                logger.info("Halving gap_time_1.")
            if self.p.DriftTrackerRamsey.auto_schedule:
                pv.set_parameter("DriftTrackerRamsey", "auto_schedule", False)
                self.scheduler.submit("main", self.expid, priority=100)
                raise TerminationRequested
        elif pstar > .55:
            new_ramsey_time = ramsey_time * 2/3
            if new_ramsey_time >= self.min_gap:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_1", U(new_ramsey_time, "s"))
                logger.info("Reducing gap_time_1 by 1/3.")
            else:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_1", U(self.min_gap, "s"))
                logger.info("Reducing gap_time_1 to minimum, as specified.")
        elif pstar < .15:
            new_ramsey_time = ramsey_time * 3/2
            if new_ramsey_time < self.max_gap:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_1", U(new_ramsey_time, "s"))
                logger.info("Increasing gap_time_1 by 3/2.")
            else:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_1", U(self.max_gap, "s"))
                logger.info("Increasing gap_time_1 to maximum, as specified.")

        detuning = np.arcsin(pstar) / (2 * np.pi * ramsey_time + 4 * duration) / 1000
        self.detuning_1_global = detuning
        cxn.disconnect()
    
    @kernel
    def set_subsequence_trackline2(self):
        self.rabi.duration = self.DriftTrackerRamsey_line_2_pi_time / 2
        self.rabi.amp_729 = self.DriftTrackerRamsey_line_2_amplitude
        self.rabi.att_729 = self.DriftTrackerRamsey_line_2_att
        self.rabi.freq_729 = self.calc_frequency(
                    self.DriftTracker_line_selection_2, 
                    dds=self.DriftTrackerRamsey_channel_729
                )

    @kernel
    def TrackLine2(self):
        delay(1*ms)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.phase_729 = 0.
        self.rabi.run(self)
        delay(self.DriftTrackerRamsey_gap_time_2)
        self.rabi.phase_729 = self.get_variable_parameter("DriftTrackerRamsey_phase_2")
        self.rabi.run(self)

    def analyze_trackline2(self):
        cxn = labrad.connect()
        pv = cxn.parametervault
        ramsey_time = self.p.DriftTrackerRamsey.gap_time_2
        duration = self.p.DriftTrackerRamsey.line_2_pi_time
        if self.StateReadout_readout_mode == "pmt":
            p1, p2 = self.data.TrackLine2.y[-1]
        else:
            p1, p2 = self.data.TrackLine2.y[self.p.DriftTrackerRamsey.ion_number]
        if p1 == p2 == 0 or p1 == p2 == 1:
            logger.error("Abnormal populations, something isn't right.")
            raise TerminationRequested

        pstar = abs((p1 - p2) / (p1 + p2))  #
        if pstar > .8:
            new_ramsey_time = ramsey_time / 2
            if new_ramsey_time >= self.min_gap:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_2", U(new_ramsey_time, "s"))
                logger.info("Halving gap_time_2.")
            if self.p.DriftTrackerRamsey.auto_schedule:
                pv.set_parameter("DriftTrackerRamsey", "auto_schedule", False)
                self.scheduler.submit("main", self.expid, priority=100)
                raise TerminationRequested
        elif pstar > .55:
            new_ramsey_time = ramsey_time * 2/3
            if new_ramsey_time >= self.min_gap:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_2", U(new_ramsey_time, "s"))
                logger.info("Reducing gap_time_2 by 1/3.")
            else:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_2", U(self.min_gap, "s"))
                logger.info("Reducing gap_time_2 to minimum, as specified.")
        elif pstar < .15:
            new_ramsey_time = ramsey_time * 3/2
            if new_ramsey_time < self.max_gap:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_2", U(new_ramsey_time, "s"))
                logger.info("Increasing gap_time_2 by 3/2.")
            else:
                pv.set_parameter("DriftTrackerRamsey", "gap_time_2", U(self.max_gap, "s"))
                logger.info("Increasing gap_time_2 to maximum, as specified.")

        detuning = np.arcsin(pstar) / (2 * np.pi * ramsey_time + 4 * duration) / 1000
        self.detuning_2_global = detuning
        cxn.disconnect()

    def run_finally(self):
        
        line1 = self.p.DriftTracker.line_selection_1
        line2 = self.p.DriftTracker.line_selection_2

        old_carr1 = self.carrier_values[self.carrier_dict[line1]] * 1e-6
        old_carr2 = self.carrier_values[self.carrier_dict[line2]] * 1e-6

        carr1 = self.detuning_1_global * 1e-6 + old_carr1
        carr2 = self.detuning_2_global * 1e-6 + old_carr2

        submission = [(line1, U(carr1, "MHz")), (line2, U(carr2, "MHz"))]

        try:
            global_cxn = labrad.connect(cl.global_address, password=cl.global_password,
                                        tls_mode="off")
            global_cxn.sd_tracker_global.set_measurements(submission, cl.client_name)
        except:
            logger.error("Failed to connect to global drift tracker.", exc_info=True)
            return
        global_cxn.disconnect()



       