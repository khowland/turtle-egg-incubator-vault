import markdown2
from bs4 import BeautifulSoup

with open('./docs/user/OPERATOR_MANUAL.md', 'r', encoding='utf-8') as f:
    content = f.read()

html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
soup = BeautifulSoup(html, 'html.parser')

# Look for the section around 3.4
target = None
for el in soup.find_all(['h3', 'hr', 'p']):
    if el.name == 'h3' and '3.4' in el.get_text():
        target = el
        break

if target:
    print(f"Found 3.4: {target}")
    prev = target.find_previous()
    print(f"Previous element: {prev.name if prev else 'None'}")
else:
    print("Could not find 3.4")
