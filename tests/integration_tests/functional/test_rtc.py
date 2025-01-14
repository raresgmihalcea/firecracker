# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""Check the well functioning af the RTC device on aarch64 platforms."""
import platform
import re

import pytest

from framework import utils

DMESG_LOG_REGEX = r"rtc-pl031\s+(\d+).rtc: setting system clock to"


@pytest.mark.skipif(
    platform.machine() != "aarch64", reason="RTC exists only on aarch64."
)
def test_rtc(test_microvm_with_api):
    """
    Test RTC functionality on aarch64.
    """
    vm = test_microvm_with_api
    vm.spawn()
    vm.memory_monitor = None
    vm.basic_config()
    vm.add_net_iface()
    vm.start()
    # check that the kernel creates an rtcpl031 base device.
    _, stdout, _ = vm.ssh.execute_command("dmesg")
    rtc_log = re.findall(DMESG_LOG_REGEX, stdout)
    assert rtc_log is not None

    _, stdout, _ = vm.ssh.execute_command("stat /dev/rtc0")
    assert "character special file" in stdout

    _, host_stdout, _ = utils.run_cmd("date +%s")
    _, guest_stdout, _ = vm.ssh.execute_command("date +%s")
    assert abs(int(guest_stdout) - int(host_stdout)) < 5
