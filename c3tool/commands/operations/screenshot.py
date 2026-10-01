"""Capture a screenshot into the configured output folder."""

from datetime import datetime, timezone

from c3tool.model import BaseCommand, CommandError, CommandSpec, FeatureUnavailable, ToolContext

COMMAND_SPEC = CommandSpec("screenshot", "None", "Captures a screenshot in the output folder.", "python3 script.py screenshot", "The saved image path.", "c3tool.commands.operations.screenshot:ScreenshotCommand", order=29)


class ScreenshotCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        try:
            from PIL import ImageGrab
        except ImportError as error:
            raise FeatureUnavailable("Install Pillow to use screenshot") from error
        context.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = context.output_dir / f"screenshot-{timestamp}.png"
        try:
            ImageGrab.grab(all_screens=True).save(destination, format="PNG")
        except Exception as error:
            raise CommandError(f"Screenshot capture failed. Linux runners need an active graphical display: {error}") from error
        return f"Screenshot saved to {destination}"
