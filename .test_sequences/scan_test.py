from artiq.language import scan
from artiq.experiment import *
from easydict import EasyDict as edict
# from subsequences.state_readout
import time
from datetime import datetime
import labrad
import numpy as np
import h5py as h5
import os
import csv
from sipyco.pc_rpc import Client


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.setattr_device("LTriggerIN")
        self.setattr_argument("scan", scan.Scannable(default=scan.RangeScan(0, 1, 100)))
        
        # Load all AD9910 and AD9912 DDS channels specified in device_db:
        for key, val in self.get_device_db().items():
            if isinstance(val, dict) and "class" in val:
                if val["class"] == "AD9910" or val["class"] == "AD9912":
                    setattr(self, "dds_" + key, self.get_device(key))
        self.cpld_list = [self.get_device("urukul{}_cpld".format(i)) for i in range(3)]

    def prepare(self):
        
        # Grab parametervault params:
        cxn = labrad.connect()
        p = cxn.parametervault
        collections = p.get_collections()
        # Takes over 1 second to do this. We should move away from using labrad units
        # in registry. Would be nice if parametervault was not a labrad server.
        D = dict()
        L = locals()
        for collection in collections:
            d = dict()
            names = p.get_parameter_names(collection)
            for name in names:
                try:
                    param = p.get_parameter([collection, name])
                    try:
                        units = param.units
                        if units == "":
                            param = param[units]
                        else:
                            param = param[units] * L[units]
                    except AttributeError:
                        pass
                    except KeyError:
                        if (units == "dBm" or
                            units == "deg" or
                            units == ""):
                            param = param[units]
                    d[name] = param
                except:
                    #broken parameter
                    continue
            D[collection] = d
        self.p = edict(D)
        cxn.disconnect()

        # Grab cw parameters:
        # Because parameters are grabbed in prepare stage, loaded dds cw parameters
        # may not be the most current.
        self.dds_list = list()
        self.freq_list = list()
        self.amp_list = list()
        self.att_list = list()
        self.state_list = list()

        for key, settings in self.p.dds_cw_parameters.items():
            self.dds_list.append(getattr(self, "dds_" + key))
            self.freq_list.append(float(settings[1][0]) * 1e6)
            self.amp_list.append(float(settings[1][1]))
            self.att_list.append(float(settings[1][3]))
            self.state_list.append(bool(float(settings[1][2])))
       
        # Try to make rcg/hist connection
        try:
            self.rcg = Client("::1", 3286, "rcg")
        except:
            self.rcg = None
        try:
            self.pmt_hist = Client("::1", 3287, "pmt_histogram")
        except:
            self.pmt_hist = None

        # Make scan object for repeating the experiment
        N = int(self.p.StateReadout.repeat_each_measurement)
        self.N = N

        # Create datasets
        M = len(self.scan)

        self.set_dataset("x", np.full(M, np.nan), broadcast=True)
        self.set_dataset("y1", np.full((M, N), np.nan), broadcast=True)
        self.set_dataset("y2", np.full((M, N), np.nan), broadcast=True)
        A = np.full((M, N), np.nan)
        for x in np.nditer(A, op_flags=["readwrite"]):
            x[...] = np.random.normal(0, .1)
        self.rand = A
        self.setattr_dataset("x")
        self.setattr_dataset("y1")
        self.setattr_dataset("y2")
        self.yfull1 = np.full(M, np.nan)
        self.yfull2 = np.full(M, np.nan)
        self.hist_counts = np.full((M, N), np.nan)
        for row in range(M):
            for col in range(N):
                self.hist_counts[row][col] = np.random.normal(10, 5)

        # Tab For Plotting
        self.RCG_TAB = "Rabi"

        # Setup for saving data
        self.timestamp = None
        self.dir = os.path.join(os.path.expanduser("~"), "data",
                                datetime.now().strftime("%Y-%m-%d"), type(self).__name__)
        os.makedirs(self.dir, exist_ok=True)
        os.chdir(self.dir)

    def run(self):
        if self.p.line_trigger_settings.enabled:
            offset = float(self.p.line_trigger_settings.offset_duration)
            offset = self.core.seconds_to_mu((16 + offset)*ms)
            self.line_trigger(offset)
        else:
            self.core.reset()

        for i, step in enumerate(self.scan):
            for j in range(self.N):
                xval = step
                y1val = np.sin(2*np.pi * xval)**2 + self.rand[i, j]
                y2val = np.cos(2*np.pi * xval)**2 + self.rand[i, j]
                self.record_result("y1", (i, j), y1val)
                self.record_result("y2", (i, j), y2val)
            self.record_result("x", i, xval)
            dp = sum(self.get_dataset("y1")[i]) / self.N
            self.yfull1[i] = dp
            dp1 = sum(self.get_dataset("y2")[i] / self.N)
            self.yfull2[i] = dp1
            self.save_and_send_to_rcg(self.get_dataset("x"), self.yfull1, "yfull1")
            self.save_and_send_to_rcg(self.get_dataset("x"), self.yfull2, "yfull2")
            if (i + 1) % 5 == 0:
                self.save_result("x", self.get_dataset("x")[i - 4:i + 1], xdata=True)
                self.save_result("yfull1", self.yfull1[i - 4:i + 1])
                self.save_result("yfull2", self.yfull2[i - 4:i + 1])
                self.send_to_hist(self.hist_counts[i-5:i].flatten())
            time.sleep(0.5)
        else:
            rem = (i + 1) % 5
            self.save_result("x", self.get_dataset("x")[-rem:], xdata=True)
            self.save_result("yfull1", self.yfull1[-rem:])
            self.save_result("yfull2", self.yfull2[-rem:])

        self.reset_cw_settings(self.dds_list, self.freq_list,
                                self.amp_list, self.state_list, self.att_list)

    @rpc(flags={"async"})
    def save_and_send_to_rcg(self, x, y, name):
        if self.timestamp is None:
            self.timestamp = datetime.now().strftime("%H%M_%S")
            self.filename = self.timestamp + ".h5"
            with h5.File(self.filename, "a") as f:
                datagrp = f.create_group("scan_data")
                datagrp.attrs["plot_show"] = self.RCG_TAB
                f.create_dataset("time", data=[], maxshape=(None,))
                params = f.create_group("parameters")
                for collection in self.p.keys():
                    collectiongrp = params.create_group(collection)
                    for key, val in self.p[collection].items():
                        collectiongrp.create_dataset(key, data=str(val))
            with open("../scan_list", "a+") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow([self.timestamp, type(self).__name__,
                                                  os.path.join(self.dir, self.filename)])
        if self.rcg is None:
            try:
                self.rcg = Client("::1", 3286, "rcg")
            except:
                return
        try:
            self.rcg.plot(x, y, tab_name=self.RCG_TAB,
                          plot_title=self.timestamp + " - " + name, append=True,
                          file_=os.path.join(os.getcwd(), self.filename))
        except:
            return

    @kernel
    def reset_cw_settings(self, dds_list, freq_list, amp_list, 
                          state_list, att_list):
        # Return the CW settings to what they were when prepare
        # stage was run
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        with parallel:
            for i in range(len(dds_list)):
                dds_list[i].init()
                dds_list[i].set(freq_list[i], amplitude=amp_list[i])
                dds_list[i].set_att(att_list[i]*dB)
                if state_list[i]:
                    dds_list[i].sw.on()
                else:
                    dds_list[i].sw.off()
    
    @kernel
    def line_trigger(self, offset):
        # Phase lock to mains
        self.core.reset()
        t_gate = self.LTriggerIN.gate_rising(16*ms)
        trigger_time = self.LTriggerIN.timestamp_mu(t_gate)
        at_mu(trigger_time + offset)

    @rpc(flags={"async"})
    def record_result(self, dataset, idx, val):
        self.mutate_dataset(dataset, idx, val)

    @rpc(flags={"async"})
    def save_result(self, dataset, data, xdata=False):
        with h5.File(self.filename, "a") as f:
            datagrp = f["scan_data"]
            try:
                datagrp[dataset]
            except KeyError:
                data = datagrp.create_dataset(dataset, data=data, maxshape=(None,))
                if xdata:
                    data.attrs["x-axis"] = True
                return
            datagrp[dataset].resize(datagrp[dataset].shape[0] + data.shape[0], axis=0)
            datagrp[dataset][-data.shape[0]:] = data

    @rpc(flags={"async"})
    def send_to_hist(self, data):
        self.pmt_hist.plot(data)

    def analyze(self):
        # Is this necessary?
        try:
            self.rcg.close_rpc()
            self.pmt_hist.close_rpc()
        except:
            pass
