from artiq import *
from artiq.language import *
from artiq.experiment import *

class test_line_trigger(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("LTriggerIN")

    def prepare(self):
        self.set_dataset("pmt_counts", [], broadcast=True)

    @kernel
    def run(self):
        self.core.reset()
        while True:
            result = self.LTriggerIN.timestamp_mu(self.seconds_to_mu(16*ms))
            self.record_result(result)
        #while True:
        #    while True:
        #        try:
        #            self.LTriggerIN.sample_input()
        #            result = self.LTriggerIN.sample_get()
        #            if result == 1:
        #                break
        #        except RTIOUnderflow:
        #            self.core.break_realtime()
        #            continue
        #    while True:
        #        try:
        #            self.LTriggerIN.sample_input()
        #            result = self.LTriggerIN.sample_get()
        #            if result == 0:
        #                self.record_result(0)
        #                break
        #        except RTIOUnderflow:
        #            self.core.break_realtime()
        #            continue

    @rpc(flags={"async"})
    def record_result(self, x):
        self.append_to_dataset("pmt_counts", x)
