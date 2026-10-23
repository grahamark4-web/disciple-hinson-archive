const headers={ 'X-Content-Type-Options':'nosniff', 'Cache-Control':'no-store' };
export default {
 async fetch(request,env){
  const url=new URL(request.url);
  if(!url.pathname.startsWith('/download/'))return env.ASSETS.fetch(request);
  if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405,headers:{...headers,Allow:'GET, HEAD'}});
  const id=url.pathname.slice('/download/'.length);
  if(!/^[a-zA-Z0-9_-]{1,80}$/.test(id))return new Response('Not found',{status:404,headers});
  const catalog=await env.ASSETS.fetch(new Request(new URL('/episodes.json',url)));
  if(!catalog.ok)return new Response('Catalog unavailable',{status:503,headers});
  const item=(await catalog.json()).sermons.find(e=>e.id===id);
  if(!item?.audio)return new Response('Not found',{status:404,headers});
  const source=new URL(item.audio);
  if(source.protocol!=='https:'||!['static1.squarespace.com','static.squarespace.com','static.squarespace-cdn.com'].includes(source.hostname))return new Response('Recording unavailable',{status:502,headers});
  const upstreamHeaders={};const range=request.headers.get('Range');if(range)upstreamHeaders.Range=range;
  let upstream;try{upstream=await fetch(source,{method:request.method,headers:upstreamHeaders,redirect:'manual'});}catch{return new Response('Recording temporarily unavailable',{status:502,headers});}
  if(![200,206,416].includes(upstream.status))return new Response('Recording temporarily unavailable',{status:502,headers});
  const out=new Headers(headers);for(const key of ['Content-Type','Content-Length','Content-Range','Accept-Ranges']){const value=upstream.headers.get(key);if(value)out.set(key,value);}
  const filename=item.title.replace(/[^a-zA-Z0-9 -]/g,'').trim().slice(0,100)||'Disciple-Hinson';
  out.set('Content-Disposition','attachment; filename="'+filename+'.mp3"');
  return new Response(request.method==='HEAD'?null:upstream.body,{status:upstream.status,headers:out});
 }
};
