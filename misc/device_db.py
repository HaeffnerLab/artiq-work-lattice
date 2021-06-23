
try:
    from HardwareConfiguration import *
    config_found = True
except:
    config_found = False


core_addr = "192.168.169.254"


device_db = {
    "core": {
        "type": "local",
        "module": "artiq.coredevice.core",
        "class": "Core",
        "arguments": {"host": core_addr, "ref_period": 1.25e-9, "target": "or1k"}
    },
    "core_log": {
        "type": "controller",
        "host": "::1",
        "port": 1068,
        "command": "aqctl_corelog -p {port} --bind {bind} " + core_addr
    },
    "core_cache": {
        "type": "local",
        "module": "artiq.coredevice.cache",
        "class": "CoreCache"
    },
    "core_dma": {
        "type": "local",
        "module": "artiq.coredevice.dma",
        "class": "CoreDMA"
    },

    "i2c_switch0": {
        "type": "local",
        "module": "artiq.coredevice.i2c",
        "class": "PCA9548",
        "arguments": {"address": 0xe0}
    },
    "i2c_switch1": {
        "type": "local",
        "module": "artiq.coredevice.i2c",
        "class": "PCA9548",
        "arguments": {"address": 0xe2}
    },
}

# device_db.update({
#     "ttl" + str(i): {
#         "type": "local",
#         "module": "artiq.coredevice.ttl",
#         "class": "TTLInOut" if i < 4 else "TTLOut",
#         "arguments": {"channel": i},
#     } for i in range(1, 16)
# })


sync_delay_seeds = [ [10, 12, 11, 13] ,
                     [20, 20, 19, 9] ,
                     [15, 15, 16, 16] ,
                     [15, 15, 15, 15] ]
io_update_delays = [ [3, 3, 0, 3] ,
                    [0, 0, 0, 3] ,
                    [0, 0, 0, 0] ,
                    [3, 3, 3, 3] ]


for j in range(4):
    device_db.update({
        "spi_urukul{}".format(j): {
            "type": "local",
            "module": "artiq.coredevice.spi2",
            "class": "SPIMaster",
            "arguments": {"channel": 16 + 7*j}
        },
        "ttl_urukul{}_sync".format(j): {
            "type": "local",
            "module": "artiq.coredevice.ttl",
            "class": "TTLClockGen",
            "arguments": {"channel": 17 + 7*j, "acc_width": 4}
        },
        "ttl_urukul{}_io_update".format(j): {
            "type": "local",
            "module": "artiq.coredevice.ttl",
            "class": "TTLOut",
            "arguments": {"channel": 18 + 7*j}
        },
        "ttl_urukul{}_sw0".format(j): {
            "type": "local",
            "module": "artiq.coredevice.ttl",
            "class": "TTLOut",
            "arguments": {"channel": 19 + 7*j}
        },
        "ttl_urukul{}_sw1".format(j): {
            "type": "local",
            "module": "artiq.coredevice.ttl",
            "class": "TTLOut",
            "arguments": {"channel": 20 + 7*j}
        },
        "ttl_urukul{}_sw2".format(j): {
            "type": "local",
            "module": "artiq.coredevice.ttl",
            "class": "TTLOut",
            "arguments": {"channel": 21 + 7*j}
        },
        "ttl_urukul{}_sw3".format(j): {
            "type": "local",
            "module": "artiq.coredevice.ttl",
            "class": "TTLOut",
            "arguments": {"channel": 22 + 7*j}
        },
        "urukul{}_cpld".format(j): {
            "type": "local",
            "module": "artiq.coredevice.urukul",
            "class": "CPLD",
            "arguments": {
                "spi_device": "spi_urukul{}".format(j),
                "sync_device": "ttl_urukul{}_sync".format(j),
                "io_update_device": "ttl_urukul{}_io_update".format(j),
                "refclk": 100e6,
                "clk_sel": 2,
                "sync_sel": 0,
            }
        }
    })

    device_db.update({
        "urukul{}_ch{}".format(j, i): {
            "type": "local",
            "module": "artiq.coredevice.ad9910",
            "class": "AD9910",
            "arguments": {
                "pll_n": 32,
                "pll_vco": 4,
                "chip_select": 4 + i,
                "cpld_device": "urukul{}_cpld".format(j),
                "sw_device": "ttl_urukul{}_sw{}".format(j, i),
                "sync_delay_seed": sync_delay_seeds[j][i],
                "io_update_delay": io_update_delays[j][i],
            }
        } for i in range(4)
    })



