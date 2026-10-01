"""List one directory."""

from c3tool.commands.files._paths import expand_path
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("ls", "<filepath, default current>", "Lists a directory.", "python3 script.py ls [filepath]", "Directory entries with type and size.", "c3tool.commands.files.list:ListCommand", order=8)


class ListCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_range(args, 0, 1, COMMAND_SPEC.usage)
        target = expand_path(args[0], context) if args else context.cwd
        if not target.is_dir():
            raise CommandError(f"Directory not found: {target}")
        rows = []
        for item in sorted(target.iterdir(), key=lambda path: path.name.lower()):
            kind = "dir" if item.is_dir() else "link" if item.is_symlink() else "file"
            size = "-" if item.is_dir() else str(item.stat().st_size)
            rows.append(f"{kind:4} {size:>10}  {item.name}")
        return "\n".join(rows) if rows else "(empty directory)"
