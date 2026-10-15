#!/usr/bin/env python3
"""Check generated pages for missing local files, anchor targets, and accessibility basics."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,path):
  super().__init__();self.path=path;self.ids=[];self.refs=[];self.h1=0;self.errors=[];self.feed(path.read_text())
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='img' and not a.get('alt'):self.errors.append('Image missing alt text')
  if tag=='iframe' and not a.get('title'):self.errors.append('Iframe missing title')
  for key in ['href','src']:
   if a.get(key):self.refs.append(a[key])
pages={p.resolve():Page(p) for p in [ROOT/'index.html',*sorted((ROOT/'projects').glob('*.html'))]}
errors=[];checked=set()
for path,page in pages.items():
 if page.h1!=1:errors.append(f'{path.name}: expected one h1')
 for key,count in Counter(page.ids).items():
  if count>1:errors.append(f'{path.name}: duplicate id {key}')
 errors.extend(f'{path.name}: {err}' for err in page.errors)
 for ref in page.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  target=(path.parent/unquote(u.path)).resolve() if u.path else path
  if not target.is_file():errors.append(f'{path.name}: missing {ref}');continue
  checked.add(target)
  if u.fragment and target.suffix=='.html':
   other=pages.get(target)
   if not other:other=Page(target)
   if unquote(u.fragment) not in other.ids:errors.append(f'{path.name}: missing anchor {ref}')
if errors:
 print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(pages)} pages, {len(checked)} local targets, unique IDs, valid anchors, and image descriptions.')
