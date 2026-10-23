const fs=require('fs'),S=require('./dist/search.js'),data=JSON.parse(fs.readFileSync('dist/episodes.json'));
const books=S.books.map(b=>b.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).sort((a,b)=>b.length-a.length).join('|');
const refs=new RegExp('\\b('+books+'|Psalm)\\s+\\d+(?:\\s*:\\s*\\d+)?(?:\\s*[-–]\\s*\\d+(?:\\s*:\\s*\\d+)?)?','gi');
const aliases={'Dan Schreiner':'Daniel Schreiner','TML':'Michael Lawrence','PK':'Paul Kim','PK Paul Kim':'Paul Kim','Mark VonWald':'Mark Von Wald','Mark Wiliams':'Mark Williams','Jim Everden':'Jim Evernden'};
for(const e of data.sermons){
 e.speaker=e.speaker.replace(/\s+/g,' ').replace(/,\s*$/,'').trim();
 e.speakers=[...new Set(e.speaker.split(/,|\s+and\s+|\s*&\s*|\s+with\s+/i).map(x=>x.replace(/^and\s+/i,'').replace(/^Dr\.\s*/,'').replace(/\s*\([^)]*\)/g,'').trim()).filter(Boolean).map(x=>aliases[x]||x))];
 e.passages=[...new Set((e.title+' '+e.description).match(refs)||[])].map(reference=>({book:S.parse(reference)?.book,reference})).filter(p=>p.book);
 e.books=[...new Set(e.passages.map(p=>p.book))];
}
fs.writeFileSync('dist/episodes.json',JSON.stringify(data)+'\n');console.log('Scripture citations:',data.sermons.filter(e=>e.passages.length).length,'episodes; individual speaker filters prepared.');
