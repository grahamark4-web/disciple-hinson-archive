const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Node{constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];}append(...nodes){this.children.push(...nodes);}}
const context={document:{createElement:t=>new Node(t),createTextNode:t=>new Node('#text',t)}};vm.createContext(context);
const source=fs.readFileSync('dist/app.js','utf8');vm.runInContext(source.slice(source.indexOf('function el('),source.indexOf('function smallIcon(')),context);
const notes=context.episodeNotes({descriptionSegments:[{text:'Read this',href:'https://example.com/book'},{text:'https://example.com/a_(b). www.example.com.'},{text:'Unsafe',href:'javascript:alert(1)'}]});
const links=notes.children.filter(n=>n.tag==='a');assert.deepEqual(links.map(n=>n.href),['https://example.com/book','https://example.com/a_(b)','https://www.example.com']);assert.equal(links[0].textContent,'Read this');assert(links.every(n=>n.target==='_blank'&&n.rel==='noopener'));
const rows=JSON.parse(fs.readFileSync('dist/episodes.json')).sermons;assert(rows.every(e=>e.descriptionSegments.length||!e.description));assert(rows.some(e=>e.descriptionSegments.some(p=>p.href)));
console.log('Source anchor labels, plain URLs, punctuation and unsafe link rejection verified.');
