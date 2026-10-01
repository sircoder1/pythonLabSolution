# C3T Python Tools

A cross-platform Python command toolkit used as the complete reference implementation for the Obsidian Runner course.

Every command now lives in its own file under a category folder:

```text
c3tool/commands/
  basics/example.py
  files/write_file.py
  network/ping.py
  system/process_kill.py
  ...one module per command
```

`script.py` asks `c3tool/discovery.py` to recursively walk those folders. Any module exposing a `COMMAND_SPEC` is registered automatically, so adding a command never requires editing a central command list. Implementations are still loaded lazily when their command runs, so one unfinished command does not prevent unrelated commands from working.

## Setup

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

The standard-library commands work without optional packages. `psutil` improves process, port, interface, mount, and host information; `Pillow` provides screenshots; `paramiko` provides the classroom SSH password-audit command.

## Usage

```bash
python3 script.py commands
python3 script.py example
python3 script.py hostinfo
python3 script.py portScan 127.0.0.1 8000
python3 script.py grep ./events.log "ERROR|WARN"
```

Run `python3 script.py commands` for the complete command, argument, usage, and expected-output reference.

## Creating the student edition

Keep the small framework intact:

- `script.py`
- `c3tool/cli.py`
- `c3tool/discovery.py`
- `c3tool/model.py`
- `c3tool/registry.py`

Each exercise has exactly one implementation file in `c3tool/commands/<category>/`. Keep its `COMMAND_SPEC`, then replace only the command class's `run` body with:

```python
raise NotImplementedError("Rebuild this command")
```

The CLI will still start, list the command, and run all remaining implementations. The selected command will return a clear not-implemented error until the student rebuilds it.

To add a brand-new command, copy one command module into any category folder, give it a unique `COMMAND_SPEC.name`, and point `COMMAND_SPEC.handler` at its command class. Recursive discovery handles the rest.

## Output folder

The `screenshot` command writes to `LAB_OUTPUT` when Obsidian Runner supplies it. Otherwise it writes to `./outputs`. Other commands write only to paths supplied on their command line.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
