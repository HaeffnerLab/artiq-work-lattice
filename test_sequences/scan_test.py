from artiq.language import core, scan
from artiq.experiment import *
from easydict import EasyDict as edict
# from subsequences.state_readout
import time
import labrad
import numpy as np
from artiq.protocols.pc_rpc import Client


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.setattr_argument("scan", scan.Scannable(default=scan.RangeScan(0, 10, 100)))

    def prepare(self):
        
        # ------------   Grab parametervault params -------------------------------
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

        #------------ try to make rcg connection -----------------------------
        try:
            self.rcg = Client("::1", 3286, "rcg")
        except:
            self.rcg = None

        #------------ make scan object ---------------------------------------
        N = int(self.p.StateReadout.repeat_each_measurement)
        self.N = N
        self.repeat = scan.NoScan(0, N)

        #------------- Create datasets ----------------------------------------
        M = len(self.scan)
        self.setattr_dataset("x", np.full(M, np.nan))
        self.setattr_dataset("y1", np.full((M, N), np.nan))
        self.setattr_dataset("y2", np.full((M, N), np.nan))
        self.setattr_dataset("yfull", np.full(M, np.nan))

    def run(self):
        for i, step in enumerate(self.scan):
            for j, _ in enumerate(self.repeat):
                xval = step
                y1val = np.random.binomial(1, np.sin(2*np.pi * xval))
                y2val = np.random.binomial(1, np.cos(2*np.pi * xval)**2)
                self.record_result(self.y1, (i, j), y1val)
                self.record_result(self.y2, (i, j), y2val)
            self.record_result(self.x, i, xval)
            dp = sum(self.y1) / self.N
            self.record_result(self.yfull, i, dp)
            self.send_to_rcg(self.x, self.yfull)
            time.sleep(0.5)
            
    @rpc(flags={"async"})
    def send_to_rcg(self, x, y):
        try:
            self.rcg.plot(x, y)
        except:
            return
    
    @rpc(flags={"async"})
    def record_result(self, dataset, idx, val):
        dataset.mutate_datset(idx, val)
        # self.mutate_dataset(dataset, idx, val)
    
    # @kernel
    # def kernel_run(self):
    #     self.core.break_realtime()
    #     self.cpld.init()
    #     self.dds_397.init()
    #     self.dds_866.init()
    #     self.dds_397.set(10*MHz)
    #     self.dds_866.set(10*MHz)
    #     self.dds_397.set_att(22*dB)
    #     self.dds_866.set_att(15*dB)
    #     with parallel:
    #         self.dds_397.sw.pulse(1*s)
    #         self.dds_866.sw.pulse(1*s)
    #     delay(1*s)
    #     self.dds_397.set(100*MHz)
    #     self.dds_866.set(100*MHz)
    #     with parallel:
    #         self.dds_397.sw.pulse(1*s)
    #         self.dds_866.sw.pulse(1*s)
    #     delay(1*s)

