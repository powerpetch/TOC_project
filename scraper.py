"""
Valorant Pro Players — Web Scraper
====================================
Scrapes professional Valorant player data from Liquipedia.net
using Python Regular Expressions (import re).

Course: Theory of Computation
Topic: Application of Regular Expression (Web Crawler)

This module demonstrates practical regex usage for data extraction,
directly applying DFA/NFA theory from the TOC course.
"""

import re
import json
import os
import time
import random
from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' library not installed. Run: pip install requests")
    exit(1)


# =========================================================================
#  REGEX PATTERN CONSTANTS — All patterns used for data extraction
# =========================================================================
class RegexPatterns:
    """
    Contains all compiled regular expression patterns used in the scraper.
    Each pattern can be described as a Finite Automaton (DFA/NFA).
    """

    # 1. Real name extraction from infobox
    REAL_NAME = re.compile(r'[Nn]ame[:\s]*</th>\s*<td[^>]*>([^<]+)</td>')

    # 2. Birth date in Month DD, YYYY format
    BIRTH_DATE = re.compile(r'[Bb]orn[:\s]*</th>\s*<td[^>]*>([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})')

    # 3. Nationality from flag link title attribute
    NATIONALITY = re.compile(r'[Nn]ationality[:\s]*</th>\s*<td[^>]*>.*?title="([^"]+)"')

    # 4. Current team from infobox link
    CURRENT_TEAM = re.compile(r'[Tt]eam[:\s]*</th>\s*<td[^>]*>.*?title="([^"]+)"')

    # 5. Player role / position
    ROLE = re.compile(r'(Duelist|Controller|Initiator|Sentinel|IGL|Flex|Entry)')

    # 6. Valorant agents from page links
    AGENTS = re.compile(
        r'title="(Jett|Raze|Reyna|Phoenix|Yoru|Neon|Iso|Clove|Omen|Brimstone|'
        r'Viper|Astra|Harbor|Sova|Breach|Skye|KAY/O|Fade|Gekko|'
        r'Chamber|Killjoy|Cypher|Sage|Deadlock)"'
    )

    # 7. Prize earnings in USD
    EARNINGS = re.compile(r'\$\s*([\d,]+(?:\.\d{2})?)')

    # 8. Twitter / X handle
    TWITTER = re.compile(r'(?:twitter|x)\.com/([A-Za-z0-9_]+)')

    # 9. Twitch channel name
    TWITCH = re.compile(r'twitch\.tv/([A-Za-z0-9_]+)')

    # 10. Years active range
    YEARS_ACTIVE = re.compile(r'(\d{4})\s*[-\u2013]\s*(\d{4}|[Pp]resent)')

    # 11. Player age
    AGE = re.compile(r'\(age[:\s]*(\d{1,2})\)')

    # 12. Player status (Active / Inactive / Retired)
    STATUS = re.compile(r'[Ss]tatus[:\s]*</th>\s*<td[^>]*>([^<]+)</td>')

    # Additional helper patterns
    PLAYER_LINK = re.compile(r'<a[^>]*href="(/valorant/[^"]*)"[^>]*title="([^"]+)"')
    INFOBOX_ROW = re.compile(r'<tr>\s*<th[^>]*>([^<]+)</th>\s*<td[^>]*>(.*?)</td>', re.DOTALL)
    HTML_TAGS = re.compile(r'<[^>]+>')
    WHITESPACE = re.compile(r'\s+')
    LIQUIPEDIA_URL = re.compile(r'href="(/valorant/[^"]+)"')
    IGN_FROM_TITLE = re.compile(r'^([^(]+?)(?:\s*\(.*\))?$')
    ROMANIZED = re.compile(r'romanized[:\s]*([^<\n]+)', re.IGNORECASE)


