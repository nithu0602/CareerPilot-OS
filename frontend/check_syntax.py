import re

with open('components/society-main.tsx') as f:
    content = f.read()

# Count JSX elements
open_tags = len(re.findall(r'<[a-zA-Z]', content))
close_tags = len(re.findall(r'</[a-zA-Z]', content))
self_closing = len(re.findall(r'/>', content))
print(f"Open JSX tags: {open_tags}")
print(f"Close JSX tags: {close_tags}")
print(f"Self-closing: {self_closing}")
print(f"Net: {open_tags - close_tags}")

# Check for unclosed template literals
backticks = content.count('`')
print(f"Backticks: {backticks} (should be even: {backticks % 2 == 0})")

# Check for unclosed JSX braces in expressions
# Count { and } outside of strings
code_no_strings = re.sub(r'"[^"]*"', '', content)
code_no_strings = re.sub(r"'[^']*'", '', code_no_strings)
open_braces = code_no_strings.count('{')
close_braces = code_no_strings.count('}')
print(f"Open braces (excl strings): {open_braces}")
print(f"Close braces (excl strings): {close_braces}")
