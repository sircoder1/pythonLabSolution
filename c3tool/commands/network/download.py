"""Download an HTTP or HTTPS resource."""

import urllib.parse
import urllib.request
from pathlib import Path

from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("download", "<source URL> [pathToSave]", "Downloads a URL to a local file.", "python3 script.py download <sourceURL> [pathToSave]", "A confirmation containing the saved path.", "c3tool.commands.network.download:DownloadCommand", order=28)


class DownloadCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_range(args, 1, 2, COMMAND_SPEC.usage)
        source = args[0]
        parsed = urllib.parse.urlparse(source)
        if parsed.scheme not in {"http", "https"}:
            raise CommandError("download supports only HTTP and HTTPS URLs")
        default_name = Path(urllib.parse.unquote(parsed.path)).name or "downloaded-file"
        destination = Path(args[1]).expanduser() if len(args) == 2 else context.cwd / default_name
        if not destination.is_absolute():
            destination = context.cwd / destination
        destination = destination.resolve(strict=False)
        destination.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(source, headers={"User-Agent": "C3T-Python-Tools/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response, destination.open("wb") as output:
                total = 0
                while chunk := response.read(65536):
                    output.write(chunk)
                    total += len(chunk)
        except Exception as error:
            destination.unlink(missing_ok=True)
            raise CommandError(f"Download failed: {error}") from error
        return f"Downloaded {total} bytes to {destination}"
