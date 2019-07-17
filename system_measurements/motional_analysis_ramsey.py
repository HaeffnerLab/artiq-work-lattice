import visa
from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.motional_analysis import MotionalAnalysis
from artiq.experiment import *


class MotionalAnalysisRamsey(PulseSequence):
    PulseSequence.accessed_params = {
        "MotionAnalysis.pulse_width_397",
        "MotionAnalysis.amplitude_397",
        "MotionAnalysis.sideband_selection",
        "MotionAnalysis.att_397",
        "MotionAnalysis.ramsey_detuning",
        "RabiFlopping.duration",
        "RabiFlopping.amplitude_729",
        "RabiFlopping.line_selection",
        "RabiFlopping.selection_sideband",
        "RabiFlopping.att_729",
        "RabiFlopping.order",
        "RabiFlopping.channel_729",
        "DopplerCooling.doppler_cooling_frequency_397",
        "DopplerCooling.doppler_cooling_frequency_866",
        "DopplerCooling.doppler_cooling_amplitude_866",
        "DopplerCooling.doppler_cooling_att_866"
    }
    PulseSequence.scan_params["MotionalRamsey"] = [
        ("Ramsey", ("MotionAnalysis.ramsey_time", 0*ms, 10*ms, 40, "ms"))
    ]

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.ma = self.add_subsequence(MotionalAnalysis)
        self.set_subsequence["MotionalRamsey"] = self.set_subsequence_motionalramsey
        self.sideband = self.p.TrapFrequencies[self.p.RabiFlopping.selection_sideband]
        self.agi_connected = False

    @kernel
    def set_subsequence_motionalramsey(self):
        self.ma.pulse_width = self.MotionAnalysis_pulse_width_397
        detuning = self.sideband + self.MotionAnalysis_ramsey_detuning
        self.set_frequency(detuning)
        self.rabi.duration = self.RabiFlopping_duration
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )
        delay(2*ms)

    @kernel
    def MotionalRamsey(self):
        self.stateprep.run(self)
        self.ma.run(self)
        self.stateprep.op.opc.run(self)
        delay(wait_time)
        self.ma.run(self)
        self.stateprep.op.opc.run(self)
        self.rabi.run(self)

    def run_finally(self):
        self.cxn.disconnect()
    
    def set_frequency(self, detuning):
        if not self.agi_connected:
            rm = visa.ResourceManager("@py")
            #self.agi = rm.open_resource(u'USB0::2391::1031::MY44013736::0::INSTR')
            self.agi = rm.open_resource(u'USB0::2391::1031::MY44007101::0::INSTR')
            self.agi.write("SYST:BEEP: STAT OFF")
            self.agi_connected = True
        self.agi.write("APPL:SQU {} HZ, 5.0 VPP".format(detuning))