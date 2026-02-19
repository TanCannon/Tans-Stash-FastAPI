from bs4 import BeautifulSoup
import re

def slugify(text):
    """Convert heading text into a URL-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def generate_toc_and_clean_html(html_content):
    """
    Generates nested TOC from h2–h4 headings and adds safe IDs.
    Returns (cleaned_html, toc_tree)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    toc = []
    stack = [{'level': 1, 'children': toc}]  # root

    for heading in soup.find_all(['h2', 'h3', 'h4']):
        title = heading.get_text().strip()
        safe_id = slugify(title)
        heading['id'] = safe_id
        level = int(heading.name[1])

        node = {'title': title, 'id': safe_id, 'level': level, 'children': []}

        # Adjust nesting based on heading level
        while stack and level <= stack[-1]['level']:
            stack.pop()
        stack[-1]['children'].append(node)
        stack.append(node)

    return str(soup), toc
