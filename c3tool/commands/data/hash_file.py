"""Calculate a streaming SHA-256 file digest."""

import hashlib

from c3tool.commands.data._files import existing_file
from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("hashFile", "<file>", "Calculates a streaming SHA-256 file digest.", "python3 script.py hashFile <file>", "A SHA-256 hexadecimal digest.", "c3tool.commands.data.hash_file:HashFileCommand", order=23)


class HashFileCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 1, COMMAND_SPEC.usage)
        source = existing_file(args[0])
        digest = hashlib.sha256()
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