#device_db.update(urukul3_cpld={
#        "type": "local",
#        "module": "artiq.coredevice.urukul",
#        "class": "CPLD",
#       "arguments": {
#            "spi_device": "spi_urukul3",
#            "io_update_device": "ttl_urukul3_io_update",
#            "refclk": 100e6,
#            "clk_sel": 0
#        }
#    }
#)
#
#for i in range(4):
#    device_db["urukul3_ch" + str(i)] = {
#        "type": "local",
#        "module": "artiq.coredevice.ad9912",
#        "class": "AD9912",
#        "arguments": {
#            "pll_n": 8,
#            "chip_select": 4 + i,
#            "cpld_device": "urukul3_cpld",
#            "sw_device": "ttl_urukul3_sw" + str(i)
#        }
#    }


device_db.update({
    "spi_zotino0": {
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {"channel": 43}
    },
    "ttl_zotino0_ldac": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": 44}
    },
    "ttl_zotino0_clr": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": 45}
    },
    "zotino0": {
        "type": "local",
        "module": "artiq.coredevice.zotino",
        "class": "Zotino",
        "arguments": {
            "spi_device": "spi_zotino0",
            "ldac_device": "ttl_zotino0_ldac",
            "clr_device": "ttl_zotino0_clr"
        }
    }
})


device_db.update({
    "led0": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": 46}
    },
    "led1": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": 47}
    }
})


if config_found:
    for name, channel in ttl_config.items():
#        if channel == 0:
#            device_db.update({
#                name: {
#                    "type": "local",
#                    "module": "artiq.coredevice.edge_counter",
#                    "class": "EdgeCounter",
#                    "arguments": {"channel": channel}
#                    }
#                })
#
        if channel < 4:
            cls = "TTLInOut"
        else:
            cls = "TTLOut"
        device_db.update({
            name: {
                "type": "local",
                "module": "artiq.coredevice.ttl",
                "class": cls,
                "arguments": {"channel": channel}
                }
            })

    for name, specs in dds_config.items():
        dev, channel = specs.urukul, specs.channel
        #if dev == 3: channel += 1
        device_db.update({
            "_" + name : {
                "type": "local",
                "module": "artiq.coredevice.ttl",
                "class": "TTLOut",
                "arguments": {"channel": 19 + channel + 7 * dev}
                }
            })
        if dev < 4:
            module = "artiq.coredevice.ad9910"
            cls = "AD9910"
            device_db.update({
                name: {
                    "type": "local",
                    "module": module,
                    "class": cls,
                    "arguments": {
                        "pll_n": 32,
                        "pll_vco": 4,
                        "chip_select": 4 + channel,
                        "cpld_device": "urukul{}_cpld".format(dev),
                        "sw_device": "_" + name,
                        "sync_delay_seed": sync_delay_seeds[dev][channel],
                        "io_update_delay": io_update_delays[dev][channel]
                        }}
                    })
        #elif dev == 3:
        #    #pass
        #    module = "artiq.coredevice.ad9912"
        #    cls = "AD9912"
        #    device_db.update({
        #        "type": "local",
        #        "module": module,
        #        "class": "AD9912",
        #        "arguments": {
        #            "pll_n": 8,
        #            "chip_select": 4 + channel,
        #            "cpld_device": "urukul3_cpld",
        #            "sw_device": "ttl_urukul3_sw" + str(channel)
        #            }})

