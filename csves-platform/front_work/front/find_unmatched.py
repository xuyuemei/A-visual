def find_unmatched_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    stack = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for char in line:
            if char == '{':
                stack.append(i + 1)
            elif char == '}':
                if not stack:
                    print(f"Unmatched closing brace at line {i + 1}: {line}")
                else:
                    stack.pop()
    if stack:
        print("Unmatched opening braces at lines:", stack)
find_unmatched_braces("src/pages/Main/Main.module.css")
