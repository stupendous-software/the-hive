import sys
sys.path.insert(0, '/a0/usr/workdir/web-scraper/scripts')
import scraper
from bs4 import BeautifulSoup
soup = scraper.scrape_url('https://www.waheagle.com/')
if not soup:
    print('Failed to fetch')
    sys.exit(1)

print('=== Sheriff headings ===')
for h in soup.find_all(['h2','h3']):
    txt = h.get_text().strip().lower()
    if 'sheriff' in txt:
        print(f"{h.name}: {h.get_text().strip()}")
        parent = h.find_parent(['div','section','article','aside'])
        print(f"  Parent: {parent.name if parent else 'None'} classes={parent.get('class') if parent else ''}")
        sib = h.find_next_sibling()
        siblings = []
        for i in range(5):
            if not sib or sib.name in ['h1','h2','h3','h4','h5','h6']:
                break
            siblings.append(sib.name)
            sib = sib.find_next_sibling()
        print(f"  Next siblings: {siblings}")

print('\n=== Article href issues ===')
hrefs = [a['href'] for a in soup.find_all('a', href=True) if '/story/' in a['href']]
print(f"Total hrefs containing /story/: {len(hrefs)}")
for i, h in enumerate(hrefs[:3]):
    print(f"{i}: {h}")
    # Show if it contains double base
    if 'HTTPS://' in h or h.count('http') > 1:
        print('   -> contains duplicate or uppercase scheme')
