from artiq.experiment import *
from collections import namedtuple


ttl_config  = {"pmt": 0,
               "linetrigger_ttl": 1,
               "blue_PIs": 4,
               "camera_ttl": 6,
               "mod397": 7
            }

dds_specs = namedtuple("dds_specs",
                ["urukul", "channel",
                 "default_freq", "min_freq", "max_freq",
                 "default_att", "min_att", "max_att",
                 "default_state", "double_pass", "offset"])

dds_config = {
        "866": dds_specs(
                urukul=0,
                channel=1,
                default_freq=80,
                min_freq=50,
                max_freq=100,
                default_att=20,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "397": dds_specs(
                urukul=0,
                channel=0,
                default_freq=80,
                min_freq=50,
                max_freq=100,
                default_att=20,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "854": dds_specs(
                urukul=0,
                channel=2,
                default_freq=80,
                min_freq=50,
                max_freq=100,
                default_att=20,
                min_att=0,
                max_att=33.5,
                default_state=False,
                double_pass=False,
                offset=0
            ),
        "729L1": dds_specs(
                urukul=1,
                channel=0,
                default_freq=220,
                min_freq=200,
                max_freq=240,
                default_att=20,
                min_att=0,
                max_att=33.5,
                default_state=False,
                double_pass=True,
                offset=-0.3
            ),
        "729L2": dds_specs(
                urukul=1,
                channel=1,
                default_freq=220,
                min_freq=200,
                max_freq=240,
                default_att=20,
                min_att=0,
                max_att=33.5,
                default_state=False,
                double_pass=True,
                offset=-0.15
            ),
        "729G": dds_specs(
                urukul=0,
                channel=3,
                default_freq=220,
                min_freq=200,
                max_freq=240,
                default_att=20,
                min_att=0,
                max_att=33.5,
                default_state=False,
                double_pass=True,
                offset=0.3
            ),
        "SP_729L1": dds_specs(
                urukul=2,
                channel=0,
                default_freq=79.7,
                min_freq=50,
                max_freq=100,
                default_att=15,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "SP_729L2": dds_specs(
                urukul=2,
                channel=2,
                default_freq=80,
                min_freq=50,
                max_freq=100,
                default_att=15,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "SP_729G": dds_specs(
                urukul=1,
                channel=2,
                default_freq=80.3,
                min_freq=0,
                max_freq=100,
                default_att=15,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "SP_729L1_bichro": dds_specs(
                urukul=2,
                channel=1,
                default_freq=79.7,
                min_freq=50,
                max_freq=100,
                default_att=15,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "SP_729L2_bichro": dds_specs(
                urukul=2,
                channel=3,
                default_freq=80,
                min_freq=50,
                max_freq=100,
                default_att=15,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
        "SP_729G_bichro": dds_specs(
                urukul=1,
                channel=3,
                default_freq=80.3,
                min_freq=0,
                max_freq=100,
                default_att=15,
                min_att=0,
                max_att=33.5,
                default_state=True,
                double_pass=False,
                offset=0
            ),
    }



