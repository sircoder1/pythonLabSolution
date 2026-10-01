"""Print the system hostname."""

import socket

from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("hostname", "None", "Prints the system hostname.", "python3 script.py hostname", "The hostname.", "c3tool.commands.system.hostname:HostnameCommand", order=9)


class HostnameCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        return socket.gethostname()
