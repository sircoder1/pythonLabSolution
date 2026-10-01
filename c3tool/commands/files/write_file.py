"""Write text to a file."""

from c3tool.commands.files._paths import expand_path
from c3tool.model import BaseCommand, CommandSpec, ToolContext, UsageError

COMMAND_SPEC = CommandSpec("writeFile", "<filename> <text>", "Writes text to a file.", "python3 script.py writeFile <filename> <text>", "A confirmation containing the written path.", "c3tool.commands.files.write_file:WriteFileCommand", order=2)


class WriteFileCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        if len(args) < 2:
            raise UsageError(f"Usage: {COMMAND_SPEC.usage}")
        destination = expand_path(args[0], context)
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = " ".join(args[1:])
        destination.write_text(text, encoding="utf-8")
        return f"Wrote {len(text.encode('utf-8'))} bytes to {destination}"
