#!/usr/bin/env python3
"""
Claude 2025 Wrapped - Conversation Analysis Script
Analyzes exported Claude conversation data to generate Spotify Wrapped-style insights
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
import re
from pathlib import Path

# Paths
RAW_DIR = Path(__file__).parent / "raw-exports"
ANALYSIS_DIR = Path(__file__).parent / "analysis"
OUTPUT_DIR = Path(__file__).parent / "output"

# Ensure output directories exist
ANALYSIS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def load_conversations(year_filter=None):
    """Load and return conversations data, optionally filtered by year"""
    with open(RAW_DIR / "conversations.json", "r") as f:
        convos = json.load(f)

    if year_filter:
        convos = [c for c in convos if c.get("created_at", "").startswith(str(year_filter))]

    return convos


def load_projects():
    """Load and return projects data"""
    with open(RAW_DIR / "projects.json", "r") as f:
        return json.load(f)


def load_memories():
    """Load and return memories data"""
    with open(RAW_DIR / "memories.json", "r") as f:
        return json.load(f)


def count_words(text):
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())


def extract_hour(timestamp):
    """Extract hour from ISO timestamp"""
    if not timestamp:
        return None
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.hour
    except:
        return None


def extract_weekday(timestamp):
    """Extract weekday from ISO timestamp (0=Monday, 6=Sunday)"""
    if not timestamp:
        return None
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.weekday()
    except:
        return None


def analyze_conversations(convos):
    """Generate comprehensive conversation statistics"""
    stats = {
        "total_conversations": len(convos),
        "total_messages": 0,
        "human_messages": 0,
        "assistant_messages": 0,
        "human_words": 0,
        "assistant_words": 0,
        "conversations_by_month": Counter(),
        "messages_by_hour": Counter(),
        "messages_by_weekday": Counter(),
        "conversation_lengths": [],
        "longest_conversations": [],
        "conversation_names": [],
    }

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for convo in convos:
        # Track conversation name
        name = convo.get("name", "Untitled")
        created = convo.get("created_at", "")[:10]
        stats["conversation_names"].append({"name": name, "date": created})

        # Count by month
        if created:
            month = created[:7]
            stats["conversations_by_month"][month] += 1

        messages = convo.get("chat_messages", [])
        msg_count = len(messages)
        stats["total_messages"] += msg_count
        stats["conversation_lengths"].append(msg_count)

        human_words_in_convo = 0
        assistant_words_in_convo = 0

        for msg in messages:
            sender = msg.get("sender", "")
            text = msg.get("text", "")
            created_at = msg.get("created_at", "")

            word_count = count_words(text)

            if sender == "human":
                stats["human_messages"] += 1
                stats["human_words"] += word_count
                human_words_in_convo += word_count
            elif sender == "assistant":
                stats["assistant_messages"] += 1
                stats["assistant_words"] += word_count
                assistant_words_in_convo += word_count

            # Track by hour and weekday
            hour = extract_hour(created_at)
            if hour is not None:
                stats["messages_by_hour"][hour] += 1

            weekday = extract_weekday(created_at)
            if weekday is not None:
                stats["messages_by_weekday"][weekday_names[weekday]] += 1

        # Track longest conversations
        stats["longest_conversations"].append({
            "name": name,
            "messages": msg_count,
            "human_words": human_words_in_convo,
            "assistant_words": assistant_words_in_convo,
            "date": created
        })

    # Sort longest conversations
    stats["longest_conversations"].sort(key=lambda x: x["messages"], reverse=True)
    stats["longest_conversations"] = stats["longest_conversations"][:20]

    # Calculate averages
    if stats["total_conversations"] > 0:
        stats["avg_messages_per_convo"] = stats["total_messages"] / stats["total_conversations"]
        stats["avg_human_words_per_convo"] = stats["human_words"] / stats["total_conversations"]
        stats["avg_assistant_words_per_convo"] = stats["assistant_words"] / stats["total_conversations"]

    # Find peak hours and days
    if stats["messages_by_hour"]:
        stats["peak_hour"] = stats["messages_by_hour"].most_common(1)[0]
    if stats["messages_by_weekday"]:
        stats["peak_weekday"] = stats["messages_by_weekday"].most_common(1)[0]

    return stats


def extract_topics(convos):
    """Extract and categorize topics from conversation names"""
    topic_keywords = {
        "Work - Duckbill": ["duckbill", "gmv", "influencer", "tagline", "billboard", "marketing copy", "pricing strategy"],
        "Work - Solstice Aerospace": ["solstice", "aerospace", "hydrogen", "aircraft", "aviation", "airline", "fuel cell", "faa"],
        "Work - Consulting": ["consulting", "anthimeros", "fractional", "client", "proposal", "firesale", "focus"],
        "Vermouth/Cartographer": ["vermouth", "cartographer", "tincture", "botanical", "extraction", "wormwood", "gentian", "filtering"],
        "Personal Projects": ["ira", "penumbra", "book tracking", "raspberry pi", "traffic light", "tinsel tag"],
        "Style & Fashion": ["outfit", "styling", "shirt", "jeans", "sock", "shoes", "wardrobe", "wes anderson", "chore jacket"],
        "Health & Fitness": ["fitness", "cycling", "bike", "ride", "oura", "readiness", "recovery", "hrv", "supplement", "vitamin", "nutrition", "sleep"],
        "Food & Dining": ["restaurant", "dinner", "lunch", "coffee", "cocktail", "bar", "sushi", "austin", "brunch", "solo dining", "date night"],
        "Parenting & Family": ["toddler", "kid", "child", "parenting", "family", "school", "teacher", "swim", "separation anxiety", "sleep training", "meltdown"],
        "Technical/Coding": ["code", "python", "script", "api", "css", "ghost", "dataview", "obsidian", "google sheets", "spreadsheet", "formula"],
        "Finance & Business": ["salary", "budget", "investment", "tax", "insurance", "equity", "fundraising", "pitch", "investor"],
        "Philosophy & Learning": ["philosophy", "explain", "etymology", "meaning", "what is", "why", "history"],
        "Travel": ["trip", "paris", "france", "denver", "colorado", "san francisco"],
    }

    topic_counts = Counter()
    categorized_convos = defaultdict(list)

    for convo in convos:
        name = convo.get("name", "").lower()
        created = convo.get("created_at", "")[:10]
        matched = False

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    topic_counts[topic] += 1
                    categorized_convos[topic].append({"name": convo.get("name"), "date": created})
                    matched = True
                    break
            if matched:
                break

        if not matched:
            topic_counts["Other"] += 1
            categorized_convos["Other"].append({"name": convo.get("name"), "date": created})

    return {
        "topic_counts": dict(topic_counts.most_common()),
        "categorized_conversations": {k: v[:10] for k, v in categorized_convos.items()}  # Top 10 per category
    }


def analyze_projects(projects):
    """Analyze project usage"""
    project_stats = []
    for proj in projects:
        project_stats.append({
            "name": proj.get("name", "Unknown"),
            "description": proj.get("description", ""),
            "created_at": proj.get("created_at", "")[:10],
            "updated_at": proj.get("updated_at", "")[:10],
            "docs_count": len(proj.get("docs", [])),
        })
    return project_stats


def extract_time_patterns(stats):
    """Analyze time-based patterns for interesting insights"""
    patterns = {}

    # Determine actual peak period - handle both int and string keys
    hours = stats.get("messages_by_hour", {})

    def get_hour(h):
        return hours.get(h, 0) + hours.get(str(h), 0)

    morning = sum(get_hour(h) for h in range(5, 12))      # 5am-11am
    afternoon = sum(get_hour(h) for h in range(12, 18))   # 12pm-5pm
    evening = sum(get_hour(h) for h in range(18, 22))     # 6pm-9pm
    late_night = sum(get_hour(h) for h in [22, 23, 0, 1, 2, 3, 4])  # 10pm-4am

    periods = {
        "Morning Person (5am-noon)": morning,
        "Afternoon Worker (noon-6pm)": afternoon,
        "Evening Thinker (6pm-10pm)": evening,
        "Night Owl (10pm-4am)": late_night
    }
    patterns["chronotype"] = max(periods, key=periods.get)
    patterns["period_breakdown"] = {
        "morning": morning,
        "afternoon": afternoon,
        "evening": evening,
        "late_night": late_night
    }

    # Weekend warrior
    weekdays = stats.get("messages_by_weekday", {})
    weekend = weekdays.get("Saturday", 0) + weekdays.get("Sunday", 0)
    weekday_total = sum(v for k, v in weekdays.items() if k not in ["Saturday", "Sunday"])
    patterns["weekend_percentage"] = round(weekend / (weekend + weekday_total) * 100, 1) if (weekend + weekday_total) > 0 else 0

    return patterns


def find_interesting_conversations(convos):
    """Find notable/interesting conversation patterns"""
    interesting = {
        "philosophical": [],
        "quick_questions": [],
        "deep_dives": [],
        "personal_growth": [],
    }

    keywords_philosophical = ["philosophy", "meaning", "why", "existence", "purpose", "ethics"]
    keywords_growth = ["coaching", "therapy", "journal", "reflection", "goals", "habits"]

    for convo in convos:
        name = convo.get("name", "").lower()
        msg_count = len(convo.get("chat_messages", []))

        # Quick questions (2 messages = question + answer)
        if msg_count == 2:
            interesting["quick_questions"].append(convo.get("name", ""))

        # Deep dives (30+ messages)
        if msg_count >= 30:
            interesting["deep_dives"].append({
                "name": convo.get("name", ""),
                "messages": msg_count
            })

        # Philosophical conversations
        for kw in keywords_philosophical:
            if kw in name:
                interesting["philosophical"].append(convo.get("name", ""))
                break

        # Personal growth
        for kw in keywords_growth:
            if kw in name:
                interesting["personal_growth"].append(convo.get("name", ""))
                break

    return interesting


def generate_wrapped_stats(stats, topics, projects):
    """Generate Spotify Wrapped-style fun statistics"""
    wrapped = {
        "headline_stats": {
            "total_conversations": stats["total_conversations"],
            "total_messages": stats["total_messages"],
            "total_words_you_wrote": stats["human_words"],
            "total_words_claude_wrote": stats["assistant_words"],
            "total_words_exchanged": stats["human_words"] + stats["assistant_words"],
        },
        "fun_comparisons": {},
        "personality_insights": {},
        "peak_usage": {},
        "top_topics": [],
        "streaks_and_records": {},
        "time_patterns": {},
    }

    # Fun word comparisons
    total_words = stats["human_words"] + stats["assistant_words"]
    wrapped["fun_comparisons"]["equivalent_novels"] = round(total_words / 80000, 1)  # Avg novel is ~80k words
    wrapped["fun_comparisons"]["equivalent_tweets"] = round(stats["human_words"] / 280)  # 280 chars ≈ 50 words
    wrapped["fun_comparisons"]["pages_of_text"] = round(total_words / 300)  # ~300 words per page

    # More fun comparisons
    wrapped["fun_comparisons"]["hours_of_audiobook"] = round(total_words / 9000, 1)  # ~9000 words per hour at normal speed
    wrapped["fun_comparisons"]["the_great_gatsby_equivalents"] = round(total_words / 47094, 1)  # Great Gatsby is 47,094 words

    # Claude's verbosity ratio
    if stats["human_words"] > 0:
        wrapped["personality_insights"]["claude_verbosity_ratio"] = round(stats["assistant_words"] / stats["human_words"], 1)
        wrapped["personality_insights"]["your_communication_style"] = "Concise" if wrapped["personality_insights"]["claude_verbosity_ratio"] > 5 else "Conversational"

    # Average conversation depth
    wrapped["personality_insights"]["avg_messages_per_conversation"] = round(stats.get("avg_messages_per_convo", 0), 1)

    # Conversation length distribution
    lengths = stats.get("conversation_lengths", [])
    if lengths:
        quick_chats = sum(1 for l in lengths if l <= 4)
        medium_convos = sum(1 for l in lengths if 4 < l <= 20)
        deep_dives = sum(1 for l in lengths if l > 20)
        wrapped["personality_insights"]["quick_chats"] = quick_chats
        wrapped["personality_insights"]["medium_conversations"] = medium_convos
        wrapped["personality_insights"]["deep_dives"] = deep_dives

    # Peak usage times
    if "peak_hour" in stats:
        hour = stats["peak_hour"][0]
        hour_12 = hour % 12 or 12
        am_pm = "AM" if hour < 12 else "PM"
        wrapped["peak_usage"]["favorite_hour"] = f"{hour_12} {am_pm}"
        wrapped["peak_usage"]["favorite_hour_messages"] = stats["peak_hour"][1]

    if "peak_weekday" in stats:
        wrapped["peak_usage"]["favorite_day"] = stats["peak_weekday"][0]
        wrapped["peak_usage"]["favorite_day_messages"] = stats["peak_weekday"][1]

    # Time patterns
    wrapped["time_patterns"] = extract_time_patterns(stats)

    # Top topics (excluding "Other")
    filtered_topics = [(k, v) for k, v in topics["topic_counts"].items() if k != "Other"]
    wrapped["top_topics"] = filtered_topics[:7]
    wrapped["other_topics_count"] = topics["topic_counts"].get("Other", 0)

    # Busiest month
    if stats["conversations_by_month"]:
        busiest = stats["conversations_by_month"].most_common(1)[0]
        wrapped["streaks_and_records"]["busiest_month"] = busiest[0]
        wrapped["streaks_and_records"]["busiest_month_convos"] = busiest[1]

        # Growth trend
        sorted_months = sorted(stats["conversations_by_month"].items())
        if len(sorted_months) >= 2:
            first_half = sum(v for k, v in sorted_months[:len(sorted_months)//2])
            second_half = sum(v for k, v in sorted_months[len(sorted_months)//2:])
            if second_half > first_half:
                wrapped["streaks_and_records"]["usage_trend"] = "📈 Increasing over time"
            else:
                wrapped["streaks_and_records"]["usage_trend"] = "📉 Decreasing over time"

    # Longest conversation
    if stats["longest_conversations"]:
        longest = stats["longest_conversations"][0]
        wrapped["streaks_and_records"]["longest_conversation"] = longest["name"]
        wrapped["streaks_and_records"]["longest_conversation_messages"] = longest["messages"]
        wrapped["streaks_and_records"]["top_5_longest"] = stats["longest_conversations"][:5]

    # Project count
    wrapped["headline_stats"]["projects_used"] = len(projects)

    return wrapped


def main():
    print("🎁 Claude 2025 Wrapped - Analyzing your conversations...\n")

    # Load data - filter to 2025 only
    print("📂 Loading data (2025 only)...")
    convos = load_conversations(year_filter=2025)
    projects = load_projects()
    memories = load_memories()

    # Analyze
    print("📊 Analyzing conversations...")
    stats = analyze_conversations(convos)

    print("🏷️  Extracting topics...")
    topics = extract_topics(convos)

    print("📁 Analyzing projects...")
    project_stats = analyze_projects(projects)

    print("🎉 Generating Wrapped stats...")
    wrapped = generate_wrapped_stats(stats, topics, project_stats)

    # Save results
    print("\n💾 Saving analysis results...")

    with open(ANALYSIS_DIR / "conversation_stats.json", "w") as f:
        # Convert Counter objects to dicts for JSON serialization
        stats_serializable = stats.copy()
        stats_serializable["conversations_by_month"] = dict(stats["conversations_by_month"])
        stats_serializable["messages_by_hour"] = dict(stats["messages_by_hour"])
        stats_serializable["messages_by_weekday"] = dict(stats["messages_by_weekday"])
        json.dump(stats_serializable, f, indent=2)

    with open(ANALYSIS_DIR / "topics.json", "w") as f:
        json.dump(topics, f, indent=2)

    with open(ANALYSIS_DIR / "projects.json", "w") as f:
        json.dump(project_stats, f, indent=2)

    with open(ANALYSIS_DIR / "wrapped.json", "w") as f:
        json.dump(wrapped, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("🎊 YOUR CLAUDE 2025 WRAPPED 🎊")
    print("=" * 60)

    print(f"\n📈 THE BIG NUMBERS")
    print(f"   Conversations: {wrapped['headline_stats']['total_conversations']}")
    print(f"   Messages exchanged: {wrapped['headline_stats']['total_messages']}")
    print(f"   Words you wrote: {wrapped['headline_stats']['total_words_you_wrote']:,}")
    print(f"   Words Claude wrote: {wrapped['headline_stats']['total_words_claude_wrote']:,}")
    print(f"   Projects used: {wrapped['headline_stats']['projects_used']}")

    print(f"\n📚 THAT'S EQUIVALENT TO:")
    print(f"   📖 {wrapped['fun_comparisons']['equivalent_novels']} novels worth of text")
    print(f"   📄 {wrapped['fun_comparisons']['pages_of_text']:,} pages of writing")
    print(f"   🎧 {wrapped['fun_comparisons']['hours_of_audiobook']} hours of audiobook")
    print(f"   📕 {wrapped['fun_comparisons']['the_great_gatsby_equivalents']}x The Great Gatsby")

    print(f"\n🎯 YOUR TOP TOPICS:")
    for i, (topic, count) in enumerate(wrapped['top_topics'], 1):
        print(f"   {i}. {topic} ({count} conversations)")
    if wrapped.get("other_topics_count", 0) > 0:
        print(f"   + {wrapped['other_topics_count']} miscellaneous conversations")

    print(f"\n💬 CONVERSATION STYLE:")
    insights = wrapped.get("personality_insights", {})
    print(f"   Communication style: {insights.get('your_communication_style', 'N/A')}")
    print(f"   Quick Q&As (≤4 msgs): {insights.get('quick_chats', 0)}")
    print(f"   Medium conversations: {insights.get('medium_conversations', 0)}")
    print(f"   Deep dives (20+ msgs): {insights.get('deep_dives', 0)}")

    print(f"\n⏰ WHEN YOU CHAT:")
    if "favorite_hour" in wrapped["peak_usage"]:
        print(f"   Peak hour: {wrapped['peak_usage']['favorite_hour']} ({wrapped['peak_usage']['favorite_hour_messages']} messages)")
    if "favorite_day" in wrapped["peak_usage"]:
        print(f"   Peak day: {wrapped['peak_usage']['favorite_day']} ({wrapped['peak_usage']['favorite_day_messages']} messages)")
    time_patterns = wrapped.get("time_patterns", {})
    if "chronotype" in time_patterns:
        print(f"   Your chronotype: {time_patterns['chronotype']}")
    if "weekend_percentage" in time_patterns:
        print(f"   Weekend usage: {time_patterns['weekend_percentage']}%")

    print(f"\n🏆 RECORDS & TRENDS:")
    records = wrapped.get("streaks_and_records", {})
    if "busiest_month" in records:
        print(f"   Busiest month: {records['busiest_month']} ({records['busiest_month_convos']} conversations)")
    if "usage_trend" in records:
        print(f"   Usage trend: {records['usage_trend']}")
    if "longest_conversation" in records:
        name = records['longest_conversation'][:45]
        print(f"   Longest conversation: \"{name}...\"")
        print(f"      ({records['longest_conversation_messages']} messages)")

    print(f"\n🤖 VERBOSITY INSIGHT:")
    if "claude_verbosity_ratio" in insights:
        ratio = insights["claude_verbosity_ratio"]
        print(f"   For every word you wrote, Claude wrote {ratio} words back")
        if ratio > 6:
            print(f"   You're efficient - you get a lot of value per word!")
        elif ratio > 4:
            print(f"   You have great back-and-forth conversations")
        else:
            print(f"   You're a detailed communicator")

    print("\n" + "=" * 60)
    print(f"📁 Full analysis saved to: {ANALYSIS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
