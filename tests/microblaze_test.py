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

    d = downloader(yamlfilename=cfg, board_name="kcu105_adrv9371x")
    d.download_boot_files(
        "kcu105_adrv9371x",
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

    manager = nebula.manager(configfilename=cfg, board_name="kcu105_adrv9371x", microblaze=True)
    manager.monitor[0].logfilename = os.path.join(log_folder, "kcu105_adrv9371x.log") # Flush

    manager.board_reboot_auto_folder(
        out_folder,
        microblaze=True
    )
    # Boot the board
    ip = manager.monitor[0].get_ip_address_microblaze()
    assert ip is not None, "MicroBlaze board did not obtain an IP address"