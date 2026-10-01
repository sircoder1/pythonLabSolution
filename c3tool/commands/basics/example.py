"""Print the first-course hello-world result."""

from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("example", "None", "Prints hello world.", "python3 script.py example", "Hello World", "c3tool.commands.basics.example:ExampleCommand", order=1)


class ExampleCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        return "Hello World"
