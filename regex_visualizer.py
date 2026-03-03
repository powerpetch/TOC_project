"""
Regex Visualizer
=================
Module for testing Regular Expression patterns.

Course: Theory of Computation
"""

import re
from typing import List


class RegexVisualizer:
    """
    Placeholder class for regex visualization.
    """
    pass


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
                print()
            else:
                print(f"  ❌ Failed at {name}")
                print(f"    Pattern: {pattern}")
                print(f"    Remaining: '{remaining}'")
                return
        
        print(f"  ✅ Successfully matched entire email!")


def demo():
    """
    Demo function showing how to use RegexTester.
    """
    print("\n" + "=" * 70)
    print("📊 Regex Pattern Tester Demo")
    print("=" * 70)
    
    tester = RegexTester()
    
    while True:
        print("\n" + "-" * 50)
        print("Select option:")
        print("  1. Test Email Pattern")
        print("  2. Trace Email Match")
        print("  3. Exit")
        print("-" * 50)
        
        choice = input("Select (1-3): ").strip()
        
        if choice == '1':
            test_emails = [
                "valid@example.com",
                "user.name+tag@domain.co.th",
                "invalid-email",
                "missing@tld",
                "test@sub.domain.com"
            ]
            tester.test_pattern(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', test_emails)
        elif choice == '2':
            email = input("Enter email to trace: ").strip()
            if email:
                tester.trace_email_match(email)
        elif choice == '3':
            break
        else:
            print("❌ Please select 1-3")


if __name__ == "__main__":
    demo()
