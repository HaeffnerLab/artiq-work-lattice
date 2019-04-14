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
        self.setattr_argument("scan", scan.Scannable(default=scan.RangeScan(0, 1, 100)))

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

        self.set_dataset("x", np.full(M, np.nan))
        self.set_dataset("y1", np.full((M, N), np.nan))
        self.set_dataset("y2", np.full((M, N), np.nan))
        self.set_dataset("yfull1", np.full(M, np.nan))
        self.set_dataset("yfull2", np.full(M, np.nan))
        A = np.full((M, N), np.nan)
        for x in np.nditer(A, op_flags=["readwrite"]):
            x[...] = np.random.normal(0, .1)
        self.set_dataset("rand", A)
        self.setattr_dataset("x")
        self.setattr_dataset("y1")
        self.setattr_dataset("y2")
        self.setattr_dataset("yfull1")
        self.setattr_dataset("yfull2")

        #------------- declare tab for plotting -------------------------------
        self.RCG_TAB = "Rabi"

    def run(self):
        for i, step in enumerate(self.scan):
            for j, _ in enumerate(self.repeat):
                xval = step
                y1val = np.sin(2*np.pi * xval)**2 + self.get_dataset("rand")[i, j]
                y2val = np.cos(2*np.pi * xval)**2 + self.get_dataset("rand")[i, j]
                self.record_result("y1", (i, j), y1val)
                self.record_result("y2", (i, j), y2val)
            self.record_result("x", i, xval)
            dp = sum(self.get_dataset("y1")[i]) / self.N
            self.record_result("yfull1", i, dp)
            dp1 = sum(self.get_dataset("y2")[i] / self.N)
            self.record_result("yfull2", i, dp1)
            self.send_to_rcg(self.get_dataset("x"), self.get_dataset("yfull1"))
            self.send_to_rcg(self.get_dataset("x"), self.get_dataset("yfull2"))
            time.sleep(0.5)
            
    @rpc(flags={"async"})
    def send_to_rcg(self, x, y):
        try:
            self.rcg.plot(x, y, self.rcg-tab)
        except:
            return
    
    @rpc(flags={"async"})
    def record_result(self, dataset, idx, val):
        self.mutate_dataset(dataset, idx, val)
    
