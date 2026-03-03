"""
Regex Visualizer - DFA/NFA State Diagrams
==========================================
Module for visualizing Regular Expression behavior as State Diagrams.

Course: Theory of Computation
"""

import re
from typing import List, Dict, Tuple


class RegexVisualizer:
    """
    Class for visualizing Regex as Automata diagrams.
    Helps understand the connection between Regex and DFA/NFA.
    """
    
    @staticmethod
    def visualize_email_dfa():
        """
        Display DFA for Email Pattern.
        """
        diagram = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     DFA for Email Pattern Recognition                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Pattern: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}                        ║
║                                                                                ║
║  States:                                                                       ║
║  • q0 (Start)     : Initial state                                              ║
║  • q1 (Local)     : Reading local-part (before @)                              ║
║  • q2 (At)        : Found @ symbol                                             ║
║  • q3 (Domain)    : Reading domain name                                        ║
║  • q4 (Dot)       : Found dot before TLD                                       ║
║  • q5 (TLD1)      : Read first TLD character                                   ║
║  • q6 (Accept)    : Read 2nd+ TLD character (Final State)                      ║
║                                                                                ║
║  Transition Diagram:                                                           ║
║                                                                                ║
║         [a-zA-Z0-9._%+-]              [a-zA-Z0-9.-]           [a-zA-Z]         ║
║              ↺                             ↺                    ↺              ║
║              │                             │                    │              ║
║      ┌───────┴───────┐             ┌───────┴───────┐    ┌───────┴───────┐      ║
║      │               │      @      │               │ .  │               │      ║
║ ──▶ (q0) ────────▶ (q1) ────────▶ (q2) ────────▶ (q3)──▶(q4) ────────▶ (q5)    ║
║      │               │             │               │    │               │      ║
║      └───────────────┘             └───────────────┘    └───────┬───────┘      ║
║                                                                 │              ║
║                                                           [a-zA-Z]             ║
║                                                                 ▼              ║
║                                                          ╔═══════════╗         ║
║                                                          ║   ((q6))  ║         ║
║                                                          ║  Accept   ║         ║
║                                                          ╚═══════════╝         ║
║                                                                 ↺              ║
║                                                           [a-zA-Z]             ║
║                                                                                ║
║  Legend:                                                                       ║
║  • (qX)   = State                                                              ║
║  • ((qX)) = Final/Accepting State                                              ║
║  • ───▶   = Transition                                                         ║
║  • ↺      = Self-loop                                                          ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(diagram)
        
    @staticmethod
    def visualize_phone_dfa():
        """
        Display DFA for Phone Pattern.
        """
        diagram = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     DFA for Phone Number Pattern                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Pattern: 0[0-9]{1,2}[-.]?[0-9]{3}[-.]?[0-9]{4}                                ║
║  Example: 02-123-4567, 081-234-5678, 0812345678                                ║
║                                                                                ║
║  Simplified DFA:                                                               ║
║                                                                                ║
║      ┌─────┐  0   ┌─────┐ [0-9] ┌─────┐ [0-9] ┌─────┐ [-.]? ┌─────┐            ║
║ ──▶  │ q0  │ ───▶ │ q1  │ ────▶ │ q2  │ ────▶ │ q3  │ ────▶ │ q4  │            ║
║      └─────┘      └─────┘       └─────┘       └─────┘       └─────┘            ║
║                                                                 │              ║
║                                                            [0-9]{3}            ║
║                                                                 ▼              ║
║      ╔═════════╗  [0-9]{4}  ┌─────┐  [-.]?  ┌─────┐                            ║
║      ║  ((q7)) ║ ◀──────── │ q6  │ ◀────── │ q5  │                            ║
║      ║ Accept  ║           └─────┘         └─────┘                             ║
║      ╚═════════╝                                                               ║
║                                                                                ║
║  State Descriptions:                                                           ║
║  • q0: Start state                                                             ║
║  • q1: Read initial '0'                                                        ║
║  • q2: Read first digit of area code                                           ║
║  • q3: Read second digit of area code (optional for mobile)                    ║
║  • q4: Passed optional separator after area code                               ║
║  • q5: Read 3 digits of middle part                                            ║
║  • q6: Passed optional separator                                               ║
║  • q7: Read 4 digits of last part (Accept State)                               ║
║                                                                                ║
║  Note: [-.]? represents ε-transition in NFA (can skip separator)              ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(diagram)

    @staticmethod
    def visualize_url_dfa():
        """
        Display DFA for URL Pattern.
        """
        diagram = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           DFA for URL Pattern                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Pattern: https?://[a-zA-Z0-9.-]+(?:/[^\\s]*)?                                  ║
