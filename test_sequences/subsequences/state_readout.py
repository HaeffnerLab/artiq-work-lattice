@kernel
def state_readout(self):
    with parallel:
        t_count = self.pmt.gate_rising(100*ms)
        pmt_counts = self.pmt.count(t_count)
    self.append_to_dataset(self.pmt_count_name, pmt_counts)
