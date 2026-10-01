"""Test one TCP host and port."""

import socket

from c3tool.commands.network._addressing import parse_port
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("portScan", "<host> <port>", "Tests one TCP host and port.", "python3 script.py portScan <host> <port>", "An open or closed result.", "c3tool.commands.network.port_scan:PortScanCommand", order=16)


class PortScanCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 2, COMMAND_SPEC.usage)
        host, port = args[0], parse_port(args[1])
        try:
            with socket.create_connection((host, port), timeout=3):
                return f"{host}:{port} is open"
        except (OSError, socket.timeout) as error:
            return f"{host}:{port} is closed or unreachable ({error})"
