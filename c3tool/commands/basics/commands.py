"""Render the reference for all recursively discovered commands."""

from c3tool.model import BaseCommand, CommandSpec, ToolContext

COMMAND_SPEC = CommandSpec("commands", "None", "Lists commands, descriptions, arguments, usage, and expected output.", "python3 script.py commands", "The complete command reference.", "c3tool.commands.basics.commands:CommandsCommand", order=5)


class CommandsCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 0, COMMAND_SPEC.usage)
        sections = []
        for spec in context.registry.specs:
            sections.append("\n".join((spec.name, f"  Description: {spec.description}", f"  Args: {spec.args}", f"  Usage: {spec.usage}", f"  Expected: {spec.expected_output}")))
        return "\n\n".join(sections)
