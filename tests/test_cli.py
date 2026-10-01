from __future__ import annotations

import hashlib
import http.server
import io
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from c3tool.catalog import COMMAND_SPECS
from c3tool.cli import main
from c3tool.discovery import discover_command_specs
from c3tool.model import CommandSpec
from c3tool.registry import CommandRegistry, MissingCommand


def invoke(arguments: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main(arguments, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_catalog_contains_every_level_command(self) -> None:
        self.assertEqual(len(COMMAND_SPECS), 32)
        self.assertEqual(len({item.name for item in COMMAND_SPECS}), 32)
        self.assertEqual(COMMAND_SPECS, discover_command_specs())
        self.assertTrue(all(spec.handler.startswith("c3tool.commands.") for spec in COMMAND_SPECS))

    def test_example_and_commands(self) -> None:
        code, output, error = invoke(["example"])
        self.assertEqual((code, output.strip(), error), (0, "Hello World", ""))
        code, output, error = invoke(["commands"])
        self.assertEqual(code, 0)
        self.assertIn("sshCracker", output)
        self.assertIn("Expected:", output)
        self.assertEqual(error, "")

    def test_removed_handler_fails_in_isolation(self) -> None:
        broken = CommandSpec("missing", "None", "test", "missing", "unavailable", "does.not.exist:Missing")
        registry = CommandRegistry([broken])
        command = registry.load("missing")
        self.assertIsInstance(command, MissingCommand)

    def test_file_lifecycle_search_and_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "nested" / "sample.txt"
            code, output, _ = invoke(["writeFile", str(target), "alpha", "ERROR", "omega"])
            self.assertEqual(code, 0)
            self.assertTrue(target.is_file())

            code, output, _ = invoke(["cat", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(output.strip(), "alpha ERROR omega")

            code, output, _ = invoke(["find", "sam", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("sample.txt", output)

            code, output, _ = invoke(["grep", str(target), "ERROR"])
            self.assertEqual(code, 0)
            self.assertIn("1: alpha ERROR omega", output)

            code, output, _ = invoke(["hashFile", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(output.strip(), hashlib.sha256(target.read_bytes()).hexdigest())

            code, _, _ = invoke(["del", str(target)])
            self.assertEqual(code, 0)
            self.assertFalse(target.exists())

    def test_md5_recovery_and_sqlite_query(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hashes = root / "hashes.txt"
            words = root / "words.txt"
            digest = hashlib.md5(b"goldenkey", usedforsecurity=False).hexdigest()
            hashes.write_text(digest + "\n", encoding="utf-8")
            words.write_text("wrong\ngoldenkey\n", encoding="utf-8")
            code, output, _ = invoke(["md5HashCracker", str(hashes), str(words)])
            self.assertEqual(code, 0)
            self.assertIn("goldenkey", output)

            database = root / "test.db"
            connection = sqlite3.connect(database)
            try:
                connection.execute("CREATE TABLE items (id INTEGER, name TEXT)")
                connection.execute("INSERT INTO items VALUES (1, 'alpha')")
                connection.commit()
            finally:
                connection.close()
            code, output, _ = invoke(["sqlite", str(database), "SELECT id, name FROM items"])
            self.assertEqual(code, 0)
            self.assertIn("alpha", output)

    def test_local_port_scan_and_banner_read(self) -> None:
        ready = threading.Event()
        holder: dict[str, int] = {}

        def serve() -> None:
            with socket.socket() as server:
                server.bind(("127.0.0.1", 0))
                server.listen(2)
                holder["port"] = server.getsockname()[1]
                ready.set()
                for _ in range(2):
                    connection, _address = server.accept()
                    with connection:
                        connection.sendall(b"C3T test banner\n")

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        self.assertTrue(ready.wait(3))
        port = holder["port"]
        code, output, _ = invoke(["portScan", "127.0.0.1", str(port)])
        self.assertEqual(code, 0)
        self.assertIn("is open", output)
        code, output, _ = invoke(["portConnect", f"127.0.0.1:{port}"])
        self.assertEqual(code, 0)
        self.assertIn("C3T test banner", output)
        thread.join(timeout=3)

    def test_disposable_process_can_be_terminated(self) -> None:
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            code, output, error = invoke(["processKill", str(process.pid)])
            self.assertEqual(code, 0, error)
            self.assertIn(str(process.pid), output)
            process.wait(timeout=6)
        finally:
            if process.poll() is None:
                process.terminate()

    def test_cross_platform_exec(self) -> None:
        command = "Write-Output runner-ok" if os.name == "nt" else "printf 'runner-ok\\n'"
        code, output, error = invoke(["exec", command])
        self.assertEqual(code, 0, error)
        self.assertIn("runner-ok", output)

    def test_download_and_ping_loopback(self) -> None:
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                body = b"download-ok\n"
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args) -> None:
                return

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                destination = Path(directory) / "result.txt"
                code, output, error = invoke([
                    "download",
                    f"http://127.0.0.1:{server.server_port}/fixture",
                    str(destination),
                ])
                self.assertEqual(code, 0, error)
                self.assertEqual(destination.read_text(encoding="utf-8"), "download-ok\n")
            code, output, error = invoke(["ping", "127.0.0.1"])
            self.assertEqual(code, 0, error)
            self.assertIn("online", output)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_system_smoke_commands(self) -> None:
        for command in ("whoami", "pwd", "hostname", "hostinfo", "interfaces", "processes", "ports", "users", "groups", "env", "mounts"):
            with self.subTest(command=command):
                code, output, error = invoke([command])
                self.assertEqual(code, 0, error)
                self.assertTrue(output.strip())


if __name__ == "__main__":
    unittest.main()
