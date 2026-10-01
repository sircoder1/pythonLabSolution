"""Test whether a host responds to one native ping."""

import os
import subprocess

from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("ping", "<IP or hostname>", "Tests whether a host responds to ping.", "python3 script.py ping <IP>", "An online or offline result.", "c3tool.commands.network.ping:PingCommand", order=14)


class PingCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        count_flag = "-n" if os.name == "nt" else "-c"
        timeout_flag = ["-w", "2000"] if os.name == "nt" else ["-W", "2"]
        try:
            result = subprocess.run(["ping", count_flag, "1", *timeout_flag, args[0]], capture_output=True, text=True, timeout=8, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise CommandError(f"Ping failed to run: {error}") from error
        state = "online" if result.returncode == 0 else "offline"
        detail = (result.stdout or result.stderr).strip()
        return f"{args[0]} is {state}\n{detail}"
