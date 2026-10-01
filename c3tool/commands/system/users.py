"""List local user accounts."""

import os

from c3tool.commands.system._support import run_platform_command
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("users", "None", "Lists local user accounts.", "python3 script.py users", "Local account rows.", "c3tool.commands.system.users:UsersCommand", order=17)


class UsersCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        if os.name == "nt":
            return run_platform_command(["net", "user"])
        import pwd

        rows = ["USERNAME             UID    GID    HOME                         SHELL"]
        for user in pwd.getpwall():
            rows.append(f"{user.pw_name:20.20} {user.pw_uid:<6} {user.pw_gid:<6} {user.pw_dir:28.28} {user.pw_shell}")
        return "\n".join(rows)
