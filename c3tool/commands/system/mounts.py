"""List mounted filesystems or logical drives."""

import os

from c3tool.commands.system._support import optional_psutil, run_platform_command
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("mounts", "None", "Shows mounted filesystems or logical drives.", "python3 script.py mounts", "Mount, device, filesystem, and usage rows.", "c3tool.commands.system.mounts:MountsCommand", order=25)


class MountsCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        psutil = optional_psutil()
        if psutil:
            rows = ["DEVICE                         MOUNT                          TYPE       TOTAL        FREE"]
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    rows.append(f"{partition.device:30.30} {partition.mountpoint:30.30} {partition.fstype:10.10} {usage.total:<12} {usage.free}")
                except (PermissionError, OSError):
                    rows.append(f"{partition.device:30.30} {partition.mountpoint:30.30} {partition.fstype:10.10} unavailable")
            return "\n".join(rows)
        if os.name == "nt":
            return run_platform_command(["wmic", "logicaldisk", "get", "caption,filesystem,freespace,size"])
        return run_platform_command(["mount"])