║  Example: https://example.com/path/to/page                                     ║
║                                                                                ║
║  Transition Diagram:                                                           ║
║                                                                                ║
║       h      t      t      p      s?     :      /      /                       ║
║  ──▶(q0)──▶(q1)──▶(q2)──▶(q3)──▶(q4)──▶(q5)──▶(q6)──▶(q7)                      ║
║                                                        │                       ║
║                                                   [a-zA-Z0-9]                  ║
║                                                        ▼                       ║
║                          [a-zA-Z0-9.-]              ┌─────┐                    ║
║                               ↺                     │ q8  │──────┐             ║
║                               │                     └─────┘      │             ║
║                               │                        │    [a-zA-Z0-9.-]      ║
║                               └────────────────────────┘         │             ║
║                                                                  │             ║
║                                                            /     │             ║
║                                                                  ▼             ║
║                                                           ╔═══════════╗        ║
║                                                           ║  ((q9))   ║        ║
║                                                           ║  Accept   ║        ║
║                                                           ╚═══════════╝        ║
║                                                                 ↺              ║
║                                                            [^\\s]*             ║
║                                                                                ║
║  Key Points:                                                                   ║
║  • 's?' in https means 's' is optional (alternation: http|https)               ║
║  • Domain allows [a-zA-Z0-9.-]+ (Kleene Plus)                                  ║
║  • Path is optional: (?:/[^\\s]*)?                                              ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(diagram)

    @staticmethod
    def visualize_ip_dfa():
        """
        Display DFA for IP Address Pattern.
        """
        diagram = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        DFA for IPv4 Address Pattern                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Pattern: \\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}                  ║
