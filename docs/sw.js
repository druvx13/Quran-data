const BUILD="07fa17495a",DATAVER="1d7efc0fba",CORE="quran-core-"+BUILD,SAVED="quran-saved";
const PRE=["./","index.html","search.html","config.html","bookmarks.html","sources.html","license.html","download.html",
  "manifest.webmanifest","assets/style.css","assets/app.js","assets/catalog.js","assets/icon.svg"];
const EXT=/^(fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net)$/;
self.addEventListener("install",e=>{e.waitUntil(caches.open(CORE).then(c=>Promise.all(PRE.map(u=>c.add(u).catch(()=>{})))).then(()=>self.skipWaiting()));});
self.addEventListener("activate",e=>{e.waitUntil((async()=>{
  for(const k of await caches.keys())if(k.startsWith("quran-core-")&&k!==CORE)await caches.delete(k);
  try{const c=await caches.open(SAVED);for(const r of await c.keys()){const u=new URL(r.url);
    if(/\/data\//.test(u.pathname)&&u.searchParams.has("v")&&u.searchParams.get("v")!==DATAVER)await c.delete(r);}}catch{}
  await self.clients.claim();})());});
const keep=async(req,res)=>{try{if(res&&(res.ok||res.type==="opaque")){const c=await caches.open(SAVED);await c.put(req,res.clone());}}catch{}return res;};
const cacheFirst=async req=>{const m=await caches.match(req);if(m)return m;return keep(req,await fetch(req));};
const networkFirst=async req=>{try{return await keep(req,await fetch(req));}
  catch{const m=await caches.match(req,{ignoreSearch:true});if(m)return m;
    if(req.mode==="navigate"){const i=await caches.match("index.html");if(i)return i;}throw new Error("offline");}};
self.addEventListener("fetch",e=>{const r=e.request;if(r.method!=="GET")return;const u=new URL(r.url);
  if(u.origin!==location.origin){if(EXT.test(u.hostname))e.respondWith(cacheFirst(r).catch(()=>fetch(r)));return;}
  e.respondWith(/\/data\/|\/assets\/fonts\//.test(u.pathname)?cacheFirst(r):networkFirst(r));});