@dataclass
class ValorantPlayer:
    """Data model for a Valorant pro player."""
    ign: str
    real_name: Optional[str] = None
    birth_date: Optional[str] = None
    age: Optional[str] = None
    country: Optional[str] = None
    current_team: Optional[str] = None
    role: Optional[str] = None
    signature_agents: Optional[str] = None
    years_active_start: Optional[str] = None
    years_active_end: Optional[str] = None
    status: Optional[str] = None
    earnings: Optional[str] = None
    twitter: Optional[str] = None
    twitch: Optional[str] = None
    liquipedia_url: Optional[str] = None


class ValorantScraper:
    """
    Scrapes Valorant pro player data from Liquipedia.
    All data extraction uses Python's `re` library (Regular Expressions).
    """

    BASE_URL = "https://liquipedia.net"
    VALORANT_URL = f"{BASE_URL}/valorant"

    # Team pages to scrape for players
    TEAM_PAGES = [
        "/valorant/Sentinels", "/valorant/Cloud9", "/valorant/100_Thieves",
        "/valorant/NRG_Esports", "/valorant/Evil_Geniuses", "/valorant/LOUD",
        "/valorant/OpTic_Gaming", "/valorant/XSET", "/valorant/Version1",
        "/valorant/The_Guard", "/valorant/FunPlus_Phoenix", "/valorant/EDward_Gaming",
        "/valorant/DRX_(Korean_Team)", "/valorant/Paper_Rex", "/valorant/ZETA_DIVISION",
        "/valorant/FNATIC", "/valorant/Team_Liquid", "/valorant/Natus_Vincere",
        "/valorant/G2_Esports", "/valorant/KRÜ_Esports", "/valorant/Leviatán",
        "/valorant/FURIA_Esports", "/valorant/MIBR", "/valorant/T1_(Korean_Team)",
        "/valorant/Gen.G", "/valorant/Global_Esports", "/valorant/Rex_Regum_Qeon",
        "/valorant/Team_Secret", "/valorant/Talon_Esports", "/valorant/DetonatioN_FocusMe",
        "/valorant/Crazy_Raccoon", "/valorant/Bilibili_Gaming", "/valorant/Trace_Esports",
        "/valorant/Karmine_Corp", "/valorant/BBL_Esports", "/valorant/Team_Heretics",
        "/valorant/Team_Vitality", "/valorant/Gentle_Mates", "/valorant/Giants_Gaming",
        "/valorant/TSM", "/valorant/FaZe_Clan", "/valorant/Complexity_Gaming",
    ]

    HEADERS = {
        'User-Agent': 'TOC-Project-Scraper/1.0 (Educational; Theory of Computation)',
        'Accept': 'text/html',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.players: List[ValorantPlayer] = []
        self.seen_igns = set()

    def _fetch_page(self, url: str) -> str:
        """Fetch page HTML with rate limiting."""
        try:
            time.sleep(random.uniform(1.5, 3.0))  # Be respectful to Liquipedia
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"  [WARN] Failed to fetch {url}: {e}")
            return ""

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text using regex."""
        text = re.sub(RegexPatterns.HTML_TAGS, '', text)
        text = re.sub(RegexPatterns.WHITESPACE, ' ', text)
        return text.strip()

    def _extract_player_from_page(self, html: str, ign: str, page_url: str) -> Optional[ValorantPlayer]:
        """Extract player data from a player page using regex patterns."""
        player = ValorantPlayer(ign=ign)
        player.liquipedia_url = f"{self.BASE_URL}{page_url}"

        # 1. Real name — regex: [Nn]ame[:\s]*</th>\s*<td[^>]*>([^<]+)</td>
        match = re.search(RegexPatterns.REAL_NAME, html)
        if match:
            player.real_name = self._clean_html(match.group(1)).strip()

        # 2. Birth date — regex: [Bb]orn[:\s]*</th>\s*<td...>(...)</td>
        match = re.search(RegexPatterns.BIRTH_DATE, html)
        if match:
            player.birth_date = match.group(1).strip()

        # 3. Nationality — regex from flag title
        match = re.search(RegexPatterns.NATIONALITY, html)
        if match:
            player.country = match.group(1).strip()

        # 4. Current team
        match = re.search(RegexPatterns.CURRENT_TEAM, html)
        if match:
            player.current_team = match.group(1).strip()

        # 5. Role
        match = re.search(RegexPatterns.ROLE, html)
        if match:
            player.role = match.group(1)

        # 6. Signature agents — find all unique agent matches
        agents = re.findall(RegexPatterns.AGENTS, html)
        if agents:
            unique_agents = list(dict.fromkeys(agents))[:5]  # top 5 unique
            player.signature_agents = ', '.join(unique_agents)

        # 7. Earnings
        match = re.search(RegexPatterns.EARNINGS, html)
        if match:
            player.earnings = f"${match.group(1)}"

        # 8. Twitter / X
        match = re.search(RegexPatterns.TWITTER, html)
        if match:
            player.twitter = match.group(1)

        # 9. Twitch
        match = re.search(RegexPatterns.TWITCH, html)
        if match:
            player.twitch = match.group(1)

        # 10. Years active
        match = re.search(RegexPatterns.YEARS_ACTIVE, html)
        if match:
            player.years_active_start = match.group(1)
            player.years_active_end = match.group(2)

        # 11. Age
        match = re.search(RegexPatterns.AGE, html)
        if match:
            player.age = match.group(1)

        # 12. Status
        match = re.search(RegexPatterns.STATUS, html)
        if match:
            status_text = self._clean_html(match.group(1)).strip()
            if re.match(r'(?i)active', status_text):
                player.status = 'Active'
            elif re.match(r'(?i)inactive', status_text):
                player.status = 'Inactive'
            elif re.match(r'(?i)retire', status_text):
                player.status = 'Retired'
            else:
                player.status = status_text

        return player

    def _find_player_links(self, html: str) -> List[tuple]:
        """Extract player page links from a team page using regex."""
        return re.findall(RegexPatterns.PLAYER_LINK, html)

    def scrape_team(self, team_path: str):
        """Scrape all players from a team page."""
        url = f"{self.BASE_URL}{team_path}"
        team_name = team_path.split('/')[-1].replace('_', ' ')
        print(f"  Scraping team: {team_name}")

        html = self._fetch_page(url)
        if not html:
            return

        player_links = self._find_player_links(html)

        for path, title in player_links:
            # Use regex to extract IGN from title
            ign_match = re.match(RegexPatterns.IGN_FROM_TITLE, title)
            ign = ign_match.group(1).strip() if ign_match else title.strip()

            if ign in self.seen_igns or not ign:
                continue
            self.seen_igns.add(ign)

            player_html = self._fetch_page(f"{self.BASE_URL}{path}")
            if player_html:
                player = self._extract_player_from_page(player_html, ign, path)
                if player:
                    if not player.current_team:
                        player.current_team = team_name
                    self.players.append(player)
                    print(f"    ✓ {ign} ({player.country or '?'}, {player.role or '?'})")

    def scrape_all(self):
        """Scrape all teams."""
        print("=" * 55)
        print("  Valorant Pro Players — Web Scraper")
        print("=" * 55)
        print(f"  Teams to scrape: {len(self.TEAM_PAGES)}")
        print()

        for team_path in self.TEAM_PAGES:
            self.scrape_team(team_path)

        print()
        print(f"  Total players scraped: {len(self.players)}")
        print("=" * 55)

    def save_to_json(self, filepath: str):
        """Save scraped data to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data = {
            "metadata": {
                "source": "Liquipedia Valorant",
                "url": "https://liquipedia.net/valorant/",
                "total_players": len(self.players),
                "description": "Professional Valorant player data extracted using Python Regular Expressions",
                "library": "import re (Python re module)",
                "regex_patterns_used": 12,
            },
            "players": [asdict(p) for p in self.players]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  Saved to: {filepath}")


def main():
    """Main entry point for the scraper."""
    output_path = os.path.join(os.path.dirname(__file__), 'data', 'valorant_players.json')

    scraper = ValorantScraper()
    scraper.scrape_all()
    scraper.save_to_json(output_path)


if __name__ == '__main__':
    main()
