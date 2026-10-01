"""List running processes."""

import os

from c3tool.commands.system._support import optional_psutil, run_platform_command
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("processes", "None", "Lists running processes.", "python3 script.py processes", "PID, user, name, and command rows.", "c3tool.commands.system.processes:ProcessesCommand", order=12)


class ProcessesCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        psutil = optional_psutil()
        if psutil:
            rows = ["PID      USER                 NAME                 COMMAND"]
            for process in psutil.process_iter(("pid", "username", "name", "cmdline")):
                try:
                    info = process.info
                    command = " ".join(info.get("cmdline") or [])
                    rows.append(f"{info['pid']:<8} {(info.get('username') or '-'):20.20} {(info.get('name') or '-'):20.20} {command}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return "\n".join(rows)
        return run_platform_command(["tasklist"] if os.name == "nt" else ["ps", "-eo", "pid,user,comm,args"])
