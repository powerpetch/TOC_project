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
GITHUB_URL = "https://github.com/powerpetch/TOC_project"

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
        "dfa_explanation": """
DFA States:
  q0 (start) → Accept 'N' or 'n'         [character class]
  q1 → Accept literal 'ame'
  q2 → Accept ':' or whitespace (0+)      [Kleene star on class]
  q3 → Accept '</th>' then whitespace
  q4 → Accept '<td' + any attributes '>'
  q5 → Capture group: ([^<]+) matches any text until '<'
  q6 (accept) → Accept '</td>'

Formal: [Nn] · ame · [:\\s]* · </th> · \\s* · <td[^>]*> · ([^<]+) · </td>
        """
    },
    "2. Birth Date": {
        "pattern": r'[Bb]orn[:\s]*</th>\s*<td[^>]*>([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
        "description": "Extracts date of birth in 'Month DD, YYYY' format from the infobox.",
        "example": "Born: May 5, 2001 → May 5, 2001",
        "dfa_explanation": """
DFA States:
  q0 (start) → Accept 'B' or 'b'         [character class]
  q1 → Accept literal 'orn'
  q2 → Accept HTML tags (non-capturing)
  q3 → Capture: [A-Z][a-z]+ matches month name (e.g., 'May')
  q4 → Capture: \\s+ then \\d{1,2} for day (1-2 digits)
  q5 → Capture: ',?' optional comma
  q6 → Capture: \\s+ then \\d{4} for year
  q7 (accept)

Uses: Character classes, quantifiers {1,2} and {4}, optional '?'
        """
    },
    "3. Nationality": {
        "pattern": r'[Nn]ationality[:\s]*</th>\s*<td[^>]*>.*?title="([^"]+)"',
        "description": "Extracts the player's country/nationality from the flag title attribute.",
        "example": 'title="Canada" → Canada',
        "dfa_explanation": """
NFA with epsilon-transitions:
  q0 → Accept 'Nationality' (case-insensitive start)
  q1 → Skip HTML via .*? (lazy quantifier — NFA epsilon-branch)
  q2 → Match literal 'title="'
  q3 → Capture group: [^"]+ matches all chars except quote
  q4 (accept) → Match closing '"'

Key: The lazy quantifier .*? creates an NFA with epsilon-transitions,
     allowing it to stop at the FIRST 'title="' match.
        """
    },
    "4. Current Team": {
        "pattern": r'[Tt]eam[:\s]*</th>\s*<td[^>]*>.*?title="([^"]+)"',
        "description": "Extracts the player's current team from the infobox link title.",
        "example": "Team: Sentinels → Sentinels",
        "dfa_explanation": """
Pattern structure:
  [Tt]eam     → Character class for case-insensitive 'T'
  [:\\s]*      → Zero or more colon or whitespace (Kleene star)
  </th>\\s*    → HTML end tag + optional whitespace
  <td[^>]*>   → Table data tag with any attributes
  .*?         → Lazy match (NFA: minimal characters)
  title="     → Literal anchor
  ([^"]+)     → Capture: negated class [^"] = any char except '"'
  "           → Closing quote
        """
    },
    "5. Role / Position": {
        "pattern": r'(Duelist|Controller|Initiator|Sentinel|IGL|Flex|Entry)',
        "description": "Matches Valorant-specific roles using alternation.",
        "example": "Duelist",
        "dfa_explanation": """
Pure Alternation (Union):
  This regex is a union of 7 strings → can be converted to a DFA
  with 7 branches from the start state:

  q0 → 'D' → q1 → 'u' → q2 → ... → 'Duelist'    → qACC
  q0 → 'C' → q8 → 'o' → q9 → ... → 'Controller'  → qACC
  q0 → 'I' → q18 → 'n' → ... → 'Initiator'        → qACC
  q0 → 'S' → q27 → 'e' → ... → 'Sentinel'         → qACC
  q0 → 'I' → q34 → 'G' → 'L' → 'IGL'             → qACC
  q0 → 'F' → q37 → 'l' → ... → 'Flex'             → qACC
  q0 → 'E' → q41 → 'n' → ... → 'Entry'            → qACC

Each branch is a linear sequence of states.
        """
    },
    "6. Agents Played": {
        "pattern": r'title="(Jett|Raze|Reyna|Phoenix|Yoru|Neon|Iso|Clove|Omen|Brimstone|Viper|Astra|Harbor|Sova|Breach|Skye|KAY/O|Fade|Gekko|Chamber|Killjoy|Cypher|Sage|Deadlock)"',
        "description": "Extracts Valorant agent names from page links/images using alternation of all agent names.",
        "example": 'title="Jett" → Jett',
        "dfa_explanation": """
Large alternation with literal prefix:
  1. Match literal: title="
  2. Alternation of 24 agent names (NFA with 24 epsilon-branches)
  3. Match literal: "

NFA → DFA conversion: Thompson's construction creates an NFA,
then subset construction produces an equivalent DFA.
The DFA shares prefix states (e.g., 'C' branches to both
'Chamber', 'Clove', 'Cypher').
        """
    },
    "7. Prize Earnings": {
        "pattern": r'\$\s*([\d,]+(?:\.\d{2})?)',
        "description": "Extracts USD prize earnings, supporting comma separators and optional cents.",
        "example": "$523,456.00 → 523,456.00",
        "dfa_explanation": """
Pattern breakdown:
  \\$         → Escaped literal dollar sign
  \\s*        → Zero or more whitespace (Kleene star)
  [\\d,]+     → One or more digits or commas (character class + Kleene plus)
  (?:        → Non-capturing group start
    \\.\\d{2}  → Literal dot + exactly 2 digits
  )?         → End non-capturing group, optional (?)

DFA: q0 →'$'→ q1 →[\\s]*→ q2 →[\\d,]+→ q3 →('.'→ q4 →\\d{2}→ q5) or → q5(acc)
        """
    },
    "8. Twitter / X Handle": {
        "pattern": r'(?:twitter|x)\.com/([A-Za-z0-9_]+)',
        "description": "Extracts the player's Twitter/X username from profile links.",
        "example": "x.com/TenZOfficial → TenZOfficial",
        "dfa_explanation": """
NFA with alternation:
  (?:twitter|x)  → Non-capturing group with alternation
                    NFA: epsilon → 'twitter' or epsilon → 'x'
  \\.com/         → Literal '.com/' (dot is escaped)
  ([A-Za-z0-9_]+) → Capturing group: character class with
                     uppercase, lowercase, digits, underscore
                     Kleene plus (+) = one or more

Supports both legacy twitter.com and new x.com URLs.
        """
    },
    "9. Twitch Channel": {
        "pattern": r'twitch\.tv/([A-Za-z0-9_]+)',
        "description": "Extracts the Twitch channel name from stream links.",
        "example": "twitch.tv/tenz → tenz",
        "dfa_explanation": """
Linear DFA:
  q0 → 't' → q1 → 'w' → q2 → 'i' → q3 → 't' → q4 → 'c' → q5
  → 'h' → q6 → '.' → q7 → 't' → q8 → 'v' → q9 → '/' → q10
  → [A-Za-z0-9_]+ → q11 (accept, loop on valid chars)

The escaped dot \\. ensures we match literal '.' not any character.
        """
    },
    "10. Years Active": {
        "pattern": r'(\d{4})\s*[-\u2013]\s*(\d{4}|[Pp]resent)',
        "description": "Extracts career year range (start year and end year or 'present').",
        "example": "2020\u2013present → start=2020, end=present",
        "dfa_explanation": """
Two capturing groups:
  Group 1: (\\d{4})     → Exactly 4 digits (start year)
  \\s*[-–]\\s*           → Optional whitespace + hyphen or en-dash + optional whitespace
  Group 2: (\\d{4}|[Pp]resent)
           → Alternation: 4 digits OR the word 'present' (case-insensitive P)

DFA: q0 →\\d{4}→ q1 →[-–]→ q2 → branch:
     q2 →\\d{4}→ q3(acc)
     q2 →[Pp]resent→ q3(acc)
        """
    },
    "11. Player Age": {
        "pattern": r'\(age[:\s]*(\d{1,2})\)',
        "description": "Extracts the player's age from parenthetical notation.",
        "example": "(age 23) → 23",
        "dfa_explanation": """
Linear DFA with bounded repetition:
  q0 → '(' → q1 → 'a' → q2 → 'g' → q3 → 'e' → q4
  → [:\\s]* → q5 (Kleene star on colon/space)
  → (\\d{1,2}) → q6 (capture 1 or 2 digits)
  → ')' → q7 (accept)

The quantifier {1,2} creates a bounded loop:
accept after 1 digit, continue to 2nd digit if present.
        """
    },
    "12. Player Status": {
        "pattern": r'[Ss]tatus[:\s]*</th>\s*<td[^>]*>([^<]+)</td>',
        "description": "Extracts player status (Active / Inactive / Retired) from the infobox.",
        "example": "Status: Active → Active",
        "dfa_explanation": """
HTML table row pattern:
  [Ss]tatus   → Character class for 'S'/'s' + literal 'tatus'
  [:\\s]*      → Optional colon and whitespace
  </th>\\s*   → End of header cell + whitespace
  <td[^>]*>   → Data cell with any attributes
  ([^<]+)     → Capture: all text until next HTML tag
  </td>       → End of data cell

Negated class [^<] means: any character EXCEPT '<'.
This prevents matching across HTML tag boundaries.
        """
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
