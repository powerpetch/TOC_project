# Valorant Pro Players — Web Analyzer

A **Theory of Computation** project that demonstrates the practical application of **Regular Expressions** (DFA/NFA) through a web scraper and interactive web application for professional Valorant player data.

## 📋 Assignment Conditions

| # | Condition | Status |
|---|-----------|--------|
| 1 | Minimum **100 instances** in the dataset | ✅ **149 players** |
| 2 | Must use Python `import re` library | ✅ **12+ regex patterns** in scraper.py |
| 3 | At least **5 non-trivial** regex patterns | ✅ **12 regex patterns** |
| 4 | Web crawler to scrape portal websites | ✅ Scrapes **Liquipedia** |
| 5 | Display on web application | ✅ Flask web app |
| 6 | GitHub link on first page | ✅ In navigation bar |

## 🚀 Features

- **Web Scraper** — Scrapes Liquipedia using Python's `re` module (12 regex patterns)
- **149+ Player Profiles** — IGN, real name, country, team, role, agents, earnings, socials
- **Interactive Table** — Searchable/sortable player list powered by DataTables
- **Player Detail Pages** — Full profile view for each player
- **Regex Documentation** — All 12 patterns displayed on the web app
- **Analytics Dashboard** — Interactive charts and statistics
- **Interactive Regex Tester** — Test patterns live with sample data
- **REST API** — JSON endpoints at `/api/players` and `/api/stats`
- **Responsive Design** — Dark Valorant-themed UI with Bootstrap 5

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Core language, regex engine |
| Flask | Web framework |
| `import re` | Regular expression data extraction |
| Requests | HTTP client for web scraping |
| Bootstrap 5 | Frontend UI framework |
| DataTables | Interactive table (search, sort, pagination) |
| Chart.js | Data visualization |

## 📂 Project Structure

```
TOC_project/
├── app.py                  # Flask web application
├── scraper.py              # Web scraper with 12 regex patterns
├── web_analyzer.py         # Single-page web analyzer module
├── web_analyzer_gui.py     # GUI version of the web analyzer
├── regex_visualizer.py     # Regex DFA/NFA visualizer
├── requirements.txt        # Python dependencies
├── README.md
├── data/
│   └── valorant_players.json   # 149 player records
└── templates/
    ├── index.html          # Home page — player table
    ├── player.html         # Player detail page
    ├── regex.html          # Regex patterns page
    ├── regex_tester.html   # Interactive regex tester
    ├── dashboard.html      # Analytics dashboard
    ├── about.html          # About page
    ├── 404.html            # Error page
    └── 500.html            # Error page
```

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install flask requests
```

### 2. Run the Web Application

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### 3. Run the Scraper (optional)

```bash
python scraper.py
```

> **Note:** The scraper fetches live data from Liquipedia. Sample data is pre-included in `data/valorant_players.json`.

## 🔤 Regex Patterns Used

| # | Pattern | Purpose |
|---|---------|---------|
| 1 | `[Nn]ame[:\s]*</th>\s*<td[^>]*>([^<]+)</td>` | Extract real name |
| 2 | `[Bb]orn[:\s]*</th>\s*<td[^>]*>([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})` | Extract birth date |
| 3 | `[Nn]ationality[:\s]*</th>...title="([^"]+)"` | Extract country |
| 4 | `[Tt]eam[:\s]*</th>...title="([^"]+)"` | Extract team |
| 5 | `(Duelist\|Controller\|Initiator\|Sentinel\|IGL\|Flex\|Entry)` | Match role |
| 6 | `title="(Jett\|Raze\|...\|Deadlock)"` | Extract agents |
| 7 | `\$\s*([\d,]+(?:\.\d{2})?)` | Extract earnings |
| 8 | `(?:twitter\|x)\.com/([A-Za-z0-9_]+)` | Extract Twitter |
| 9 | `twitch\.tv/([A-Za-z0-9_]+)` | Extract Twitch |
| 10 | `(\d{4})\s*[-–]\s*(\d{4}\|[Pp]resent)` | Extract years active |
| 11 | `\(age[:\s]*(\d{1,2})\)` | Extract age |
| 12 | `[Ss]tatus[:\s]*</th>\s*<td[^>]*>([^<]+)</td>` | Extract status |

## 📊 Data Source

All player data is sourced from [Liquipedia Valorant](https://liquipedia.net/valorant/).

## 📄 License

This project is for educational purposes only — Theory of Computation course assignment.
