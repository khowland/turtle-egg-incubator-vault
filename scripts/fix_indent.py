import sys

with open(r'c:\dev\projects\turtle-db\vault_views\3_Observations.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(108, 212):
    if lines[i].startswith('    '):
        lines[i] = lines[i][4:]

with open(r'c:\dev\projects\turtle-db\vault_views\3_Observations.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Indentation fixed.")
