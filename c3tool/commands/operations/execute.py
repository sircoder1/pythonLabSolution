"""Run one command through Bash or PowerShell."""

import os
import shutil
import subprocess

from c3tool.model import BaseCommand, CommandError, CommandSpec, FeatureUnavailable, ToolContext, UsageError

COMMAND_SPEC = CommandSpec("exec", "<command>", "Runs a command in Bash or PowerShell.", "python3 script.py exec <command>", "Captured stdout, stderr, and exit code.", "c3tool.commands.operations.execute:ExecCommand", order=27)


class ExecCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        if not args:
            raise UsageError(f"Usage: {COMMAND_SPEC.usage}")
        command = " ".join(args)
        if os.name == "nt":
            executable = shutil.which("pwsh") or shutil.which("powershell")
            if not executable:
                raise FeatureUnavailable("PowerShell was not found")
            invocation = [executable, "-NoProfile", "-NonInteractive", "-Command", command]
        else:
            invocation = [shutil.which("bash") or "/bin/bash", "-lc", command]
        try:
            result = subprocess.run(invocation, capture_output=True, text=True, timeout=60, check=False)
        except subprocess.TimeoutExpired as error:
            raise CommandError("Command exceeded the 60-second timeout") from error
        except OSError as error:
            raise CommandError(f"Could not start the platform shell: {error}") from error
        sections = []
        if result.stdout:
            sections.append(result.stdout.rstrip())
        if result.stderr:
            sections.append(f"[stderr]\n{result.stderr.rstrip()}")
        sections.append(f"[exit code: {result.returncode}]")
        return "\n".join(sections)
