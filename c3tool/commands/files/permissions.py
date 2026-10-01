"""Show cross-platform path permissions and ownership metadata."""

import os
import stat

from c3tool.commands.files._paths import expand_path
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("permissions", "<file>", "Shows permissions and ownership for a path.", "python3 script.py permissions <file>", "Numeric mode, symbolic mode, owner, and group.", "c3tool.commands.files.permissions:PermissionsCommand", order=26)


class PermissionsCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        target = expand_path(args[0], context)
        if not target.exists():
            raise CommandError(f"Path not found: {target}")
        details = target.stat()
        rows = [f"Path: {target}", f"Mode: {stat.filemode(details.st_mode)}", f"Numeric mode: {oct(stat.S_IMODE(details.st_mode))}"]
        if os.name == "posix":
            import grp
            import pwd

            rows.append(f"Owner: {pwd.getpwuid(details.st_uid).pw_name} ({details.st_uid})")
            rows.append(f"Group: {grp.getgrgid(details.st_gid).gr_name} ({details.st_gid})")
        else:
            rows.append(f"Owner UID: {details.st_uid}")
        return "\n".join(rows)
