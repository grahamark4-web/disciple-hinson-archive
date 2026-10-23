"""Refresh Disciple Hinson from its Squarespace collection, independently of sermons."""
import json,re,html,time,urllib.request,datetime,pathlib,collections
from html.parser import HTMLParser
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).parent;CACHE=ROOT/'.cache';CACHE.mkdir(exist_ok=True)
BASE='https://www.hinsonchurch.org';COLLECTION='/disciple-hinson-podcast'
class Extract(HTMLParser):
 def __init__(self):super().__init__();self.audio=[];self.text=[];self.skip=0;self.paragraph=0
 def handle_starttag(self,t,a):
  d=dict(a)
  if t in ('style','script'):self.skip+=1
  if t in ('p','li'):self.paragraph+=1
  if 'data-asset-url' in d or 'data-url' in d:
   u=d.get('data-asset-url') or d.get('data-url')
   if u and ('.mp3' in u or 'audio' in d.get('class','')):self.audio.append({'url':u,'author':d.get('data-author',''),'title':d.get('data-title',''),'duration':d.get('data-length-in-milli-seconds','')})
 def handle_endtag(self,t):
  if t in ('style','script'):self.skip=max(0,self.skip-1)
  if t in ('p','li'):self.paragraph=max(0,self.paragraph-1);self.text.append('\n')
 def handle_data(self,d):
  if not self.skip and self.paragraph:self.text.append(d)
def fetch(url,key):
 p=CACHE/(key+'.json')
 if p.exists() and time.time()-p.stat().st_mtime<300:return json.loads(p.read_text())
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HinsonPodcastArchive/1.0'}),timeout=40) as r:d=json.load(r)
   p.write_text(json.dumps(d));return d
  except Exception:
   if attempt==2:raise
   time.sleep(2)
def series(title):
 t=re.sub(r'^\d+\s*[-—–:]*\s*','',title).strip();low=t.lower()
 groups=[('part time theologians','Part Time Theologians'),('get to know','Get to Know'),('get to know','Get to Know'),('ministry update','Ministry Updates'),('statement of faith','Statement of Faith'),('covenant','Covenants'),('fellow workers','Fellow Workers'),('christian political engagement','Christian Political Engagement'),('corporate worship','Corporate Worship'),('adoniram judson','The Life and Ministry of Adoniram Judson'),('christ in the old testament','Christ in the Old Testament')]
 for k,v in groups:
  if k in low:return [v]
 if 'anxiety' in low:return ['Conversations on Anxiety']
 return []
def main():
 items={};offset=None;seen=set();page=0
 while True:
  url=BASE+COLLECTION+'?format=json'+('&offset='+str(offset) if offset else '')
  d=fetch(url,'page-'+str(offset or 'latest'));page+=1
  for x in d.get('items',[]):items[x['id']]=x
  print('Page',page,'episodes',len(items),flush=True)
  pg=d.get('pagination',{})
  if not pg.get('nextPage'):break
  offset=pg['nextPageOffset']
  if offset in seen:raise RuntimeError('Repeated pagination offset')
  seen.add(offset)
 rows=[];missing=[]
 for x in items.values():
  e=Extract();e.feed(x.get('body',''));audio=next((a for a in e.audio if a['url'].startswith('https://')),None)
  desc=html.unescape(re.sub(r'\s+',' ',' '.join(e.text))).strip();title=html.unescape(x['title']);speaker=html.unescape(audio['author']).strip() if audio else ''
  tags=x.get('tags',[]);cats=x.get('categories',[])
  row={'id':x['id'],'title':title,'date':datetime.datetime.fromtimestamp(x['publishOn']/1000,ZoneInfo('America/Los_Angeles')).date().isoformat(),'speaker':speaker,'description':desc,'passages':[],'books':[],'series':series(title),'url':BASE+x['fullUrl'] if x.get('fullUrl','').startswith('/') else BASE+COLLECTION+'/'+x['urlId'],'audio':audio['url'] if audio else None,'legacyAudio':False,'sourceTags':tags+cats}
  if not audio:missing.append({'id':x['id'],'title':title,'url':row['url']})
  rows.append(row)
 rows.sort(key=lambda x:(x['date'],x['title']),reverse=True)
 if len(rows)<200:raise RuntimeError('Incomplete episode catalog')
 old=ROOT/'dist/episodes.json'
 if old.exists() and len(rows)<len(json.loads(old.read_text())['sermons'])*.95:raise RuntimeError('Catalog unexpectedly shrank')
 old.write_text(json.dumps({'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':BASE+'/disciple-hinson-podcast-index','sermons':rows},ensure_ascii=False,separators=(',',':'))+'\n')
 (ROOT/'catalog-report.json').write_text(json.dumps({'episodes':len(rows),'audio':len(rows)-len(missing),'missingAudio':missing,'pages':page,'earliest':rows[-1]['date'],'latest':rows[0]['date']},indent=2)+'\n');print((ROOT/'catalog-report.json').read_text(),flush=True)
if __name__=='__main__':main()
