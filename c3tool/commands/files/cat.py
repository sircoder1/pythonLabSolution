"""Print a text file."""

from c3tool.commands.files._paths import require_existing_file
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("cat", "<filepath>", "Prints a text file.", "python3 script.py cat <filepath>", "The complete file contents.", "c3tool.commands.files.cat:CatCommand", order=3)


class CatCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        return require_existing_file(args[0], context).read_text(encoding="utf-8", errors="replace")
