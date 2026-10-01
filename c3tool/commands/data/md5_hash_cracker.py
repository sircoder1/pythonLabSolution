"""Recover classroom MD5 values using a wordlist."""

import hashlib

from c3tool.commands.data._files import existing_file
from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("md5HashCracker", "<hashFilePath> <wordlistFilePath>", "Recovers classroom MD5 values using a wordlist.", "python3 script.py md5HashCracker <hashFilePath> <wordlistFilePath>", "Recovered hash-to-word mappings.", "c3tool.commands.data.md5_hash_cracker:Md5HashCrackerCommand", order=30)


class Md5HashCrackerCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 2, COMMAND_SPEC.usage)
        hash_file, wordlist_file = existing_file(args[0]), existing_file(args[1])
        targets = {line.strip().lower() for line in hash_file.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()}
        invalid = sorted(value for value in targets if len(value) != 32 or any(char not in "0123456789abcdef" for char in value))
        if invalid:
            raise CommandError(f"Invalid MD5 digest in hash file: {invalid[0]}")
        recovered = {}
        with wordlist_file.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                word = line.rstrip("\r\n")
                digest = hashlib.md5(word.encode("utf-8"), usedforsecurity=False).hexdigest()
                if digest in targets and digest not in recovered:
                    recovered[digest] = word
                if len(recovered) == len(targets):
                    break
        rows = [f"{digest}: {recovered[digest]}" for digest in sorted(recovered)]
        rows.extend(f"{digest}: not found" for digest in sorted(targets - recovered.keys()))
        return "\n".join(rows) if rows else "No hashes were supplied."
