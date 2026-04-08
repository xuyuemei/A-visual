import re

with open("src/pages/Main/Main.module.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if skip:
        if "}" in line:
            skip = False
        continue
    
    if ".textScoreSection .heroTextColumn" in line:
        skip = True
        if "  .textScoreSection" in line: # mobile
            new_lines.append("  .textScoreSection .heroTextColumn {\n")
            new_lines.append("    padding-left: calc(36px + 0.8cm);\n")
            new_lines.append("  }\n")
        else:
            new_lines.append(".textScoreSection .heroTextColumn {\n")
            new_lines.append("  padding-left: calc(72px + 0.8cm);\n")
            new_lines.append("}\n")
        continue

    new_lines.append(line)

with open("src/pages/Main/Main.module.css", "w", encoding="utf-8") as f:
    f.write("".join(new_lines))
