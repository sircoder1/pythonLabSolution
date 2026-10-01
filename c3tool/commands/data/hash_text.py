"""Calculate a SHA-256 text digest."""

import hashlib

from c3tool.model import BaseCommand, CommandSpec, ToolContext, UsageError

COMMAND_SPEC = CommandSpec("hashText", "<text>", "Calculates a SHA-256 text digest.", "python3 script.py hashText <text>", "A SHA-256 hexadecimal digest.", "c3tool.commands.data.hash_text:HashTextCommand", order=22)


class HashTextCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        if not args:
            raise UsageError(f"Usage: {COMMAND_SPEC.usage}")
        return hashlib.sha256(" ".join(args).encode("utf-8")).hexdigest()
