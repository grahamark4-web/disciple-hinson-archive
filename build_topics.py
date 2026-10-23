import json,re,pathlib
ROOT=pathlib.Path(__file__).parent
vocab=json.loads((ROOT/'theme-vocabulary.json').read_text());data=json.loads((ROOT/'dist/episodes.json').read_text());result={}
for e in data['sermons']:
 text=' '.join([e['title'],e['description'],*e['series'],*e['sourceTags']]).lower().replace('’',"'")
 tags=[tag for tag,terms in vocab.items() if any(re.search(r'(?<!\w)'+re.escape(term.lower())+r'(?!\w)',text) for term in [tag,*terms])]
 result[e['id']]={'tags':tags,'source':'episode-metadata'}
(ROOT/'dist/episode-themes.json').write_text(json.dumps({'version':1,'method':'Themes inferred from titles, episode notes and publisher tags; no transcripts.','aliases':vocab,'sermons':result},ensure_ascii=False,separators=(',',':'))+'\n')
print('Themed episodes:',sum(bool(x['tags']) for x in result.values()),'of',len(result))
