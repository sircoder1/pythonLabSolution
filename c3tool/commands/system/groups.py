"""List current-account group memberships."""

import os

from c3tool.commands.system._support import run_platform_command
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("groups", "None", "Lists current account group memberships.", "python3 script.py groups", "Group names or platform group rows.", "c3tool.commands.system.groups:GroupsCommand", order=18)


class GroupsCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        if os.name == "nt":
            return run_platform_command(["whoami", "/groups"])
        import grp

        group_ids = set(os.getgroups())
        group_ids.add(os.getgid())
        return "\n".join(sorted(grp.getgrgid(group_id).gr_name for group_id in group_ids))