║           (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b                           ║
║                                                                                ║
║  Valid Range: 0.0.0.0 - 255.255.255.255                                        ║
║                                                                                ║
║  Octet Sub-DFA (repeated 4 times with dot separator):                          ║
║                                                                                ║
║                          ┌──────────────────────────────────────┐              ║
║                          │         Octet (0-255)                │              ║
║                          │                                      │              ║
║                     ┌────┴────┐                                 │              ║
║                     ▼         │                                 │              ║
║                 ┌───────┐     │ [0-9]                           │              ║
║            ──▶  │  q0   │─────┴─────────────────────────────────│──▶           ║
║                 └───┬───┘                                       │              ║
║                     │                                           │              ║
║           ┌─────────┼──────────┬────────────────┐              │              ║
║           │         │          │                │              │              ║
║        [0-1]       [2]      [3-9]            [0]              │              ║
║           │         │          │                │              │              ║
║           ▼         ▼          ▼                │              │              ║
║       ┌───────┐ ┌───────┐ ┌───────┐            │              │              ║
║       │  q1   │ │  q2   │ │  q3   │ ───────────┼──────────────┘              ║
║       └───┬───┘ └───┬───┘ └───────┘            │                             ║
║           │         │                          │                             ║
║       [0-9]     ┌───┴───┐                     │                              ║
║           │     │       │                      │                             ║
║           ▼  [0-4]   [5]                      │                              ║
║       ┌───────┐ │       │                      │                             ║
║       │  q4   │ ▼       ▼                      │                             ║
║       └───┬───┘ q5     q6                      │                             ║
║           │     │       │                      │                             ║
║       [0-9] [0-9]   [0-5]                     │                              ║
║           │     │       │                      │                             ║
║           └─────┴───────┴──────────────────────┘                             ║
║                          │                                                    ║
║                          ▼                                                    ║
║                     Accept (0-255)                                            ║
║                                                                                ║
║  Complete IP = Octet.Octet.Octet.Octet                                        ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(diagram)

    @staticmethod
    def show_thompson_construction():
        """
        Display Thompson's Construction principles.
        """
        explanation = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         Thompson's Construction                                ║
║              Converting Regular Expression to NFA                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Principle: Every Regular Expression can be converted to an NFA.               ║
║                                                                                ║
║  1. Base Case - Single Character (a):                                          ║
║     ┌───┐  a   ┌───┐                                                          ║
║     │ q0│ ───▶ │q1 │                                                          ║
║     └───┘      └───┘                                                          ║
║                                                                                ║
║  2. Concatenation (ab):                                                        ║
║     ┌───┐  a   ┌───┐  ε   ┌───┐  b   ┌───┐                                    ║
║     │q0 │ ───▶ │q1 │ ───▶ │q2 │ ───▶ │q3 │                                    ║
║     └───┘      └───┘      └───┘      └───┘                                    ║
║                                                                                ║
║  3. Alternation (a|b):                                                         ║
║                    ε   ┌───┐  a   ┌───┐  ε                                     ║
║               ┌──────▶ │q1 │ ───▶ │q2 │ ─────┐                                 ║
║     ┌───┐     │        └───┘      └───┘      │      ┌───┐                      ║
║     │q0 │ ────┤                              ├────▶ │q5 │                      ║
║     └───┘     │        ┌───┐  b   ┌───┐      │      └───┘                      ║
║               └──────▶ │q3 │ ───▶ │q4 │ ─────┘                                 ║
║                    ε   └───┘      └───┘  ε                                     ║
║                                                                                ║
║  4. Kleene Star (a*):                                                          ║
║                         ε                                                      ║
║                    ┌─────────────┐                                             ║
║                    │             │                                             ║
║     ┌───┐  ε   ┌───┴──┐  a   ┌───▼──┐  ε   ┌───┐                              ║
║     │q0 │ ───▶ │  q1  │ ───▶ │  q2  │ ───▶ │q3 │                              ║
║     └───┘      └──────┘      └──────┘      └───┘                              ║
║        │                                      ▲                                ║
║        └──────────────── ε ───────────────────┘                                ║
║                                                                                ║
║  5. Plus (a+):                                                                 ║
║                         ε                                                      ║
║                    ┌─────────────┐                                             ║
║                    │             │                                             ║
║     ┌───┐  ε   ┌───┴──┐  a   ┌───▼──┐  ε   ┌───┐                              ║
║     │q0 │ ───▶ │  q1  │ ───▶ │  q2  │ ───▶ │q3 │                              ║
║     └───┘      └──────┘      └──────┘      └───┘                              ║
║                                                                                ║
║  Note: ε = epsilon transition (can change state without reading input)         ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(explanation)

    @staticmethod
    def show_subset_construction():
        """
        Display Subset Construction (NFA to DFA) principles.
        """
        explanation = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          Subset Construction                                   ║
║                   Converting NFA to DFA                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Principle: Every NFA can be converted to an equivalent DFA.                   ║
║                                                                                ║
║  Algorithm:                                                                    ║
║  1. Start: DFA start state = ε-closure(NFA start state)                       ║
║  2. For each DFA state and input symbol:                                      ║
║     - Compute move(state, symbol)                                             ║
║     - Compute ε-closure of the result                                         ║
║     - Add new DFA state if not exists                                         ║
║  3. DFA accept states = states containing any NFA accept state                ║
║                                                                                ║
║  Example: NFA for (a|b)*                                                       ║
║                                                                                ║
║  NFA:                                                                          ║
║            ε   ┌───┐  a   ┌───┐  ε                                            ║
║       ┌──────▶ │ 1 │ ───▶ │ 2 │ ─────┐                                        ║
║       │    ε   └───┘      └───┘  ε   │                                        ║
║  ┌────┴───┐                          ▼  ┌───────┐                              ║
║  │   0    │ ◀──────────────────────────│   5   │                              ║
║  └────┬───┘          ε                  └───────┘                              ║
║       │    ε   ┌───┐  b   ┌───┐  ε   ▲                                        ║
║       └──────▶ │ 3 │ ───▶ │ 4 │ ─────┘                                        ║
║                └───┘      └───┘                                                ║
║                                                                                ║
║  Subset Construction:                                                          ║
║  ┌─────────────────┬─────────────────┬─────────────────┐                      ║
║  │   DFA State     │     a           │     b           │                      ║
║  ├─────────────────┼─────────────────┼─────────────────┤                      ║
║  │ A = {0,1,3,5}   │ B = {0,1,2,3,5} │ C = {0,1,3,4,5} │                      ║
║  │ B = {0,1,2,3,5} │ B = {0,1,2,3,5} │ C = {0,1,3,4,5} │                      ║
║  │ C = {0,1,3,4,5} │ B = {0,1,2,3,5} │ C = {0,1,3,4,5} │                      ║
║  └─────────────────┴─────────────────┴─────────────────┘                      ║
║                                                                                ║
║  Resulting DFA:                                                                ║
║              a,b        a                                                      ║
║               ↺        ┌───┐                                                   ║
║         ┌─────────┐    │   │                                                   ║
║    ──▶  │ A (start│ ───┴───▶ B ◀───┐                                          ║
║         │  accept)│           │    │ a                                         ║
║         └────┬────┘           │    │                                           ║
║              │ b              │ b  │                                           ║
║              │                ▼    │                                           ║
║              └─────────────▶  C ───┘                                           ║
║                               ↺ b                                              ║
║                                                                                ║
║  All states are accept states (contain state 5)                               ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(explanation)


class RegexTester:
    """
    Class for testing Regular Expressions.
    Shows step-by-step matching.
    """
    
    @staticmethod
    def test_pattern(pattern: str, test_strings: List[str]) -> None:
        """
        Test a pattern against multiple strings.
        """
        print(f"\n🔍 Testing Pattern: {pattern}")
        print("=" * 60)
        
        compiled = re.compile(pattern)
        
        for test_str in test_strings:
            match = compiled.search(test_str)
            if match:
                print(f"  ✅ '{test_str}'")
                print(f"     Match: '{match.group()}' at position {match.start()}-{match.end()}")
            else:
                print(f"  ❌ '{test_str}' - No match")
    
    @staticmethod
    def trace_email_match(email: str) -> None:
        """
        Show step-by-step email matching.
        """
        print(f"\n📧 Tracing Email Match: {email}")
        print("=" * 60)
        
        # Break down the email pattern
        local_part = r'[a-zA-Z0-9._%+-]+'
        at_symbol = r'@'
        domain = r'[a-zA-Z0-9.-]+'
        dot = r'\.'
        tld = r'[a-zA-Z]{2,}'
        
        patterns = [
            ("Local Part", local_part),
            ("@ Symbol", at_symbol),
            ("Domain", domain),
            ("Dot", dot),
            ("TLD", tld)
        ]
        
        pos = 0
        remaining = email
        
        for name, pattern in patterns:
            match = re.match(pattern, remaining)
            if match:
                matched = match.group()
                print(f"  State: {name}")
                print(f"    Pattern: {pattern}")
                print(f"    Matched: '{matched}'")
                print(f"    Remaining: '{remaining[len(matched):]}'")
                remaining = remaining[len(matched):]
                pos += len(matched)
                print()
            else:
                print(f"  ❌ Failed at {name}")
                print(f"    Pattern: {pattern}")
                print(f"    Remaining: '{remaining}'")
                return
        
        print(f"  ✅ Successfully matched entire email!")


def demo():
    """
    Demo function showing how to use RegexVisualizer.
    """
    print("\n" + "=" * 70)
    print("📊 Regex Pattern Visualizer Demo")
    print("=" * 70)
    
    viz = RegexVisualizer()
    tester = RegexTester()
    
    while True:
        print("\n" + "-" * 50)
        print("Select Visualization:")
        print("  1. Email DFA")
        print("  2. Phone Number DFA")
        print("  3. URL DFA")
        print("  4. IP Address DFA")
        print("  5. Thompson's Construction")
        print("  6. Subset Construction (NFA to DFA)")
        print("  7. Test Email Pattern")
        print("  8. Trace Email Match")
        print("  9. Exit")
        print("-" * 50)
        
        choice = input("Select (1-9): ").strip()
        
        if choice == '1':
            viz.visualize_email_dfa()
        elif choice == '2':
            viz.visualize_phone_dfa()
        elif choice == '3':
            viz.visualize_url_dfa()
        elif choice == '4':
            viz.visualize_ip_dfa()
        elif choice == '5':
            viz.show_thompson_construction()
        elif choice == '6':
            viz.show_subset_construction()
        elif choice == '7':
            test_emails = [
                "valid@example.com",
                "user.name+tag@domain.co.th",
                "invalid-email",
                "missing@tld",
                "test@sub.domain.com"
            ]
            tester.test_pattern(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', test_emails)
        elif choice == '8':
            email = input("Enter email to trace: ").strip()
            if email:
                tester.trace_email_match(email)
        elif choice == '9':
            break
        else:
            print("❌ Please select 1-9")


if __name__ == "__main__":
    demo()
