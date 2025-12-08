# Claude 2025 Wrapped

A "Spotify Wrapped"-style analysis of my Claude conversation history for 2025.

**[View the live report](https://alexpriest.github.io/claude-2025-wrapped/)**

## Why I Made This

I was curious what patterns would emerge from a year of Claude conversations. Turns out I had 501 conversations, wrote 100k+ words, and use Claude more as a thinking partner than a search engine.

## How It Works

1. Export your data from Claude.ai (Settings → Export Data)
2. Drop the JSON files in `raw-exports/`
3. Run `python analyze.py` to process the data
4. Run `python generate_html.py` to generate the report
5. Open `output/wrapped.html`

The analysis includes conversation stats, topic categorization, time patterns, personality insights, and a carbon footprint estimate with offset cost.

## Notes

- Timestamps are converted from UTC to Central Time
- The month-by-month narratives in `generate_html.py` are specific to my year—you'd want to customize those
- Carbon calculation uses aggressive estimates for extended thinking usage (20 Wh/query)
