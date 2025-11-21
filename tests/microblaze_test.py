import os
import time
import pytest
import shutil
from nebula import downloader

here = os.path.dirname(os.path.abspath(__file__))
cfg = os.path.join(here, "nebula_config","microblaze.yaml")
out_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outs")
log_folder = os.path.join(here, "logs")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

def test_microblaze_downloader():
    # Clean output folder
    if os.path.isdir(out_folder):
        shutil.rmtree(out_folder)

    d = downloader(yamlfilename=cfg, board_name="kc705_ad9467_fmc")
    d.download_boot_files(
        "kc705_ad9467_fmc",
        source="artifactory",
        source_root="artifactory.analog.com",
        branch="main",
        microblaze=True,
    )

    assert os.path.isfile(os.path.join(out_folder, "system_top.bit"))
    assert os.path.isfile(os.path.join(out_folder, "simpleImage.strip"))
    assert os.path.isfile(os.path.join(out_folder, "properties.yaml"))
    assert os.path.isfile(os.path.join(out_folder, "hashes.txt"))

def test_microblaze_boot():
    # Use files from outs folder
    bitstream = os.path.join("/root/wk_ace/nebula/outs/", "system_top.bit")
    strip = os.path.join("/root/wk_ace/nebula/outs/", "simpleImage.strip")
    assert os.path.isfile(bitstream), "Bitstream file not found"
    assert os.path.isfile(strip), "Strip file not found"

    import nebula

    manager = nebula.manager(configfilename=cfg, board_name="kc705_ad9467_fmc")
    manager.monitor[0].logfilename = os.path.join(log_folder, "kc705_ad9467_fmc.log") # Flush
    manager.monitor[0].print_to_console = True
    manager.monitor[0].start_log(logappend=True)


    # Boot the board
    manager.jtag.microblaze_boot_linux(bitstream, strip)
    time.sleep(60)
    manager.monitor[0].stop_log()
    manager.monitor[0]._wait_for_boot_complete_microblaze()
    time.sleep(5)
    manager.monitor[0].stop_log()
    manager.monitor[0].request_ip_dhcp_microblaze()
    manager.monitor[0].stop_log()