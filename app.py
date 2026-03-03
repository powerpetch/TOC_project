"""
Flask Web Application - Valorant Pro Players Database
======================================================
Displays scraped Valorant pro player data on a web application.

Course: Theory of Computation
Topic: Application of Regular Expression (Web Crawler)
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import re

app = Flask(__name__)

# GitHub Repository URL - Replace with your repo URL
GITHUB_URL = "https://github.com/powerpetch05/TOC_project"

# Path to data file
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'valorant_players.json')


def load_players():
    """Load players from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('players', []), data.get('metadata', {})
    return [], {}


# =====================================================
# ALL REGEX PATTERNS USED IN THIS PROJECT
# =====================================================
REGEX_PATTERNS = {
    "1. Real Name": {
        "pattern": r'[Nn]ame[:\s]*</th>\s*<td[^>]*>([^<]+)</td>',
        "description": "Extracts the player's real name from the Liquipedia infobox table.",
        "example": "Name: Tyson Ngo → Tyson Ngo",
    },
    "2. Birth Date": {
        "pattern": r'[Bb]orn[:\s]*</th>\s*<td[^>]*>([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
        "description": "Extracts date of birth in 'Month DD, YYYY' format from the infobox.",
        "example": "Born: May 5, 2001 → May 5, 2001",
    },
    "3. Nationality": {
        "pattern": r'[Nn]ationality[:\s]*</th>\s*<td[^>]*>.*?title="([^"]+)"',
        "description": "Extracts the player's country/nationality from the flag title attribute.",
        "example": 'title="Canada" → Canada',
    },
    "4. Current Team": {
        "pattern": r'[Tt]eam[:\s]*</th>\s*<td[^>]*>.*?title="([^"]+)"',
        "description": "Extracts the player's current team from the infobox link title.",
        "example": "Team: Sentinels → Sentinels",
    },
    "5. Role / Position": {
        "pattern": r'(Duelist|Controller|Initiator|Sentinel|IGL|Flex|Entry)',
        "description": "Matches Valorant-specific roles using alternation.",
        "example": "Duelist",
    },
    "6. Agents Played": {
        "pattern": r'title="(Jett|Raze|Reyna|Phoenix|Yoru|Neon|Iso|Clove|Omen|Brimstone|Viper|Astra|Harbor|Sova|Breach|Skye|KAY/O|Fade|Gekko|Chamber|Killjoy|Cypher|Sage|Deadlock)"',
        "description": "Extracts Valorant agent names from page links/images using alternation of all agent names.",
        "example": 'title="Jett" → Jett',
    },
    "7. Prize Earnings": {
        "pattern": r'\$\s*([\d,]+(?:\.\d{2})?)',
        "description": "Extracts USD prize earnings, supporting comma separators and optional cents.",
        "example": "$523,456.00 → 523,456.00",
    },
    "8. Twitter / X Handle": {
        "pattern": r'(?:twitter|x)\.com/([A-Za-z0-9_]+)',
        "description": "Extracts the player's Twitter/X username from profile links.",
        "example": "x.com/TenZOfficial → TenZOfficial",
    },
    "9. Twitch Channel": {
        "pattern": r'twitch\.tv/([A-Za-z0-9_]+)',
        "description": "Extracts the Twitch channel name from stream links.",
        "example": "twitch.tv/tenz → tenz",
    },
    "10. Years Active": {
        "pattern": r'(\d{4})\s*[-\u2013]\s*(\d{4}|[Pp]resent)',
        "description": "Extracts career year range (start year and end year or 'present').",
        "example": "2020\u2013present → start=2020, end=present",
    },
    "11. Player Age": {
        "pattern": r'\(age[:\s]*(\d{1,2})\)',
        "description": "Extracts the player's age from parenthetical notation.",
        "example": "(age 23) → 23",
    },
    "12. Player Status": {
        "pattern": r'[Ss]tatus[:\s]*</th>\s*<td[^>]*>([^<]+)</td>',
        "description": "Extracts player status (Active / Inactive / Retired) from the infobox.",
        "example": "Status: Active → Active",
    },
}


@app.route('/')
def index():
    """Home page — shows all players in a searchable table"""
    players, metadata = load_players()

    total_players = len(players)
    countries = set(p.get('country') for p in players if p.get('country'))
    teams = set(p.get('current_team') for p in players if p.get('current_team'))
    roles = {}
    for p in players:
        r = p.get('role', 'Unknown')
        roles[r] = roles.get(r, 0) + 1

    stats = {
        'total_players': total_players,
        'total_countries': len(countries),
        'total_teams': len(teams),
        'regex_patterns_used': len(REGEX_PATTERNS),
        'roles': roles,
    }

    # Sorted lists for filter dropdowns
    countries_list = sorted(countries)
    teams_list = sorted(teams)

    return render_template('index.html',
                           players=players,
                           stats=stats,
                           metadata=metadata,
                           countries_list=countries_list,
                           teams_list=teams_list,
                           github_url=GITHUB_URL)


@app.route('/player/<int:player_id>')
def player_detail(player_id):
    """Individual player detail page"""
    players, _ = load_players()
    if 0 <= player_id < len(players):
        player = players[player_id]
        return render_template('player.html',
                               player=player,
                               player_id=player_id,
                               github_url=GITHUB_URL)
    return render_template('404.html', github_url=GITHUB_URL), 404


@app.route('/regex')
def regex_patterns():
    """Page showing all Regex patterns with DFA/NFA explanations"""
    players, _ = load_players()
    stats = {'total_players': len(players)}
    return render_template('regex.html',
                           patterns=REGEX_PATTERNS,
                           stats=stats,
                           github_url=GITHUB_URL)


