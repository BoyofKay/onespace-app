#!/usr/bin/env python3
"""One-time, reproducible generation of draft locale catalogues.

Public Google browser translation is used ONLY here during catalogue
generation, never during site builds or when site visitors open a page.
The translator has no access to account data: only authored public copy.
All output is stored as UTF-8 JSON in version control for review.
"""
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from full_localization import NEW_LANGS, GLOSSARY, catalog_for_pages, eligible

PAGES = [p.name for p in ROOT.glob('*.html') if p.name not in ('404.html', 'v4.html', 'v4-tutorial.html', 'founders-admin.html')]
CATALOG = catalog_for_pages(PAGES,ROOT)
print('CATALOG size:',len(CATALOG),'pages:',len(PAGES),flush=True)
out=ROOT/'content'/'translations'
out.mkdir(exist_ok=True)
(out/'source_catalog.json').write_text(json.dumps(CATALOG,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def batches(strings):
    buf=[]; length=0
    for text in strings:
        # Keep query URLs small enough for CDNs, and preserve item boundaries.
        cost=len(urllib.parse.quote(text))+15
        if buf and (len(buf)>=20 or length+cost>2700):
            yield buf
            buf=[];length=0
        buf.append(text);length+=cost
    if buf:yield buf

def translate_many(items,locale):
    query=[('client','dict-chrome-ex'),('sl','en'),('tl',locale)]
    query.extend(('q',x) for x in items)
    uri='https://translate.googleapis.com/translate_a/t?'+urllib.parse.urlencode(query)
    for attempt in range(9):
        try:
            req=urllib.request.Request(uri,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
            with urllib.request.urlopen(req,timeout=45) as r:
                payload=json.loads(r.read().decode('utf8'))
            if not isinstance(payload,list) or len(payload)!=len(items):
                raise RuntimeError(f'Unexpected batch output {len(payload) if isinstance(payload,list) else type(payload)} vs {len(items)}')
            return [str(x) for x in payload]
        except (urllib.error.URLError,TimeoutError,ValueError,RuntimeError) as exc:
            if attempt==8:raise RuntimeError(f'{locale}: translation batch never succeeded: {exc}') from exc
            print('Retry',locale,'items',len(items),'attempt',attempt+1,str(exc)[:120],flush=True)
            time.sleep(min(24,2**attempt+random.random()))
    raise RuntimeError('unreachable')

for locale in NEW_LANGS:
    target=out/(locale+'.json')
    data=json.loads(target.read_text(encoding='utf8')) if target.exists() else {}
    to_do=[s for s in CATALOG if s not in data and s not in GLOSSARY.get(locale,{})]
    work=list(batches(to_do))
    print(locale,'to translate:',len(to_do),'batches:',len(work),flush=True)
    for i,batch in enumerate(work):
        results=translate_many(batch,locale)
        for source,result in zip(batch,results):
            if not result.strip():
                # The public batch endpoint occasionally emits an empty item even
                # when the rest of the batch is valid. Retry that text alone.
                result=translate_many([source],locale)[0]
            if not result.strip():
                raise RuntimeError(f'Invalid {locale} translation for {source!r}: {result!r}')
            data[source]=result
        if i%20==0 or i+1==len(work):
            target.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
            print(locale,'done',i+1,'/',len(work),'entries',len(data),flush=True)
        time.sleep(.22)
    # Include all glossary entries explicitly for direct inspection and QA.
    data.update(GLOSSARY.get(locale,{}))
    remaining=[s for s in CATALOG if s not in data]
    if remaining:raise RuntimeError(f'{locale}: missing {len(remaining)} translation keys')
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(locale,'complete:',len(data),'strings',flush=True)
