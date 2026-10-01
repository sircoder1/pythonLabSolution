"""Connect to a TCP endpoint and print received data."""

import socket

from c3tool.commands.network._addressing import parse_host_port
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("portConnect", "<host:port>", "Connects to a TCP port and prints received data.", "python3 script.py portConnect <host:port>", "The received banner or a no-data message.", "c3tool.commands.network.port_connect:PortConnectCommand", order=32)


class PortConnectCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        host, port = parse_host_port(args[0])
        chunks = []
        try:
            with socket.create_connection((host, port), timeout=4) as connection:
                connection.settimeout(2)
                while sum(map(len, chunks)) < 65536:
                    try:
                        chunk = connection.recv(min(4096, 65536 - sum(map(len, chunks))))
                    except socket.timeout:
                        break
                    if not chunk:
                        break
                    chunks.append(chunk)
        except OSError as error:
            raise CommandError(f"Could not connect to {host}:{port}: {error}") from error
        if not chunks:
            return f"Connected to {host}:{port}; no data was received before timeout."
        return b"".join(chunks).decode("utf-8", errors="replace")
