#!/usr/bin/env python3
"""
Generate a visual HTML Wrapped report
"""

import json
from pathlib import Path

ANALYSIS_DIR = Path(__file__).parent / "analysis"
OUTPUT_DIR = Path(__file__).parent / "output"

def load_wrapped():
    with open(ANALYSIS_DIR / "wrapped.json", "r") as f:
        return json.load(f)

def load_stats():
    with open(ANALYSIS_DIR / "conversation_stats.json", "r") as f:
        return json.load(f)

def generate_html():
    wrapped = load_wrapped()
    stats = load_stats()

    # Prepare data for charts
    months_data = stats.get("conversations_by_month", {})
    sorted_months = sorted(months_data.items())
    months_labels = [m[0] for m in sorted_months]
    months_values = [m[1] for m in sorted_months]

    hours_data = stats.get("messages_by_hour", {})
    hours_labels = [str(h) for h in range(24)]
    hours_values = [hours_data.get(str(h), 0) for h in range(24)]

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_data = stats.get("messages_by_weekday", {})
    weekday_values = [weekday_data.get(d, 0) for d in weekday_order]

    topics = wrapped.get("top_topics", [])
    topic_labels = [t[0] for t in topics]
    topic_values = [t[1] for t in topics]

    headline = wrapped.get("headline_stats", {})
    comparisons = wrapped.get("fun_comparisons", {})
    insights = wrapped.get("personality_insights", {})
    peak = wrapped.get("peak_usage", {})
    time_patterns = wrapped.get("time_patterns", {})
    records = wrapped.get("streaks_and_records", {})
    carbon = wrapped.get("carbon_footprint", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alex's Claude 2025 Wrapped</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #fffcf0;
            --bg-secondary: #f5f2e6;
            --bg-card: #ffffff;
            --accent: #CB6120;
            --accent-light: #e07830;
            --accent-glow: rgba(203, 97, 32, 0.15);
            --text-primary: #100f0f;
            --text-secondary: #57534e;
            --text-muted: #78716c;
            --border: #e5e2d9;
        }}

        body {{
            font-family: 'Work Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 300;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            padding: 3rem 0;
        }}

        h1 {{
            font-size: 3rem;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}

        .subtitle {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            font-weight: 300;
        }}

        .section {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }}

        .section h2 {{
            font-size: 1.25rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
            color: var(--accent);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }}

        .stat-card {{
            background: var(--bg-card);
            border-radius: 8px;
            padding: 1.25rem;
            text-align: center;
            border: 1px solid var(--border);
        }}

        .stat-value {{
            font-size: 2.25rem;
            font-weight: 600;
            color: var(--accent);
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
            font-weight: 400;
        }}

        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1rem;
        }}

        .comparison-card {{
            background: var(--bg-card);
            border-radius: 8px;
            padding: 1.25rem;
            text-align: center;
            border: 1px solid var(--border);
        }}

        .comparison-icon {{
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }}

        .comparison-value {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-light);
        }}

        .comparison-label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}

        .chart-container {{
            height: 280px;
            margin: 1rem 0;
        }}

        .chart-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 1.5rem;
        }}

        .chart-section h3 {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
            font-weight: 400;
        }}

        .topic-list {{
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }}

        .topic-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .topic-rank {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--accent);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.85rem;
            color: #fff;
        }}

        .topic-bar {{
            flex: 1;
            height: 36px;
            background: var(--bg-card);
            border-radius: 6px;
            overflow: hidden;
            position: relative;
            border: 1px solid var(--border);
        }}

        .topic-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--accent-light));
            border-radius: 5px;
            display: flex;
            align-items: center;
            padding-left: 0.75rem;
        }}

        .topic-name {{
            font-size: 0.85rem;
            white-space: nowrap;
            font-weight: 500;
            color: #fff;
        }}

        .topic-count {{
            position: absolute;
            right: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .insight-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
        }}

        .insight-card {{
            background: var(--bg-card);
            border-radius: 8px;
            padding: 1.25rem;
            border-left: 3px solid var(--accent);
        }}

        .insight-title {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .insight-value {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-primary);
        }}

        .longest-convos {{
            margin-top: 1.5rem;
        }}

        .longest-convos h3 {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
            font-weight: 400;
        }}

        .convo-item {{
            padding: 0.875rem 1rem;
            background: var(--bg-card);
            border-radius: 6px;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
        }}

        .convo-name {{
            font-size: 0.9rem;
            max-width: 75%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-weight: 400;
        }}

        .convo-msgs {{
            color: var(--accent);
            font-weight: 500;
            font-size: 0.9rem;
        }}

        .deep-insight {{
            padding: 1.5rem;
            background: var(--bg-card);
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid var(--border);
        }}

        .deep-insight h3 {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--accent);
            margin-bottom: 0.75rem;
        }}

        .deep-insight p {{
            font-size: 0.95rem;
            line-height: 1.7;
            color: var(--text-secondary);
        }}

        .deep-insight .highlight {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        .traits-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            margin-top: 1.5rem;
        }}

        .traits-column h3 {{
            font-size: 1rem;
            font-weight: 500;
            color: var(--accent);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}

        .traits-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .traits-list li {{
            margin-bottom: 1.25rem;
            padding-left: 0;
        }}

        .traits-list li strong {{
            display: block;
            font-size: 0.95rem;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 0.35rem;
        }}

        .traits-list li span {{
            display: block;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-secondary);
        }}

        .traits-list.growth li strong {{
            color: var(--text-primary);
        }}

        .month-narrative {{
            padding: 1.5rem;
            background: var(--bg-card);
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid var(--border);
        }}

        .month-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .month-name {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--accent);
        }}

        .month-theme {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-style: italic;
        }}

        .month-narrative p {{
            font-size: 0.95rem;
            line-height: 1.7;
            color: var(--text-secondary);
            margin: 0;
        }}

        .month-narrative p strong {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        footer {{
            text-align: center;
            padding: 2.5rem 1rem;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        footer p {{
            margin-bottom: 0.25rem;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            h1 {{
                font-size: 2rem;
            }}
            .chart-row {{
                grid-template-columns: 1fr;
            }}
            .section {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Claude 2025 Wrapped</h1>
            <p class="subtitle">Your year in AI conversations</p>
        </header>

        <section class="section">
            <h2>The Big Numbers</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{headline.get('total_conversations', 0)}</div>
                    <div class="stat-label">Conversations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{headline.get('total_messages', 0):,}</div>
                    <div class="stat-label">Messages Exchanged</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{headline.get('total_words_you_wrote', 0):,}</div>
                    <div class="stat-label">Words You Wrote</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{headline.get('total_words_claude_wrote', 0):,}</div>
                    <div class="stat-label">Words Claude Wrote</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">140</div>
                    <div class="stat-label">Days Active</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">3.6</div>
                    <div class="stat-label">Avg Convos/Day</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">44</div>
                    <div class="stat-label">Deep Dives (20+ msgs)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{headline.get('projects_used', 0)}</div>
                    <div class="stat-label">Projects Used</div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>Together We Wrote...</h2>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1.25rem;">{headline.get('total_words_exchanged', 0):,} total words exchanged</p>
            <div class="comparison-grid">
                <div class="comparison-card">
                    <div class="comparison-icon">📖</div>
                    <div class="comparison-value">{comparisons.get('equivalent_novels', 0)}</div>
                    <div class="comparison-label">Novels Worth of Text</div>
                </div>
                <div class="comparison-card">
                    <div class="comparison-icon">📄</div>
                    <div class="comparison-value">{comparisons.get('pages_of_text', 0):,}</div>
                    <div class="comparison-label">Pages of Writing</div>
                </div>
                <div class="comparison-card">
                    <div class="comparison-icon">🎧</div>
                    <div class="comparison-value">{comparisons.get('hours_of_audiobook', 0)}</div>
                    <div class="comparison-label">Hours of Audiobook</div>
                </div>
                <div class="comparison-card">
                    <div class="comparison-icon">📕</div>
                    <div class="comparison-value">{comparisons.get('the_great_gatsby_equivalents', 0)}x</div>
                    <div class="comparison-label">The Great Gatsby</div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>Your Top Topics</h2>
            <div class="topic-list">
                {"".join(f'''
                <div class="topic-item">
                    <div class="topic-rank">{i+1}</div>
                    <div class="topic-bar">
                        <div class="topic-fill" style="width: {min(100, t[1] / max(topic_values) * 100)}%">
                            <span class="topic-name">{t[0]}</span>
                        </div>
                        <span class="topic-count">{t[1]} convos</span>
                    </div>
                </div>
                ''' for i, t in enumerate(topics))}
            </div>
        </section>

        <section class="section">
            <h2>Conversation Patterns</h2>
            <div class="chart-row">
                <div>
                    <h3 style="font-size: 1rem; color: #94a3b8; margin-bottom: 0.5rem;">Conversations by Month</h3>
                    <div class="chart-container">
                        <canvas id="monthsChart"></canvas>
                    </div>
                </div>
                <div>
                    <h3 style="font-size: 1rem; color: #94a3b8; margin-bottom: 0.5rem;">Messages by Hour</h3>
                    <div class="chart-container">
                        <canvas id="hoursChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>Your Personality Insights</h2>
            <div class="insight-grid">
                <div class="insight-card">
                    <div class="insight-title">Your Chronotype</div>
                    <div class="insight-value">{time_patterns.get('chronotype', 'N/A')}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Peak Hour</div>
                    <div class="insight-value">{peak.get('favorite_hour', 'N/A')}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Peak Day</div>
                    <div class="insight-value">{peak.get('favorite_day', 'N/A')}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Communication Style</div>
                    <div class="insight-value">{insights.get('your_communication_style', 'N/A')}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Quick Q&As</div>
                    <div class="insight-value">{insights.get('quick_chats', 0)}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Deep Dives (20+ msgs)</div>
                    <div class="insight-value">{insights.get('deep_dives', 0)}</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Claude Verbosity Ratio</div>
                    <div class="insight-value">{insights.get('claude_verbosity_ratio', 0)}x</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Weekend Usage</div>
                    <div class="insight-value">{time_patterns.get('weekend_percentage', 0)}%</div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>Records & Trends</h2>
            <div class="insight-grid">
                <div class="insight-card">
                    <div class="insight-title">Busiest Month</div>
                    <div class="insight-value">{records.get('busiest_month', 'N/A')} ({records.get('busiest_month_convos', 0)} convos)</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Usage Trend</div>
                    <div class="insight-value">{records.get('usage_trend', 'N/A')}</div>
                </div>
            </div>

            <div class="longest-convos">
                <h3 style="font-size: 1rem; color: #94a3b8; margin-bottom: 1rem;">Your Longest Conversations</h3>
                {"".join(f'''
                <div class="convo-item">
                    <span class="convo-name">{c['name'][:60]}...</span>
                    <span class="convo-msgs">{c['messages']} msgs</span>
                </div>
                ''' for c in records.get('top_5_longest', [])[:5])}
            </div>
        </section>

        <section class="section">
            <h2>Carbon Footprint & Offset</h2>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1.25rem;">Claude.ai web usage only — API and Claude Code usage would add to this total</p>
            <div class="deep-insight">
                <h3>Your Environmental Impact</h3>
                <p>Your {carbon.get('message_pairs', 0):,} message exchanges produced an estimated <span class="highlight">{carbon.get('total_co2_kg', 0)} kg of CO2</span>. That's {carbon.get('operational_co2_kg', 0)} kg from inference + hardware embodied carbon, plus {carbon.get('training_co2_kg', 0)} kg from amortized model training. Equivalent to driving <span class="highlight">{int(carbon.get('car_miles_equivalent', 0)):,} miles</span>. Data center and power plant cooling used <span class="highlight">{int(carbon.get('water_liters', 0)):,} liters of water</span> ({carbon.get('showers_equivalent', 0)} showers).</p>
            </div>

            <div class="stats-grid" style="margin-top: 1rem;">
                <div class="stat-card">
                    <div class="stat-value">{carbon.get('total_co2_kg', 0)}</div>
                    <div class="stat-label">kg CO2</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{carbon.get('operational_kwh', 0)}</div>
                    <div class="stat-label">kWh Energy</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{int(carbon.get('water_liters', 0)):,}</div>
                    <div class="stat-label">Liters Water</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{int(carbon.get('car_miles_equivalent', 0)):,}</div>
                    <div class="stat-label">Car Miles Equiv.</div>
                </div>
            </div>

            <div class="insight-grid" style="margin-top: 1rem;">
                <div class="insight-card">
                    <div class="insight-title">Inference + Hardware</div>
                    <div class="insight-value">{carbon.get('operational_co2_kg', 0)} kg CO2</div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">Training (Amortized)</div>
                    <div class="insight-value">{carbon.get('training_co2_kg', 0)} kg CO2</div>
                </div>
            </div>

            <div class="stats-grid" style="margin-top: 1.5rem;">
                <div class="stat-card" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 2px solid #22c55e; grid-column: span 2;">
                    <div class="stat-value" style="color: #16a34a; font-size: 2.75rem;">${carbon.get('offset_cost_usd', 0):.2f}</div>
                    <div class="stat-label" style="color: #15803d; font-weight: 500;">Estimated Offset Cost</div>
                </div>
            </div>

            <div class="deep-insight" style="margin-top: 1.5rem; background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%); border-left: 3px solid #22c55e;">
                <h3 style="color: #16a34a;">How to Offset</h3>
                <p>To neutralize your Claude.ai carbon footprint, donate <span class="highlight" style="color: #16a34a;">${carbon.get('offset_cost_usd', 0):.2f}</span> to a quality offset provider: <a href="https://www.goldstandard.org/" target="_blank" style="color: var(--accent);">Gold Standard</a>, <a href="https://www.southpole.com/" target="_blank" style="color: var(--accent);">South Pole</a>, or <a href="https://www.cooleffect.org/" target="_blank" style="color: var(--accent);">Cool Effect</a>.</p>
            </div>

            <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 1rem; line-height: 1.5;">
                <em>Aggressive methodology for power users: 20 Wh/query (above 17 Wh extended thinking benchmark), ×1.3 PUE, ×1.5 hardware embodied, 0.45 kg CO2/kWh grid, training at 24g/query (6g base × 4 for reasoning overhead), water at 10 L/kWh (direct + indirect), $20/ton offset. Sources: <a href="https://arxiv.org/abs/2505.09598" target="_blank" style="color: var(--text-muted);">arxiv.org/abs/2505.09598</a>, <a href="https://www.eesi.org/articles/view/data-centers-and-water-consumption" target="_blank" style="color: var(--text-muted);">EESI</a>, <a href="https://spectrum.ieee.org/ai-water-usage" target="_blank" style="color: var(--text-muted);">IEEE Spectrum</a></em>
            </p>
        </section>

        <section class="section">
            <h2>What Your Conversations Reveal</h2>

            <div class="deep-insight">
                <h3>How You Use Claude: Thinking Out Loud</h3>
                <p>You asked "thoughts?" <span class="highlight">205 times</span> this year. That's your signature move - present something, get a reaction, refine. You use Claude less for research and more for <span class="highlight">processing</span>: working through pricing decisions, drafting emails, pressure-testing strategies. It's externalized thinking.</p>
            </div>

            <div class="deep-insight">
                <h3>Your Communication Style: Short Prompts, Long Threads</h3>
                <p><span class="highlight">80% of your messages</span> are under 50 words. You don't over-explain upfront - you share context, get a response, then steer with "tweak this" or "not quite." <span class="highlight">44 conversations</span> went past 20 messages this year. You're willing to iterate when it matters, but you don't waste words getting started.</p>
            </div>

            <div class="deep-insight">
                <h3>The Pattern: Drafting as Thinking</h3>
                <p>Most of your conversations aren't questions - they're <span class="highlight">working sessions</span>. You draft proposals, emails, and strategies in real-time rather than planning in isolation. You seem to think better when you have something concrete to react to and refine. The output is the thinking process.</p>
            </div>

            <div class="traits-section">
                <div class="traits-column">
                    <h3>Strengths</h3>
                    <ul class="traits-list">
                        <li>
                            <strong>Connecting Dots</strong>
                            <span>You pull from multiple domains in a single conversation - referencing Uber experience while discussing vermouth distribution, or applying startup thinking to parenting logistics. The cross-pollination seems natural to you.</span>
                        </li>
                        <li>
                            <strong>Bias Toward Action</strong>
                            <span>Your conversations show "here's a draft, let's improve it" rather than "help me plan this." You get something on paper quickly and iterate from there.</span>
                        </li>
                        <li>
                            <strong>Range</strong>
                            <span>In October alone, you went from hydrogen aircraft regulations to toddler Halloween costumes to vermouth tincture ratios. You don't seem to find this disorienting - you just switch contexts and go.</span>
                        </li>
                    </ul>
                </div>
                <div class="traits-column">
                    <h3>Growth Edges</h3>
                    <ul class="traits-list growth">
                        <li>
                            <strong>Over-Processing Big Decisions</strong>
                            <span>Small decisions, you move fast. But career moves, investments, and major life choices generate a lot of exploratory conversations. The thoroughness is useful, but sometimes it looks like delay.</span>
                        </li>
                        <li>
                            <strong>The "Thoughts?" Reflex</strong>
                            <span>205 times is a lot. Sometimes you probably already know the answer and are looking for confirmation. Worth noticing when you're seeking input vs. seeking permission.</span>
                        </li>
                        <li>
                            <strong>One More Iteration</strong>
                            <span>You refine drafts extensively - pricing models get multiple passes, emails get tweaked repeatedly. Usually this improves things, but occasionally you're polishing something that was ready three versions ago.</span>
                        </li>
                    </ul>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>How You Use AI</h2>

            <div class="deep-insight">
                <h3>Working Sessions, Not Search</h3>
                <p>Only about <span class="highlight">12% of your conversations</span> are pure information lookups. The rest are working sessions - drafting, strategizing, decision-making. You use Claude more like a colleague you can think out loud with than a reference tool.</p>
            </div>

            <div class="deep-insight">
                <h3>The Collaboration Pattern</h3>
                <p>You present work-in-progress, ask "thoughts?", incorporate feedback, repeat. It's efficient - you don't spend time explaining context that becomes obvious from the draft itself. You also aren't precious about your first attempts; you expect to iterate.</p>
            </div>
        </section>

        <section class="section">
            <h2>Your Year, Month by Month</h2>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">January - February</span>
                    <span class="month-theme">Aviation Focus</span>
                </div>
                <p>The year started with <strong>Solstice Aerospace</strong> front and center - 79 aviation-related mentions in February. Pitch deck work, cofounder search, hydrogen aircraft feasibility research. You were heads-down on one thing.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">March</span>
                    <span class="month-theme">Busy</span>
                </div>
                <p>55 conversations - your busiest early month. Aviation work continued (recruiting engineers, accident analysis, Pacific logistics), but life stuff appeared too: a child's stomach symptoms needed sorting out. The dual-track of work and parenting showed up clearly this month.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">April</span>
                    <span class="month-theme">New Threads</span>
                </div>
                <p>Aviation still central, but other things started appearing. First vermouth conversations. A traffic light alert device concept. Lost jewelry, insurance claims. Less singular focus, more variety creeping in.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">May - June</span>
                    <span class="month-theme">Personal Brand Work</span>
                </div>
                <p>Focus shifted to positioning yourself: superpower statements, bio drafts, website CSS. A lot of Ghost theme work. You were building the infrastructure for fractional consulting - how you'd present yourself to potential clients.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">July - August</span>
                    <span class="month-theme">Quiet Transition</span>
                </div>
                <p>Only 24 conversations across two months - noticeably slower. But the conversations that happened were about Duckbill marketing, consulting landing pages, new client work. A pivot was underway, just not a loud one.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">October</span>
                    <span class="month-theme">Everything at Once</span>
                </div>
                <p><strong>119 conversations</strong> - 5x your earlier monthly average. Duckbill work dominated (74 mentions), but you were also into fitness tracking, food logging apps, parenting stuff, vermouth experiments. A lot of plates spinning simultaneously.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">November</span>
                    <span class="month-theme">Peak Activity</span>
                </div>
                <p><strong>140 conversations</strong> - your highest month. Vermouth/Cartographer became a real focus (76 mentions). Conversations with the Four Sigmatic founder. Restaurant recommendations. Parenting. Style advice. Kid was sick. You were doing a lot of different things at once.</p>
            </div>

            <div class="month-narrative">
                <div class="month-header">
                    <span class="month-name">December</span>
                    <span class="month-theme">Winding Down</span>
                </div>
                <p>54 conversations - slower pace. Technical projects, partnership thinking, this Wrapped analysis. More reflection than execution. Setting up for next year rather than sprinting to finish this one.</p>
            </div>
        </section>

        <section class="section">
            <h2>The Year's Arc</h2>
            <div class="deep-insight">
                <h3>From Single Focus to Portfolio</h3>
                <p>You started 2025 focused on <span class="highlight">one venture</span> (Solstice). By fall, you were running <span class="highlight">multiple tracks</span>: Duckbill consulting, vermouth development, fitness optimization, parenting, personal projects. Whether this was intentional strategy or natural drift, it's where you ended up.</p>
            </div>

            <div class="deep-insight">
                <h3>What the Data Suggests</h3>
                <p>Your October-November activity spike (259 conversations in two months) wasn't followed by burnout - December was productive, just calmer. You seem to handle variety without it becoming chaos. The open question for 2026: is the multi-track approach sustainable long-term, or does something eventually need to become the main thing?</p>
            </div>
        </section>

        <footer>
            <p>Generated with Claude Code</p>
            <p>January - December 2025</p>
        </footer>
    </div>

    <script>
        // Chart.js configuration - matching alexpriest.com colors (light mode)
        Chart.defaults.color = '#57534e';
        Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.08)';

        // Months chart
        new Chart(document.getElementById('monthsChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(months_labels)},
                datasets: [{{
                    label: 'Conversations',
                    data: {json.dumps(months_values)},
                    backgroundColor: 'rgba(203, 97, 32, 0.85)',
                    borderColor: 'rgba(203, 97, 32, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(0, 0, 0, 0.06)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});

        // Hours chart
        new Chart(document.getElementById('hoursChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(hours_labels)},
                datasets: [{{
                    label: 'Messages',
                    data: {json.dumps(hours_values)},
                    fill: true,
                    backgroundColor: 'rgba(203, 97, 32, 0.12)',
                    borderColor: 'rgba(203, 97, 32, 1)',
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(203, 97, 32, 1)',
                    pointBorderColor: '#fff',
                    pointRadius: 3
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(0, 0, 0, 0.06)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    output_path = OUTPUT_DIR / "wrapped.html"
    with open(output_path, "w") as f:
        f.write(html)

    print(f"HTML report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_html()
