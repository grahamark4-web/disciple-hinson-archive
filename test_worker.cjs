const assert=require('assert/strict');
(async()=>{
 const worker=(await import('./worker.mjs')).default;
 const catalog={sermons:[{id:'known',title:'Episode: A test',audio:'https://static1.squarespace.com/audio/test.mp3'},{id:'bad',title:'Bad',audio:'https://example.com/private'}]};
 const env={ASSETS:{fetch:async r=>new URL(r.url).pathname==='/episodes.json'?Response.json(catalog):new Response('static')}};
 const realFetch=global.fetch;let sent;
 global.fetch=async(u,opts)=>{sent={u:String(u),opts};return new Response('audio',{status:206,headers:{'Content-Range':'bytes 0-4/100','Content-Type':'audio/mpeg','Set-Cookie':'ignore=1'}})};
 assert.equal(await (await worker.fetch(new Request('https://app.test/'),env)).text(),'static');
 assert.equal((await worker.fetch(new Request('https://app.test/download/missing'),env)).status,404);
 assert.equal((await worker.fetch(new Request('https://app.test/download/known',{method:'POST'}),env)).status,405);
 assert.equal((await worker.fetch(new Request('https://app.test/download/bad'),env)).status,502);
 const r=await worker.fetch(new Request('https://app.test/download/known',{headers:{Range:'bytes=0-4'}}),env);
 assert.equal(r.status,206);assert.equal(sent.opts.headers.Range,'bytes=0-4');assert.equal(sent.opts.redirect,'manual');assert.match(r.headers.get('content-disposition'),/^attachment;/);assert.equal(r.headers.get('set-cookie'),null);assert.equal(await r.text(),'audio');
 global.fetch=realFetch;console.log('Static routing, allowlisted downloads, byte ranges and download headers passed.');
})().catch(e=>{console.error(e);process.exit(1)});
