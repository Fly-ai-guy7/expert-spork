Run the research bot in Nine Mode: fast sweep across all 9 Egyptian research topics.

Execute the following in the project root:

```bash
./run.sh --mode nine
```

Nine Mode settings:
- 3 results per source (fast/minimal)
- All Egyptian topics swept in one pass
- Runs once then exits immediately
- Lowest overhead — good for a quick status check

After it finishes:
1. List the files updated in research/
2. Show the last-modified timestamp on each
3. Report back with a one-line status per topic (updated / no new results / error)
