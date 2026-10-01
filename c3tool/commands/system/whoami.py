"""Print the current account name."""

import getpass

from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("whoami", "None", "Prints the current account.", "python3 script.py whoami", "The current username.", "c3tool.commands.system.whoami:WhoAmICommand", order=6)


class WhoAmICommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        return getpass.getuser()
