"""List local listening TCP and UDP endpoints."""

import os
import socket
import subprocess

from c3tool.model import BaseCommand, CommandSpec, FeatureUnavailable, ToolContext

COMMAND_SPEC = CommandSpec("ports", "None", "Lists local listening ports and services.", "python3 script.py ports", "Listening endpoints and service details.", "c3tool.commands.network.ports:PortsCommand", order=15)


class PortsCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        try:
            import psutil
        except ImportError:
            command = ["netstat", "-ano"] if os.name == "nt" else ["netstat", "-tulpen"]
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
            except OSError as error:
                raise FeatureUnavailable("Install psutil or provide netstat for the ports command") from error
            return (result.stdout or result.stderr).strip()
        rows = ["PROTO  ADDRESS                                      PORT   SERVICE          PID"]
        for connection in psutil.net_connections(kind="inet"):
            listening = connection.status == psutil.CONN_LISTEN or connection.type == socket.SOCK_DGRAM
            if not connection.laddr or not listening:
                continue
            address, port = connection.laddr.ip, connection.laddr.port
            protocol = "tcp" if connection.type == socket.SOCK_STREAM else "udp"
            try:
                service = socket.getservbyport(port, protocol)
            except OSError:
                service = "-"
            rows.append(f"{protocol:6} {address:44.44} {port:<6} {service:16.16} {connection.pid or '-'}")
        return "\n".join(rows)
