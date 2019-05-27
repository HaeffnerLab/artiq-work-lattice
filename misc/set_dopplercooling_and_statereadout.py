import labrad
import numpy as np
from artiq.experiment import *
from artiq.language.core import TerminationRequested
from labrad.units import WithUnit as U


class set_dopplercooling_and_statereadout(EnvExperiment):

    def build(self):
        self.cxn = labrad.connect()
        self.p = self.cxn.parametervault
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.pmt = self.get_device("pmt")

    def prepare(self):
        self.readout_duration = 15*ms
        self.scan_length = 40
        self.set_dataset("pmt_counts", [], broadcast=True)
        self.set_dataset("collection_duration", [self.readout_duration])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        self.freq_866 = self.p.get_parameter("DopplerCooling", "doppler_cooling_frequency_866")["MHz"]
        self.amp_866 = self.p.get_parameter("DopplerCooling", "doppler_cooling_amplitude_866")[""]
        self.att_866 = self.p.get_parameter("DopplerCooling", "doppler_cooling_att_866")["dBm"]
        self.att_397 = self.p.get_parameter("DopplerCooling", "doppler_cooling_att_397")["dBm"]
        self.background_level = 0
        self.cpld_list = [self.get_device("urukul{}_cpld".format(i)) for i in range(3)]
        self.dds_names = list()
        self.dds_device_list = list()
        for key, val in self.get_device_db().items():
            if isinstance(val, dict) and "class" in val:
                if val["class"] == "AD9910" or val["class"] == "AD9912":
                    setattr(self, "dds_" + key, self.get_device(key))
                    self.dds_device_list.append(getattr(self, "dds_" + key))
                    try:
                        self.dds_names.append(key)
                    except KeyError:
                        continue
        # Grab cw parameters:
        # NOTE: Because parameters are grabbed in prepare stage,
        # loaded dds cw parameters may not be the most current.
        self.dds_list = list()
        self.freq_list = list()
        self.amp_list = list()
        self.att_list = list()
        self.state_list = list()
        dds_cw_parameters = dict()
        names = self.p.get_parameter_names("dds_cw_parameters")
        for name in names:
            param = self.p.get_parameter("dds_cw_parameters", name)
            dds_cw_parameters[name] = param
        for key, settings in dds_cw_parameters.items():
            self.dds_list.append(getattr(self, "dds_" + key))
            self.freq_list.append(float(settings[1][0]) * 1e6)
            self.amp_list.append(float(settings[1][1]))
            self.att_list.append(float(settings[1][3]))
            self.state_list.append(bool(float(settings[1][2])))
        self.completed = False
        self.dataset_length = dict()

    def run(self):
        self.initialize(self.freq_866, self.amp_866, self.att_866, self.att_397)
        
        freq_list = np.linspace(65*MHz, 85*MHz, self.scan_length)
        self.scan_freq_list = freq_list
        self.freq_data = []
        for i, freq in enumerate(freq_list):
            self.krun_freq(freq)
            self.freq_data.append(self.get_dataset("pmt_counts")[-1])
        self.set_dc_freq()

        # self.recrystallize()

        amp_list = np.linspace(.25, .99, self.scan_length)
        self.scan_amp_list = amp_list
        self.amp_data = []
        for i, amp in enumerate(amp_list):
            self.krun_amp(self.dc_freq, amp)
            self.amp_data.append(self.get_dataset("pmt_counts")[-1])
        self.set_dc_amp()

        self.completed = True
        self.reset_cw_settings()

    @kernel
    def initialize(self, freq_866, amp_866, att_866, att_397):
        self.turn_off_all()
        self.core.reset()
        t_count = self.pmt.gate_rising(self.readout_duration)
        self.background_level = self.pmt.count(t_count)
        self.core.break_realtime()
        self.dds_866.set(freq_866*MHz, amplitude=amp_866)
        self.dds_866.set_att(att_866*dB)
        self.dds_866.sw.on()
        self.dds_397.set(65*MHz, amplitude=0.2)
        self.dds_397.set_att(att_397*dB)
        self.dds_397.sw.on()

    @kernel
    def turn_off_all(self):
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        for device in self.dds_device_list:
            device.init()
            device.sw.off()

    @kernel
    def reset_cw_settings(self):
        # Return the CW settings to what they were when prepare stage was run
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        self.core.break_realtime()
        for i in range(len(self.dds_list)):
            try:
                self.dds_list[i].init()
            except RTIOUnderflow:
                self.core.break_realtime()
                self.dds_list[i].init()
            self.dds_list[i].set(self.freq_list[i], amplitude=self.amp_list[i])
            self.dds_list[i].set_att(self.att_list[i]*dB)
            if self.state_list[i]:
                self.dds_list[i].sw.on()
            else:
                self.dds_list[i].sw.off()
    
    @kernel
    def krun_freq(self, freq):
        self.core.break_realtime()
        self.dds_397.set(freq)
        self.core.break_realtime()
        t_count = self.pmt.gate_rising(self.readout_duration)
        pmt_count = self.pmt.count(t_count)
        self.append("pmt_counts", pmt_count)
        self.append("pmt_counts_866_off", -1)

    @kernel
    def krun_amp(self, freq, amp):
        self.core.break_realtime()
        self.dds_397.set(freq, amplitude=amp)
        self.core.break_realtime()
        delay(3*ms) # time for amplitude to be increased
        t_count = self.pmt.gate_rising(self.readout_duration)
        pmt_count = self.pmt.count(t_count)
        self.append("pmt_counts", pmt_count)
        self.append("pmt_counts_866_off", -1)

    @kernel
    def recrystallize(self):
        self.core.break_realtime()
        self.dds_397.set(70*MHz, amplitude=1.0)
        delay(1*s)

    def append(self, dataset_name, data_to_append):
        if not dataset_name in self.dataset_length.keys():
            self.dataset_length[dataset_name] = 0

        if self.dataset_length[dataset_name] % 1000 == 0:
            self.set_dataset(dataset_name, [], broadcast=True)

        self.append_to_dataset(dataset_name, data_to_append)
        self.dataset_length[dataset_name] += 1

    def set_dc_freq(self):
        max_counts = max(self.freq_data)
        max_counts_index = np.abs(self.freq_data - max_counts).argmin()
        self.peak_freq_397 = self.scan_freq_list[max_counts_index]
        half_max_counts = max_counts / 2 + self.background_level
        half_max_counts_index = np.abs(self.freq_data - half_max_counts).argmin()
        dc_freq = self.scan_freq_list[half_max_counts_index] * 1e-6
        self.dc_freq = dc_freq * 1e6
        self.p.set_parameter("DopplerCooling", "doppler_cooling_frequency_397", U(dc_freq, "MHz"))

    def set_dc_amp(self):
        max_counts = max(self.amp_data)
        max_counts_index = np.abs(self.amp_data - max_counts).argmin()
        self.peak_amp_397 = self.scan_amp_list[max_counts_index]
        third_max_counts = max_counts / 3 + self.background_level
        third_max_counts_index = np.abs(self.amp_data - third_max_counts).argmin()
        dc_amp = self.scan_amp_list[third_max_counts_index]
        self.p.set_parameter("DopplerCooling", "doppler_cooling_amplitude_397", dc_amp)

    def analyze(self):
        if self.completed:
            self.p.set_parameter("StateReadout", "amplitude_397", self.peak_amp_397)
            freq = (self.peak_freq_397 - 5*MHz) * 1e-6
            self.p.set_parameter("StateReadout", "frequency_397", U(freq, "MHz"))
            self.p.set_parameter("StateReadout", "att_397", U(self.att_397, "dBm"))
        self.cxn.disconnect()