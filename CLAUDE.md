# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A "Spotify Wrapped"-style analysis tool that generates visual reports from exported Claude conversation data. Takes raw JSON exports from Claude.ai and produces an HTML report with statistics, charts, and personality insights.

## Commands

```bash
# Run the analysis pipeline (processes raw-exports/ → analysis/)
python analyze.py

# Generate HTML report (reads analysis/ → outputs to output/wrapped.html)
python generate_html.py

# Full regenerate: run both, then copy to root for GitHub Pages
python analyze.py && python generate_html.py && cp output/wrapped.html index.html
```

## Architecture

**Data Flow:** `raw-exports/*.json` → `analyze.py` → `analysis/*.json` → `generate_html.py` → `output/wrapped.html`

**analyze.py** - Core analysis engine
- Loads conversations.json, projects.json, memories.json from `raw-exports/`
- Filters to 2025 data only (`year_filter=2025`)
- Calculates statistics, topic categorization, time patterns, carbon footprint
- Outputs JSON files to `analysis/` directory
- Timestamps are UTC in raw data; converted to Central Time (UTC-6) for display

**generate_html.py** - HTML report generator
- Reads processed JSON from `analysis/`
- Generates single-file HTML with embedded CSS and Chart.js
- Uses Cartridge font (from `assets/fonts/`) for headers
- Supports light/dark mode via `prefers-color-scheme`
- Month-by-month narratives and personality insights are hardcoded in the template

**Key Data Files:**
- `analysis/wrapped.json` - Main stats used by HTML generator
- `analysis/conversation_stats.json` - Detailed conversation metrics
- `index.html` - Copy of wrapped.html for GitHub Pages hosting

## Notes

- Carbon footprint calculation uses aggressive estimates for power users with extended thinking (20 Wh/query)
- Topic categorization in `analyze.py` uses keyword matching against conversation names
- The HTML template contains hardcoded narrative text about specific months/themes that may need updating for different users
