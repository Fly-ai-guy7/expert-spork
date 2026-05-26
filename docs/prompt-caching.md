# Prompt Caching

The Egyptian statute corpus is large (multi-kilobyte text block) and stable across every agent
call in a single case run. Anthropic's ephemeral prompt caching lets us pay the input-token cost
once per ~5 minutes and hit the cache on every subsequent call.

## How it's wired

`backend/app/llm/claude_client.py` builds the Anthropic `system` parameter as a list of typed
blocks:

```python
system_param = []
for block in system:
    entry = {"type": "text", "text": block.text}
    if block.cacheable:
        entry["cache_control"] = {"type": "ephemeral"}
    system_param.append(entry)
```

In `backend/app/agents/base.py`, every agent's `_system()` helper returns the disclaimer prefix
as a non-cacheable block followed by the statute corpus as a **cacheable** block:

```python
def _system(self, body: str, ctx: AgentContext) -> list[CacheBlock]:
    blocks = [CacheBlock(text=SYSTEM_DISCLAIMER_PREFIX + body, cacheable=False)]
    if ctx.statute_block:
        blocks.append(CacheBlock(text=ctx.statute_block, cacheable=True))
    return blocks
```

Anthropic caches blocks that have `cache_control={"type":"ephemeral"}` for ~5 minutes. Cache
hits on subsequent calls show up as `cache_read_input_tokens` in the usage dict.

## Expected impact

A single case run makes ~6 agent calls (evidence migration + 3 rounds × 2 sides + judicial + 6
scorings = ~13 LLM calls), all reading the same statute corpus block.

- **First call**: `cache_creation_input_tokens` pays full cost.
- **Subsequent calls within 5 min**: `cache_read_input_tokens` at ~10% of normal input cost.
- **Net**: roughly 90% reduction in repeat input token costs and 30–50% latency reduction on
  cached calls.

## DeepSeek

DeepSeek's OpenAI-compatible API does not currently support an equivalent caching primitive. The
DeepSeek client inlines a **trimmed** subset of statute articles relevant to the case rather
than the full corpus, to keep input token counts manageable. For the scaffold we pass the full
corpus for simplicity — tune `corpus_service.build_statute_block` to filter by relevance once
profiling shows it matters.

## Observability

Each `LLMResponse.usage` dict includes:

```python
{
  "input_tokens": ...,
  "output_tokens": ...,
  "cache_creation_input_tokens": ...,   # Anthropic only
  "cache_read_input_tokens": ...,       # Anthropic only
}
```

Surface these in logs (or future OTel spans) to confirm cache hit rates in production.
