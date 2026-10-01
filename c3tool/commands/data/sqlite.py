"""Execute a SQLite statement and format its result."""

import sqlite3
from pathlib import Path

from c3tool.model import BaseCommand, CommandError, CommandSpec, ToolContext, UsageError

COMMAND_SPEC = CommandSpec("sqlite", "<filePath> <command>", "Runs a SQLite statement.", "python3 script.py sqlite <filePath> <command>", "Query columns and rows or an affected-row count.", "c3tool.commands.data.sqlite:SqliteCommand", order=31)


class SqliteCommand(BaseCommand):
    def run(self, args, context: ToolContext) -> str:
        if len(args) < 2:
            raise UsageError(f"Usage: {COMMAND_SPEC.usage}")
        database_path = Path(args[0]).expanduser().resolve(strict=False)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = None
        try:
            connection = sqlite3.connect(database_path)
            with connection:
                cursor = connection.execute(" ".join(args[1:]))
                if cursor.description:
                    columns, rows = [column[0] for column in cursor.description], cursor.fetchall()
                    widths = [len(column) for column in columns]
                    for row in rows:
                        for index, value in enumerate(row):
                            widths[index] = max(widths[index], len(str(value)))
                    header = " | ".join(column.ljust(widths[index]) for index, column in enumerate(columns))
                    divider = "-+-".join("-" * width for width in widths)
                    body = [" | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)) for row in rows]
                    return "\n".join((header, divider, *body))
                connection.commit()
                return f"Statement complete. Rows affected: {cursor.rowcount}"
        except sqlite3.Error as error:
            raise CommandError(f"SQLite error: {error}") from error
        finally:
            if connection is not None:
                connection.close()
