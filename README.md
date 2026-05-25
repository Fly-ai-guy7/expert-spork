# expert-spork

**spork** — a tiny JSON-backed CLI todo manager, written in Python. Single file, no runtime dependencies, Python 3.9+.

## Install

There is nothing to install. Clone the repo and run `spork.py` directly:

```
python3 spork.py --help
```

To use it like a command, drop a shim on your `PATH`:

```
alias spork='python3 /path/to/expert-spork/spork.py'
```

## Usage

```
spork add "buy milk"                    # medium priority by default
spork add "ship the release" -p high
spork add "tidy desk" --priority low
spork list
spork done 2
spork remove 3
spork clear                             # drop all completed tasks
```

Example `list` output:

```
  2 [ ] !! ship the release
  1 [x]  · buy milk
  3 [ ]    tidy desk
```

Tasks are sorted by priority (high → medium → low), then by id within each tier.

## Storage

Tasks persist as JSON to `~/.spork.json` by default. Override the location with the `SPORK_FILE` environment variable — useful for per-project todo lists:

```
SPORK_FILE=./.todo.json spork add "fix the parser"
```

## Commands

| Command          | Description                                          |
| ---------------- | ---------------------------------------------------- |
| `add TEXT...`    | Add a task. `-p {low,medium,high}` sets priority.    |
| `list`           | List tasks, sorted by priority then id.              |
| `done ID`        | Mark task `ID` as done.                              |
| `remove ID`      | Delete task `ID` (whether done or not).              |
| `clear`          | Delete all completed tasks.                          |

`done` and `remove` exit non-zero if the id is unknown.

## Development

Tests use pytest:

```
pip install pytest
python3 -m pytest tests/
```