@app.route('/regex-tester')
def regex_tester():
    """Interactive Regex Tester page — test patterns live against sample data"""
    return render_template('regex_tester.html',
                           patterns=REGEX_PATTERNS,
                           github_url=GITHUB_URL)


@app.route('/dashboard')
def dashboard():
    """Analytics Dashboard — charts and statistics"""
    players, metadata = load_players()

    # Basic stats
    countries = {}
    teams = {}
    roles = {}
    statuses = {}
    agents_count = {}
    total_agents = 0

    for p in players:
        c = p.get('country', 'Unknown')
        countries[c] = countries.get(c, 0) + 1

        t = p.get('current_team', 'Unknown')
        teams[t] = teams.get(t, 0) + 1

        # Parse role (may contain "IGL, Controller" etc.)
        role_str = p.get('role', 'Unknown')
        for r in re.split(r',\s*', role_str):
            r = r.strip()
            if r:
                roles[r] = roles.get(r, 0) + 1

        s = p.get('status', 'Unknown')
        statuses[s] = statuses.get(s, 0) + 1

        # Count agents
        sig_agents = p.get('signature_agents', '')
        if sig_agents:
            agent_list = [a.strip() for a in sig_agents.split(',')]
            total_agents += len(agent_list)
            for a in agent_list:
                if a:
                    agents_count[a] = agents_count.get(a, 0) + 1

    total_players = len(players)
    active_count = statuses.get('Active', 0)
    avg_agents = total_agents / total_players if total_players > 0 else 0

    stats = {
        'total_players': total_players,
        'total_countries': len(countries),
        'total_teams': len(teams),
        'regex_patterns_used': len(REGEX_PATTERNS),
        'active_count': active_count,
        'avg_agents': avg_agents,
    }

    # Build chart data
    role_data = sorted([{'role': k, 'count': v} for k, v in roles.items()],
                       key=lambda x: x['count'], reverse=True)
    country_data = sorted([{'country': k, 'count': v} for k, v in countries.items()],
                          key=lambda x: x['count'], reverse=True)[:10]
    team_data = sorted([{'team': k, 'count': v} for k, v in teams.items()],
                       key=lambda x: x['count'], reverse=True)[:15]
    status_data = [{'status': k, 'count': v} for k, v in statuses.items()]
    agent_data = sorted([{'agent': k, 'count': v} for k, v in agents_count.items()],
                        key=lambda x: x['count'], reverse=True)[:20]

    # Top teams with country diversity
    top_teams = []
    for team_name in sorted(teams, key=teams.get, reverse=True)[:10]:
        team_players = [p for p in players if p.get('current_team') == team_name]
        team_countries = len(set(p.get('country', '?') for p in team_players))
        top_teams.append({'name': team_name, 'count': teams[team_name], 'countries': team_countries})

    # Top countries with dominant role
    top_countries = []
    for country_name in sorted(countries, key=countries.get, reverse=True)[:10]:
        country_players = [p for p in players if p.get('country') == country_name]
        country_roles = {}
        for cp in country_players:
            cr = cp.get('role', 'Unknown')
            country_roles[cr] = country_roles.get(cr, 0) + 1
        top_role = max(country_roles, key=country_roles.get) if country_roles else 'N/A'
        top_countries.append({'name': country_name, 'count': countries[country_name], 'top_role': top_role})

    return render_template('dashboard.html',
                           stats=stats,
                           role_data=role_data,
                           country_data=country_data,
                           team_data=team_data,
                           status_data=status_data,
                           agent_data=agent_data,
                           top_teams=top_teams,
                           top_countries=top_countries,
                           github_url=GITHUB_URL)


@app.route('/about')
def about():
    """About page"""
    players, _ = load_players()
    stats = {'total_players': len(players)}
    return render_template('about.html', stats=stats, github_url=GITHUB_URL)


@app.route('/api/players')
def api_players():
    """REST API endpoint — returns player data as JSON"""
    players, metadata = load_players()
    search = request.args.get('search', '').lower()
    if search:
        players = [p for p in players if
                   search in p.get('ign', '').lower() or
                   search in (p.get('real_name') or '').lower() or
                   search in (p.get('current_team') or '').lower() or
                   search in (p.get('country') or '').lower()]
    return jsonify({'total': len(players), 'players': players, 'metadata': metadata})


@app.route('/api/stats')
def api_stats():
    """REST API endpoint — returns statistics"""
    players, metadata = load_players()
    countries, teams, roles = {}, {}, {}
    for p in players:
        c = p.get('country', 'Unknown'); countries[c] = countries.get(c, 0) + 1
        t = p.get('current_team', 'Unknown'); teams[t] = teams.get(t, 0) + 1
        r = p.get('role', 'Unknown'); roles[r] = roles.get(r, 0) + 1
    return jsonify({'total_players': len(players), 'countries': countries,
                    'teams': teams, 'roles': roles, 'metadata': metadata})


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', github_url=GITHUB_URL), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', github_url=GITHUB_URL), 500


if __name__ == '__main__':
    print()
    print("=" * 55)
    print("  VALORANT Pro Players — Web Application")
    print("=" * 55)
    print(f"  Server  : http://127.0.0.1:5000")
    print(f"  Data    : {DATA_FILE}")
    print(f"  GitHub  : {GITHUB_URL}")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    print()
    app.run(debug=True, host='0.0.0.0', port=5000)
