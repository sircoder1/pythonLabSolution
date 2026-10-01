"""Delete one file or symbolic link without recursive removal."""

from c3tool.commands.files._paths import expand_path
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("del", "<filepath>", "Deletes one file or symbolic link.", "python3 script.py del <filepath>", "A deletion confirmation.", "c3tool.commands.files.delete:DeleteCommand", order=4)


class DeleteCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        target = expand_path(args[0], context)
        if target.is_dir() and not target.is_symlink():
            raise CommandError("del removes files or symbolic links, not directories")
        if not target.exists() and not target.is_symlink():
            raise CommandError(f"Path not found: {target}")
        target.unlink()
        return f"Deleted {target}"
