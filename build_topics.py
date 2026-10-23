"""Index specific episode subjects using weighted, boundary-aware metadata rules.
No transcript-derived claims: each topic is backed by title or episode notes.
"""
import json,re,pathlib,collections,unicodedata
ROOT=pathlib.Path(__file__).parent
vocab=json.loads((ROOT/'theme-vocabulary.json').read_text());data=json.loads((ROOT/'dist/episodes.json').read_text())
def norm(s):return unicodedata.normalize('NFKD',s).lower().replace('’',"'").replace('–','-').replace('—','-')
def sentences(s):return re.split(r'(?<=[.!?])\s+',norm(s))
freq=collections.Counter(x.strip() for e in data['sermons'] for x in set(sentences(e['description'])) if len(x)>50)
patterns={tag:re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(norm(x)) for x in set([tag,*terms]))+r')(?!\w)') for tag,terms in vocab.items()}
# Broad labels must not match a standalone incidental word or a series heading.
strict={'faith','work','service','peace','contentment','friendship','parenting and family'}
for tag in strict:patterns[tag]=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(norm(x)) for x in vocab[tag])+r')(?!\w)')
result={};report=[]
for e in data['sermons']:
 title=norm(e['title']);title=re.sub(r'statement of faith\s*article\s*\d+\s*[:\-]\s*','',title)
 description=' '.join(x for x in sentences(e['description']) if freq[x.strip()]<5)
 publisher=norm(' '.join(e['sourceTags']));scores={};evidence={}
 for tag,pat in patterns.items():
  tc=len(pat.findall(title));dc=len(pat.findall(description));pc=len(pat.findall(publisher))
  if tc or dc or pc:
   scores[tag]=tc*10+pc*8+min(dc,3)*2
   evidence[tag]={'title':bool(tc),'notes':bool(dc),'publisherTags':bool(pc)}
 # Keep direct subjects first; avoid filling short descriptions with numerous weak tags.
 tags=sorted(scores,key=lambda t:(-scores[t],t))[:8]
 result[e['id']]={'tags':tags,'source':'episode-metadata'}
 report.append({'id':e['id'],'title':e['title'],'themes':tags,'evidence':{t:evidence[t] for t in tags}})
(ROOT/'dist/episode-themes.json').write_text(json.dumps({'version':2,'method':'Weighted title, unique episode-note and publisher-tag subjects; repeated boilerplate excluded. No transcripts.','aliases':vocab,'sermons':result},ensure_ascii=False,separators=(',',':'))+'\n')
(ROOT/'theme-index-report.json').write_text(json.dumps({'episodes':len(result),'tagged':sum(bool(x['tags']) for x in result.values()),'episodesForReview':[r for r in report if not r['themes']],'evidence':report},ensure_ascii=False,indent=2)+'\n')
print('Subject-indexed episodes:',sum(bool(x['tags']) for x in result.values()),'of',len(result))
