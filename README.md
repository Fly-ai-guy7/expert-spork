# expert-spork

**spork** — a tiny JSON-backed CLI todo manager, written in Python.

## Usage

```
spork add "buy milk"
spork list
spork done 1
spork remove 2
spork clear
```

Tasks persist to `~/.spork.json`. Override the location with the `SPORK_FILE` environment variable.

## Run

Requires Python 3.9+. No external runtime dependencies.

```
python3 spork.py list
```

## Future work

- **TODO**: support task priorities (`low` / `medium` / `high`) via a `--priority` flag on `add`, and sort `list` by priority then id.
