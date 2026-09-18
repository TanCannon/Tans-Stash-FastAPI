from bs4 import BeautifulSoup
import re

def slugify(text):
    """Convert heading text into a URL-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def generate_toc_and_clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    toc = []
    stack = [{'level': 1, 'children': toc}]

    for heading in soup.find_all(['h2', 'h3', 'h4']):
        title = heading.get_text(strip=True)

        # Skip empty headings
        if not title:
            continue

        safe_id = slugify(title)

        # Guarantee id exists
        if not safe_id:
            safe_id = "section"

        heading['id'] = safe_id
        level = int(heading.name[1])

        node = {'title': title, 'id': safe_id, 'level': level, 'children': []}

        while stack and level <= stack[-1]['level']:
            stack.pop()

        stack[-1]['children'].append(node)
        stack.append(node)

    return str(soup), toc