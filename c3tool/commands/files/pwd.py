"""Print the current working directory."""

from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("pwd", "None", "Prints the current working directory.", "python3 script.py pwd", "An absolute path.", "c3tool.commands.files.pwd:PwdCommand", order=7)


class PwdCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        return str(context.cwd)
