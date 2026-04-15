# expert-spork — Research Update Bot

A 24/7 bot that continuously fetches and updates research files from **Wikipedia**, **arXiv**, and **RSS news feeds** for configurable topics.

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd expert-spork

# 2. Start the bot (creates venv, installs deps, runs)
chmod +x run.sh
./run.sh
```

The bot runs immediately on startup, then repeats every 60 minutes (configurable).

## Configuration

Edit `config.yaml` to customise:

| Setting | Description |
|---|---|
| `bot.update_interval_minutes` | How often to fetch updates (default: 60) |
| `bot.results_per_source` | Articles/papers per topic per source (default: 5) |
| `topics` | List of research topics to track |
| `rss_feeds` | RSS feed URLs to pull news from |
| `sources` | Toggle Wikipedia / arXiv / RSS on or off |

### Adding a new topic

```yaml
topics:
  - name: My Topic
    keywords:
      - keyword one
      - keyword two
    arxiv_category: cs.LG        # arXiv category code
    wikipedia_page: My_Topic     # Wikipedia article title (underscores)
```

## Output

Research files are written to `research/<topic_name>.md`, updated on every cycle.

Logs are written to `logs/bot_YYYYMMDD.log` and also printed to stdout.

## Running 24/7

### systemd (Linux)

Create `/etc/systemd/system/research-bot.service`:

```ini
[Unit]
Description=Research Update Bot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/expert-spork
ExecStart=/path/to/expert-spork/run.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now research-bot
sudo systemctl status research-bot
```

### Manual background process

```bash
nohup ./run.sh > logs/stdout.log 2>&1 &
echo $! > bot.pid
```

Stop it: `kill $(cat bot.pid)`

## Project Structure

```
expert-spork/
├── research_bot.py    # Main bot script
├── config.yaml        # Topics, sources, schedule
├── requirements.txt   # Python dependencies
├── run.sh             # One-command startup script
├── research/          # Generated research markdown files
└── logs/              # Rotating daily log files
```
