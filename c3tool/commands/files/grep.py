"""Report lines matching a regular expression."""

import re

from c3tool.commands.files._paths import require_existing_file
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("grep", "<filename> <regex>", "Shows matching lines and line numbers.", "python3 script.py grep <filename> <regex>", "line_number: matching text rows.", "c3tool.commands.files.grep:GrepCommand", order=21)


class GrepCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 2, COMMAND_SPEC.usage)
        source = require_existing_file(args[0], context)
        try:
            pattern = re.compile(args[1])
        except re.error as error:
            raise CommandError(f"Invalid regular expression: {error}") from error
        matches = []
        with source.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                if pattern.search(line):
                    matches.append(f"{line_number}: {line.rstrip()}")
        return "\n".join(matches) if matches else "No matches found."
