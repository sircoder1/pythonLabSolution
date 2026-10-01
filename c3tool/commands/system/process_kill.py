"""Terminate one process by PID."""

import os
import signal

from c3tool.commands.system._support import optional_psutil
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext, UsageError

COMMAND_SPEC = CommandSpec("processKill", "<PID>", "Terminates a process by PID.", "python3 script.py processKill <PID>", "A termination confirmation.", "c3tool.commands.system.process_kill:ProcessKillCommand", order=13)


class ProcessKillCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        try:
            pid = int(args[0])
        except ValueError as error:
            raise UsageError("PID must be an integer") from error
        if pid <= 1 or pid == os.getpid():
            raise CommandError("Refusing to terminate PID 0, PID 1, or the current tool process")
        psutil = optional_psutil()
        if psutil:
            try:
                process = psutil.Process(pid)
                name = process.name()
                process.terminate()
                process.wait(timeout=5)
                return f"Terminated PID {pid} ({name})"
            except psutil.NoSuchProcess as error:
                raise CommandError(f"Process not found: {pid}") from error
            except psutil.AccessDenied as error:
                raise CommandError(f"Permission denied for PID {pid}") from error
            except psutil.TimeoutExpired as error:
                raise CommandError(f"PID {pid} did not terminate within 5 seconds") from error
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError as error:
            raise CommandError(f"Process not found: {pid}") from error
        except PermissionError as error:
            raise CommandError(f"Permission denied for PID {pid}") from error
        return f"Sent termination signal to PID {pid}"
