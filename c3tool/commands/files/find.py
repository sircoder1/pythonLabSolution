"""Recursively find partial filename matches."""

import os
from pathlib import Path

from c3tool.commands.files._paths import expand_path
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("find", "<filename> <folder>", "Recursively finds partial filename matches.", "python3 script.py find <filename> <folder>", "Matching paths.", "c3tool.commands.files.find:FindCommand", order=20)


class FindCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 2, COMMAND_SPEC.usage)
        needle = args[0].casefold()
        root = expand_path(args[1], context)
        if not root.is_dir():
            raise CommandError(f"Directory not found: {root}")
        matches = []
        for current_root, directory_names, file_names in os.walk(root):
            directory_names.sort(key=str.casefold)
            for file_name in sorted(file_names, key=str.casefold):
                if needle in file_name.casefold():
                    matches.append(str(Path(current_root) / file_name))
        return "\n".join(matches) if matches else "No matching files found."
