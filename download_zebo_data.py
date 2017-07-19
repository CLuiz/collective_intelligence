from bs4 import BeautifulSoup
import requests
import re


chare = re.compile(r'[!-\.$]')
item_owners = {}

# Words to Remove
dropwords = 'a new some more my own the many other another'.split()

current_user = 0
for i in range(1, 51):
    r = (requests.get(f'http://member.zebo.com/Main?event_key=USERSEARCH&wiowiw=wi&keyword=car&page={i}'))
    soup = BeautifulSoup(r.text)
    for td in soup('td'):
        # Find table cells of bgverdanasmall class
        if('class' in dict(td.attrs) and td['class'] == 'bgverdanasmall'):
            items = [re.sub(chare, '', a.contents[0].lower()).strip()
                     for a in td('a')]
            for item in items:
                # Remove extra words
                txt = ' '.join([t for t in item.split() if t not in dropwords])
                if len(txt) < 2:
                    continue
                item_owners.setdefault(txt, {})
                item_owners[txt][current_user] = 1
            current_user += 1

with open('zebo.txt', 'w') as f:
    f.write('Item')
    f.write('\n')
    for item, owners in item_owners.items():
        if len(owners) > 10:
            f.write(item)
            for user in range(0, current_user):
                if user in owners:
                    f.write('\t1')
                else:
                    f.write('\t0')
            f.write('\n')
