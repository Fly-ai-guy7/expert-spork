Run the research bot in God Mode: maximum depth, all sources, loops every 2 hours.

Execute the following in the project root:

```bash
./run.sh --mode god
```

God Mode settings:
- 15 results per source (3x normal)
- All 8 Egyptian topics covered
- Wikipedia + arXiv + all RSS feeds active
- Loops automatically every 2 hours, 24/7
- DEBUG-level logging for full visibility

After launching, tail the logs to confirm it's running:

```bash
tail -f logs/bot_$(date +%Y%m%d).log
```

Report back with confirmation that the bot started and the first cycle completed successfully.
