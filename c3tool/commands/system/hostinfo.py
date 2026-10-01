"""Show operating-system and hardware information."""

import os
import platform
import socket

from c3tool.commands.system._support import optional_psutil
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("hostinfo", "None", "Shows operating system and hardware information.", "python3 script.py hostinfo", "A structured host summary.", "c3tool.commands.system.hostinfo:HostInfoCommand", order=10)


class HostInfoCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        rows = [f"Hostname: {socket.gethostname()}", f"OS: {platform.system()} {platform.release()}", f"Version: {platform.version()}", f"Architecture: {platform.machine()}", f"Processor: {platform.processor() or 'unknown'}", f"Python: {platform.python_version()}", f"CPU count: {os.cpu_count() or 'unknown'}"]
        psutil = optional_psutil()
        if psutil:
            memory = psutil.virtual_memory()
            rows.extend((f"Memory total: {memory.total}", f"Memory available: {memory.available}"))
        return "\n".join(rows)
