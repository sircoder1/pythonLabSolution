"""List network interfaces and addresses."""

import socket

from c3tool.commands.system._support import optional_psutil
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("interfaces", "None", "Lists network interfaces and addresses.", "python3 script.py interfaces", "Interface and address rows.", "c3tool.commands.system.interfaces:InterfacesCommand", order=11)


class InterfacesCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        psutil = optional_psutil()
        if psutil:
            rows = []
            for interface, addresses in sorted(psutil.net_if_addrs().items()):
                for address in addresses:
                    family = getattr(address.family, "name", str(address.family))
                    rows.append(f"{interface:20} {family:12} {address.address}")
            return "\n".join(rows) if rows else "No interfaces found."
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(socket.gethostname(), None)})
        return "\n".join(f"host                 address      {address}" for address in addresses)
