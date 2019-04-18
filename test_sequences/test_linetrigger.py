from artiq import *
from artiq.language import *

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
            self.core.break_realtime()
            try:
                self.LTriggerIN.sample_input()
                result = self.LTriggerIN.sample_get()
                self.record_result(result)
            finally:
                self.core.break_realtime()
                self.LTriggerIN.watch_done()
            #self.LTriggerIN.watch_done()

    @rpc(flags={"async"})
    def record_result(x, y):
        print(x)
        print(y)
        self.append_to_dataset("pmt_counts", x)
