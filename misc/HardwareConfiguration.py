from collections import namedtuple


ttl_config  = {"pmt": 0,
               "LTriggerIN": 1,
               "blue_PIs": 4,
              }

dds_specs = namedtuple("dds_specs",
                ["urukul", "channel",
              "default_freq", "min_freq", "max_freq",
              "default_att", "min_att", "max_att",
              "default_state"])

dds_config = {"866": dds_specs(0, 1, 80, 50, 100, 20, 0, 33.5, True),
              "397": dds_specs(0, 0, 80, 50, 100, 20, 0, 33.5, True),
              "854": dds_specs(0, 2, 80, 50, 100, 20, 0, 33.5, False),
              "729L1": dds_specs(1, 0, 220, 200, 240, 20, 0, 33.5, False),
              "729L2": dds_specs(1, 1, 220, 200, 240, 20, 0, 33.5, False),
              "729G": dds_specs(1, 2, 220, 200, 240, 20, 0, 33.5, False),
              }




