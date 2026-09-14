with open('components/society-main.tsx', encoding='utf-8') as f:
    content = f.read()

# Check if there are any \r characters
print(f"Contains CR: {chr(13) in content}")
# Check for null bytes
print(f"Contains null: {chr(0) in content}")

# Check for any control characters (except \n, \t)
for ch in content:
    if ord(ch) < 32 and ch not in ('\n', '\t'):
        i = content.index(ch)
        print(f"Control char U+{ord(ch):02X} at {i}: context={repr(content[max(0,i-5):i+5])}")
