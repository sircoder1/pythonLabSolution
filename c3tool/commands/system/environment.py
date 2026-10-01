"""List environment variables."""

import os

from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("env", "None", "Lists environment variables.", "python3 script.py env", "Sorted NAME=value rows.", "c3tool.commands.system.environment:EnvironmentCommand", order=19)


class EnvironmentCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        return "\n".join(f"{name}={value}" for name, value in sorted(os.environ.items()))
