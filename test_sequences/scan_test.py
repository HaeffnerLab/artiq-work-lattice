from artiq.language import core, scan
from artiq.experiment import *
from easydict import EasyDict as edict
# from subsequences.state_readout
import time
import labrad
import numpy as np


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")
        self.pmt = self.get_device("pmt")
        self.setattr_argument("scan", scan.Scannable(default=scan.RangeScan(0, 10, 10)))

    def prepare(self):
        cxn = labrad.connect()
        p = cxn.parametervault
        collections = p.get_collections()
        pmt_count_name = "pmt_counts_" + str(int(time.time()))
        self.set_dataset(pmt_count_name, [], broadcast=True)
        # self.pmt = self.get_dataset(pmt_count_name)
        self.pmt_count_name = pmt_count_name
        
        # Takes over a second to do this. We should move away from using labrad units
        # in registry. Really we should rewrite parameter vault as 
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


    def run(self):
        self.core.reset()
        for _ in scan.NoScan(0, int(self.p.StateReadout.repeat_each_measurement)):
            try:
                self.scheduler.pause()
                self.kernel_run()
                self.state_readout()
            except core.TerminationRequested:
                break

    @kernel
    def kernel_run(self):
        self.core.break_realtime()
        self.cpld.init()
        self.dds_397.init()
        self.dds_866.init()
        self.dds_397.set(10*MHz)
        self.dds_866.set(10*MHz)
        self.dds_397.set_att(22*dB)
        self.dds_866.set_att(15*dB)
        with parallel:
            self.dds_397.sw.pulse(1*s)
            self.dds_866.sw.pulse(1*s)
        delay(1*s)
        self.dds_397.set(100*MHz)
        self.dds_866.set(100*MHz)
        with parallel:
            self.dds_397.sw.pulse(1*s)
            self.dds_866.sw.pulse(1*s)
        delay(1*s)
        

    @kernel
    def state_readout(self):
        with parallel:
            t_count = self.pmt.gate_rising(100*ms)
            pmt_counts = self.pmt.count(t_count)
        self.append_to_dataset(self.pmt_count_name, pmt_counts)
