(()=>{
"use strict";
const C=window.QURAN_CATALOG||{suras:[],tr:[],defaults:{},audio:"",range:[1,114]};
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const pad=n=>String(n).padStart(3,"0");
const h=(tag,attrs={},...kids)=>{const e=document.createElement(tag);
  for(const[k,v]of Object.entries(attrs)){if(k==="text")e.textContent=v;else if(k==="html")e.innerHTML=v;
    else if(v===true)e.setAttribute(k,"");else if(v!==false&&v!=null)e.setAttribute(k,v);}
  kids.flat().forEach(c=>c!=null&&c!==false&&e.append(c));return e;};
const store={
  get(k,d){try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v);}catch{return d;}},
  set(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true;}catch{return false;}},
  del(k){try{localStorage.removeItem(k);}catch{}}};
const ORD=Object.fromEntries(C.tr.map((t,i)=>[t.id,i]));
const sname=s=>C.suras[s-1]?C.suras[s-1].name:"Surah "+s;
const ago=t=>{const m=Math.round((Date.now()-t)/6e4);return m<1?"just now":m<60?m+" min ago":m<1440?Math.round(m/60)+" h ago":Math.round(m/1440)+" d ago";};

/* ---------- preferences ---------- */
let prefs=store.get("quran-cf",{});if(!prefs||typeof prefs!=="object"||Array.isArray(prefs))prefs={};
const isOn=id=>Object.prototype.hasOwnProperty.call(prefs,id)?!!prefs[id]:!!C.defaults[id];
const setOn=(id,v)=>{prefs[id]=!!v;store.set("quran-cf",prefs);};
let ui=store.get("quran-ui",{});if(!ui||typeof ui!=="object")ui={};
const applyUi=()=>{const r=document.documentElement;
  if(ui.theme&&ui.theme!=="auto")r.dataset.theme=ui.theme;else delete r.dataset.theme;
  r.style.setProperty("--tx",ui.tx||1);r.style.setProperty("--ar",ui.ar||2);};
const sliderRow=(label,key,min,max,step,def)=>{
  const i=h("input",{type:"range",min,max,step,value:ui[key]||def,"aria-label":label});
  i.addEventListener("input",()=>{ui[key]=+i.value;store.set("quran-ui",ui);applyUi();layout();});
  return h("label",{class:"row"},h("span",{text:label}),i);};

const layout=()=>dispatchEvent(new Event("quran:layout"));
const readingRows=()=>{
  const pick=(name,label,opts,cur,on)=>{const fs=h("fieldset",{class:"grp"},h("legend",{text:label}));
    opts.forEach(([v,tx])=>{const r=h("input",{type:"radio",name});r.checked=v===cur;r.addEventListener("change",()=>on(v));fs.append(h("label",{class:"radio"},r,tx));});return fs;};
  const save=(k,v)=>{ui[k]=v;store.set("quran-ui",ui);if(document.body.dataset.page==="reader")location.reload();};
  return[pick("rd-mode","Reading style",[["book","Book pages"],["scroll","Continuous scroll"]],ui.mode==="scroll"?"scroll":"book",v=>save("mode",v)),
    pick("rd-dir","Page turning (book pages)",[["rtl","Right to left, like a mushaf"],["ltr","Left to right"]],ui.dir==="ltr"?"ltr":"rtl",v=>save("dir",v))];};

/* ---------- ui helpers ---------- */
let tt;const toast=m=>{let t=$("#toast");if(!t){t=h("div",{id:"toast",role:"status","aria-live":"polite"});document.body.append(t);}
  t.textContent=m;t.classList.add("show");clearTimeout(tt);tt=setTimeout(()=>t.classList.remove("show"),2400);};
const copy=async text=>{try{await navigator.clipboard.writeText(text);return true;}catch{
  const t=h("textarea",{style:"position:fixed;opacity:0"});t.value=text;document.body.append(t);t.select();
  let ok=false;try{ok=document.execCommand("copy");}catch{}t.remove();return ok;}};
const ICONS={
  play:'<polygon points="6 4 20 12 6 20 6 4"/>',
  pause:'<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>',
  bookmark:'<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
  copy:'<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  link:'<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'};
const svg=n=>`<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[n]}</svg>`;
const iconBtn=(cls,icon,label,fn)=>{const b=h("button",{type:"button",class:"ib "+cls,"aria-label":label,title:label,html:svg(icon)});b.addEventListener("click",()=>fn(b));return b;};

/* ---------- search-friendly normalisation (Arabic marks, Latin accents, apostrophes) ---------- */
const MARKS=/[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u08D3-\u08FF\u0640]/;
const nch=c=>{if(MARKS.test(c))return"";
  if("\u0622\u0623\u0625\u0671".includes(c))return"\u0627";
  if(c==="\u0649"||c==="\u06CC")return"\u064A";if(c==="\u06A9")return"\u0643";
  if("'\u2019\u2018\u02BF\u02BE`".includes(c))return"";
  return c.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();};
const normMap=s=>{let t="";const m=[];for(let i=0;i<s.length;i++){const n=nch(s[i]);for(const ch of n){t+=ch;m.push(i);}}return{t,m};};
const norm=s=>normMap(s).t;

/* ---------- on-demand data (script tags so it also works from file://) ---------- */
const cache={},wait={};
window.QData=(k,a)=>{cache[k]=a;const w=wait[k];delete wait[k];(w||[]).forEach(p=>p[0](a));};
const load=k=>new Promise((ok,no)=>{
  if(cache[k])return ok(cache[k]);
  if(wait[k]){wait[k].push([ok,no]);return;}
  wait[k]=[[ok,no]];
  const s=document.createElement("script");s.src="data/"+k+".js";
  s.onerror=()=>{const w=wait[k];delete wait[k];s.remove();w.forEach(p=>p[1](new Error(k)));};
  document.head.append(s);});

/* ---------- edition picker (reader, settings, download) ---------- */
function chips(box,o){
  box.textContent="";
  const items=(o.audio?[{id:"audio",label:"Verse audio (Mishary Alafasy)",group:"Audio"}]:[]).concat(C.tr);
  const q=h("input",{type:"search",class:"field","aria-label":"Filter editions",placeholder:"Filter, e.g. Urdu or Yusuf"});
  const count=h("p",{class:"small muted","aria-live":"polite"});box.append(q,count);
  const groups=[],idx={};
  items.forEach(t=>{if(!(t.group in idx)){idx[t.group]=groups.length;groups.push({name:t.group,items:[]});}groups[idx[t.group]].items.push(t);});
  const upd=()=>{count.textContent=items.filter(t=>o.isOn(t.id)).length+" selected";};
  const sets=groups.map(g=>{
    const fs=h("fieldset",{class:"grp"},h("legend",{text:g.name})),row=h("div",{class:"chips"});
    g.items.forEach(t=>{
      const cb=h("input",{type:"checkbox"});cb.checked=!!o.isOn(t.id);
      cb.addEventListener("change",()=>{o.set(t.id,cb.checked);upd();if(o.change)o.change(t.id,cb.checked);});
      const sp=h("span",{text:t.label});if(t.tag)sp.append(" ",h("em",{text:t.tag}));
      row.append(h("label",{class:"chip","data-s":norm(`${t.full||t.label} ${g.name}`)},cb,sp));});
    fs.append(row);box.append(fs);return fs;});
  q.addEventListener("input",()=>{const w=norm(q.value).split(/\s+/).filter(Boolean);
    sets.forEach(fs=>{let any=false;$$(".chip",fs).forEach(l=>{const ok=w.every(x=>l.dataset.s.includes(x));l.hidden=!ok;if(ok)any=true;});fs.hidden=!any;});});
  upd();}

/* ---------- book view: paginated pages with swipe / drag page turns ---------- */
function makeBook(o){
  const rtl=o.rtl,reduce=matchMedia("(prefers-reduced-motion: reduce)").matches,all=$$("#verses>*");
  const sheet=cls=>{const head=h("div",{class:"pg-head",text:"\u00a0"}),body=h("div",{class:"pg-body"}),foot=h("div",{class:"pg-foot",text:"0"});
    return{head,body,foot,el:h("div",{class:"sheet "+cls},h("div",{class:"pg"},head,body,foot))};};
  const base=sheet("base"),meas=sheet("meas"),leaf=sheet("leaf");leaf.el.hidden=true;
  const leaves=h("div",{class:"leaves"},base.el,meas.el,leaf.el),cover=h("div",{class:"cover"},leaves);
  const prev=h("button",{type:"button",class:"btn bk-btn","aria-label":"Previous page",text:rtl?"\u203A":"\u2039"});
  const next=h("button",{type:"button",class:"btn bk-btn","aria-label":"Next page",text:rtl?"\u2039":"\u203A"});
  const slider=h("input",{type:"range",min:1,max:1,value:1,class:"bk-slider","aria-label":"Go to page"});
  const count=h("span",{class:"bk-count small","aria-live":"polite"});
  const bar=h("div",{class:"bk-bar"},prev,h("div",{class:"bk-mid"},slider,count),next);
  $("#verses").before(h("div",{class:"book"+(rtl?" rtl":"")},cover,bar));
  document.documentElement.classList.add("bookmode","book-ready");

  let pages=[],idx=0,busy=false,turn=null;
  const isAyah=x=>x.classList.contains("ayah");
  const firstAyah=i=>{const n=pages[i]&&pages[i].find(isAyah);return n?+n.dataset.a:0;};
  const groups=()=>{const G=[];let pend=[...o.title];
    all.forEach(n=>{if(n.hidden)return;if(isAyah(n)){G.push([...pend,n]);pend=[];}else pend.push(n);});
    G.push([...pend,...o.end]);return G;};
  const size=()=>{const top=cover.getBoundingClientRect().top+scrollY;
    leaves.style.height=Math.max(420,Math.min(innerHeight-top-bar.offsetHeight-36,900))+"px";};
  const fill=(s,i)=>{const pg=pages[i]||[],A=pg.filter(isAyah).map(x=>+x.dataset.a);
    s.body.replaceChildren(...pg);s.body.scrollTop=0;
    s.head.replaceChildren(h("span",{text:o.name}),h("span",{text:A.length?(A.length>1?`${o.sura}:${A[0]}\u2013${A[A.length-1]}`:`${o.sura}:${A[0]}`):""}));
    s.foot.textContent=String(i+1);};
  const setIdx=i=>{idx=Math.max(0,Math.min(i,pages.length-1));fill(base,idx);base.el.style.setProperty("--cast",0);
    slider.max=pages.length;slider.value=idx+1;count.textContent=`Page ${idx+1} of ${pages.length}`;
    prev.disabled=idx===0;next.disabled=idx===pages.length-1;if(o.onPage)o.onPage(firstAyah(idx));};
  const paginate=()=>{
    const atEnd=pages.length>1&&idx===pages.length-1,keep=pages.length?firstAyah(idx):0;
    base.body.replaceChildren();leaf.body.replaceChildren();size();meas.body.replaceChildren();
    const P=[];let cur=[];
    groups().forEach(g=>{meas.body.append(...g);
      if(meas.body.scrollHeight>meas.body.clientHeight+1&&cur.length){meas.body.replaceChildren(...g);P.push(cur);cur=[...g];}else cur.push(...g);});
    P.push(cur);meas.body.replaceChildren();pages=P;
    let t=0;if(atEnd)t=P.length-1;else if(keep){const j=P.findIndex(pg=>pg.includes(o.arts[keep-1]));t=j<0?0:j;}
    setIdx(t);};

  /* page-turn animation: t goes 0 -> 1; the leaf swings about the spine edge */
  const angle=(t,dir)=>(dir>0?t:1-t)*90*(rtl?1:-1);
  const draw=t=>{const a=angle(t,turn.dir);leaf.el.style.transform=`rotateY(${a}deg)`;
    leaf.el.style.setProperty("--shade",Math.abs(a)/90);base.el.style.setProperty("--cast",Math.sin(Math.PI*t));};
  const begin=dir=>{const to=idx+dir;if(to<0||to>=pages.length)return false;
    if(dir>0){fill(leaf,idx);fill(base,to);}else{fill(base,idx);fill(leaf,to);}
    turn={dir,to};leaf.el.hidden=false;draw(dir>0?0:0);return true;};
  const finish=ok=>{if(ok)idx=turn.to;turn=null;leaf.el.hidden=true;leaf.el.style.transform="";busy=false;setIdx(idx);};
  const anim=(from,to,ms,done)=>{if(reduce){draw(to);done();return;}const t0=performance.now();
    const step=now=>{const k=Math.min(1,(now-t0)/ms),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;draw(from+(to-from)*e);k<1?requestAnimationFrame(step):done();};
    requestAnimationFrame(step);};
  const turnBy=dir=>{if(busy||!begin(dir))return;busy=true;anim(0,1,430,()=>finish(true));};

  /* touch / pen drag follows the finger; mouse uses buttons, keys or horizontal wheel */
  const fwdSign=rtl?1:-1,st={id:null};
  leaves.addEventListener("pointerdown",e=>{if(e.pointerType==="mouse"||busy)return;Object.assign(st,{id:e.pointerId,x:e.clientX,y:e.clientY,t0:performance.now(),on:false,t:0,v:0});});
  leaves.addEventListener("pointermove",e=>{if(st.id!==e.pointerId)return;const dx=e.clientX-st.x,dy=e.clientY-st.y;
    if(!st.on){if(Math.abs(dx)<10||Math.abs(dx)<Math.abs(dy)*1.3)return;
      st.dir=dx*fwdSign>0?1:-1;if(!begin(st.dir)){st.id=null;return;}st.on=true;busy=true;try{leaves.setPointerCapture(e.pointerId);}catch{}}
    const along=dx*fwdSign*st.dir;st.t=Math.max(0,Math.min(1,along/(leaves.clientWidth*.85)));
    st.v=along/Math.max(1,performance.now()-st.t0);draw(st.t);});
  const release=cancel=>{if(!st.on){st.id=null;return;}st.id=null;st.on=false;
    const ok=!cancel&&(st.t>.3||st.v>.45);anim(st.t,ok?1:0,260,()=>finish(ok));};
  leaves.addEventListener("pointerup",e=>{if(st.id===e.pointerId)release(false);});
  leaves.addEventListener("pointercancel",e=>{if(st.id===e.pointerId)release(true);});
  let wl=0;leaves.addEventListener("wheel",e=>{if(Math.abs(e.deltaX)>Math.abs(e.deltaY)&&Math.abs(e.deltaX)>40&&performance.now()-wl>600){
    wl=performance.now();e.preventDefault();turnBy((e.deltaX>0)!==rtl?1:-1);}},{passive:false});
  document.addEventListener("keydown",e=>{if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest("input,select,textarea,[contenteditable]"))return;
    if(e.key==="ArrowRight"||e.key==="ArrowLeft")turnBy((e.key==="ArrowRight")!==rtl?1:-1);});
  prev.addEventListener("click",()=>turnBy(-1));next.addEventListener("click",()=>turnBy(1));
  slider.addEventListener("input",()=>{if(!busy)setIdx(+slider.value-1);});

  /* re-flow when anything that changes page heights changes */
  let rt;const refresh=()=>{clearTimeout(rt);rt=setTimeout(()=>busy?refresh():paginate(),90);};
  addEventListener("quran:layout",refresh);
  let lw=innerWidth,lh=innerHeight;addEventListener("resize",()=>{if(innerWidth!==lw||Math.abs(innerHeight-lh)>80){lw=innerWidth;lh=innerHeight;refresh();}});
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(refresh);
  const panel=$("#panel");if(panel)panel.addEventListener("toggle",refresh);

  const reveal=(n,flash=true)=>{const i=pages.findIndex(pg=>pg.includes(o.arts[n-1]));if(i<0||busy)return;
    const done=()=>{const el=o.arts[n-1];base.body.scrollTop=Math.max(0,el.offsetTop-6);if(flash){el.classList.add("flash");setTimeout(()=>el.classList.remove("flash"),1800);}};
    if(i===idx)done();else if(Math.abs(i-idx)===1){turnBy(i-idx);setTimeout(done,480);}else{setIdx(i);done();}};
  paginate();
  if(!store.get("quran-bk-hint",false)){store.set("quran-bk-hint",true);setTimeout(()=>toast(`Swipe ${rtl?"right":"left"} to turn the page`),700);}
  return{refresh,reveal};
}

/* ---------- reader ---------- */
function initReader(){
  const s=+document.body.dataset.sura,meta=C.suras[s-1],size=meta.size,root=document.documentElement;
  const arts=$$(".ayah"),bar=$("#rangebar"),statusEl=$("#status");let book=null;
  const jump=$("#jump");
  jump.append(h("option",{value:"",text:"Choose a surah"}));
  C.suras.forEach((m,i)=>{const n=i+1;if(n<C.range[0]||n>C.range[1])return;jump.append(h("option",{value:pad(n)+".html",text:`${n}. ${m.name}`,selected:n===s}));});
  jump.addEventListener("change",()=>{if(jump.value)location.href=jump.value;});
  const flags=()=>{root.classList.toggle("no-ar",!isOn("arabic"));root.classList.toggle("simple-primary",!isOn("arabic")&&isOn("arabic-simple"));root.classList.toggle("no-audio",!isOn("audio"));};

  /* range + deep links: #5 jumps to a verse, #5-9 shows only those verses */
  let from=1,to=size;const fi=h("input",{type:"number",class:"num",min:1,max:size,value:1,"aria-label":"From verse"}),ti=h("input",{type:"number",class:"num",min:1,max:size,value:size,"aria-label":"To verse"});
  const applyRange=(a,b,pushHash)=>{from=a;to=b;fi.value=a;ti.value=b;
    arts.forEach(x=>{const n=+x.dataset.a;x.hidden=n<a||n>b;});
    $$(".juz-mark").forEach(x=>{const n=+x.dataset.a;x.hidden=n<a||n>b;});
    const full=a===1&&b===size;bar.hidden=full;bar.textContent="";
    if(!full){bar.append(a===b?`Showing verse ${a} of ${size}. `:`Showing verses ${a}–${b} of ${size}. `,h("button",{type:"button",class:"link",text:"Show whole surah"}));
      $("button",bar).addEventListener("click",()=>applyRange(1,size,true));}
    if(pushHash)history.replaceState(null,"",full?location.pathname+location.search:`#${a}${a===b?"":"-"+b}`);if(book)book.refresh();};
  const focusAyah=n=>{if(book){book.reveal(n);return;}const el=arts[n-1];if(!el)return;el.scrollIntoView({block:"start"});el.classList.add("flash");setTimeout(()=>el.classList.remove("flash"),1800);};
  const route=()=>{const m=/^#(?:ayah-)?(\d+)(?:-(\d+))?$/.exec(location.hash);if(!m)return;
    let a=+m[1],b=m[2]?+m[2]:a;if(a>b){const t=a;a=b;b=t;}if(a<1||a>size)return;b=Math.min(b,size);
    if(a!==b){applyRange(a,b,false);if(!book)scrollTo({top:Math.max(0,bar.offsetTop-8)});}else{applyRange(1,size,false);focusAyah(a);}};

  /* bookmarks */
  const bms=()=>{const b=store.get("quran-bookmark",[]);return Array.isArray(b)?b:[];};
  const toggleBm=(a,btn)=>{const l=bms(),i=l.findIndex(b=>b.s===s&&b.a===a);
    if(i>=0){l.splice(i,1);btn.setAttribute("aria-pressed","false");toast("Bookmark removed");}
    else{l.unshift({s,a,n:meta.name,t:Date.now()});btn.setAttribute("aria-pressed","true");toast(`Bookmarked ${s}:${a}`);}
    store.set("quran-bookmark",l);};

  /* audio */
  let au=null;const cont=()=>store.get("quran-cont",true)!==false;
  const setPlay=(art,on)=>{const b=$(".play",art);if(!b)return;const a=+art.dataset.a;b.innerHTML=svg(on?"pause":"play");const l=on?`Pause verse ${a}`:`Play verse ${a}`;b.setAttribute("aria-label",l);b.title=l;};
  const stopAudio=()=>{if(au){au.pause();au.onended=au.onerror=null;au=null;}arts.filter(x=>x.classList.contains("playing")).forEach(x=>{x.classList.remove("playing");setPlay(x,false);});};
  const play=a=>{stopAudio();const art=arts[a-1];if(!art)return;
    au=new Audio(C.audio.replace("{s}",pad(s)).replace("{a}",pad(a)));art.classList.add("playing");setPlay(art,true);
    au.onended=()=>{stopAudio();const nx=arts[a];if(cont()&&nx&&!nx.hidden){play(a+1);if(book)book.reveal(a+1,false);else nx.scrollIntoView({block:"center",behavior:"smooth"});}};
    au.onerror=()=>{stopAudio();toast("Audio could not be loaded. Check your connection.");};
    au.play().catch(()=>{stopAudio();toast("Couldn’t start audio.");});};

  const verseText=art=>{const a=+art.dataset.a,L=[`${meta.name} (${s}:${a})`];
    if(isOn("arabic"))L.push($(".ar",art).textContent);
    $$(".ar-alt",art).forEach(t=>L.push((isOn("arabic")?$("h3",t).textContent+": ":"")+$("p",t).textContent));
    $$(".tr",art).forEach(t=>L.push($("h3",t).firstChild.textContent+": "+$("p",t).textContent));return L.join("\n");};
  arts.forEach(art=>{const a=+art.dataset.a,box=h("div",{class:"actions"});
    box.append(
      iconBtn("play","play",`Play verse ${a}`,()=>{if(au&&art.classList.contains("playing"))stopAudio();else play(a);}),
      (()=>{const b=iconBtn("bm","bookmark",`Bookmark verse ${a}`,b=>toggleBm(a,b));b.setAttribute("aria-pressed",String(bms().some(x=>x.s===s&&x.a===a)));return b;})(),
      iconBtn("cp","copy",`Copy verse ${a} text`,async()=>toast(await copy(verseText(art))?"Verse copied":"Couldn’t copy")),
      iconBtn("ln","link",`Copy link to verse ${a}`,async()=>toast(await copy(location.href.split("#")[0]+"#"+a)?"Link copied":"Couldn’t copy")));
    $(".ayah-head",art).append(box);});

  /* on-demand editions */
  const trNode=(t,text)=>t.kind==="arabic"?h("section",{class:"ar-alt","data-t":t.id,lang:"ar",dir:"rtl"},h("h3",{text:t.full}),h("p",{text})):h("section",{class:"tr","data-t":t.id,"data-kind":t.kind,lang:t.lang,dir:t.rtl?"rtl":false},
    h("h3",{},t.full,t.tag?h("span",{class:"tag",text:t.tag}):null),h("p",{text}));
  const place=(art,t,text)=>{if(!text||$(`[data-t="${t.id}"]`,art))return;
    const list=$(t.kind==="arabic"?".ar-extra":".tr-list",art),ref=[...list.children].find(c=>ORD[c.dataset.t]>ORD[t.id]);list.insertBefore(trNode(t,text),ref||null);};
  const sync=async()=>{
    arts.forEach(a=>$$("[data-t]",a).forEach(n=>{if(!isOn(n.dataset.t))n.remove();}));
    const need=C.tr.filter(t=>t.id!=="arabic"&&isOn(t.id)&&!arts.some(a=>$(`[data-t="${t.id}"]`,a)));
    if(!need.length){statusEl.textContent="";layout();return;}
    statusEl.textContent="Loading…";
    const res=await Promise.all(need.map(t=>load(`surah/${t.id}/${pad(s)}`).then(a=>[t,a],()=>[t,null])));
    const fails=[];
    res.forEach(([t,arr])=>{if(!arr){fails.push(t.label);return;}if(!isOn(t.id))return;arts.forEach(art=>place(art,t,arr[+art.dataset.a-1]));});
    statusEl.textContent=fails.length?`Couldn’t load ${fails.join(", ")}. Check your connection and try again.`:"";layout();};

  /* display panel */
  const body=$("#panel-body");body.textContent="";
  const go=h("button",{type:"button",class:"btn small",text:"Show"});
  go.addEventListener("click",()=>{let a=parseInt(fi.value,10)||1,b=parseInt(ti.value,10)||size;if(a>b)[a,b]=[b,a];applyRange(Math.max(1,a),Math.min(size,b),true);});
  const autoplay=h("input",{type:"checkbox"});autoplay.checked=cont();autoplay.addEventListener("change",()=>store.set("quran-cont",autoplay.checked));
  const chipBox=h("div");
  body.append(...readingRows(),sliderRow("Translation text size","tx",0.85,1.6,0.05,1),sliderRow("Arabic text size","ar",1.4,3.4,0.1,2),
    h("div",{class:"row"},h("span",{text:"Show verses"}),fi,"to",ti,go),
    h("label",{class:"radio"},autoplay,"Play the next verse automatically"),
    h("h2",{text:"Shown with each verse"}),chipBox);
  chips(chipBox,{audio:true,isOn,set:setOn,change:()=>{flags();sync();}});

  /* reading position */
  let last=1,tm;const save=()=>store.set("quran-history",{s,a:last,n:meta.name,t:Date.now()});save();
  flags();
  if(ui.mode!=="scroll"){
    book=makeBook({sura:s,name:meta.name,arts,rtl:ui.dir!=="ltr",title:[$("h1"),$(".meaning"),$(".facts")],end:[$(".pager"),$(".pager").nextElementSibling],
      onPage:a=>{if(a){last=a;clearTimeout(tm);tm=setTimeout(save,800);}}});
  }else if("IntersectionObserver"in window){const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting)last=+e.target.dataset.a;});clearTimeout(tm);tm=setTimeout(save,1000);},{rootMargin:"0px 0px -75% 0px"});arts.forEach(a=>io.observe(a));}
  addEventListener("pagehide",save);addEventListener("hashchange",route);
  flags();sync();route();
}

/* ---------- index ---------- */
function initIndex(){
  const f=$("#filter"),items=$$("#sgrid li").map(li=>({li,k:norm(li.dataset.k)}));
  f.addEventListener("input",()=>{const q=norm(f.value).split(/\s+/).filter(Boolean);let n=0;
    items.forEach(({li,k})=>{const ok=q.every(t=>k.includes(t));li.hidden=!ok;if(ok)n++;});
    $("#fcount").textContent=q.length?`${n} surah${n===1?"":"s"} found`:"";});
  const hist=store.get("quran-history",null),res=$("#resume");
  if(hist&&hist.s&&C.suras[hist.s-1]){res.hidden=false;
    res.append(h("h2",{text:"Continue reading"}),h("a",{class:"btn",href:`${pad(hist.s)}.html#${hist.a||1}`,text:`${sname(hist.s)} ${hist.s}:${hist.a||1}, ${ago(hist.t)}`}));}
  const bm=store.get("quran-bookmark",[]);
  if(Array.isArray(bm)&&bm.length){res.hidden=false;res.append(" ",h("a",{class:"btn",href:"bookmarks.html",text:`${bm.length} bookmark${bm.length===1?"":"s"}`}));}
  if(!store.get("quran-seen",false)){const w=$("#welcome");w.hidden=false;$("#welcome-x").addEventListener("click",()=>{store.set("quran-seen",true);w.hidden=true;});}
}

/* ---------- settings ---------- */
function initConfig(){
  const build=()=>chips($("#cfg-chips"),{audio:true,isOn,set:setOn});build();
  $("#cfg-sliders").append(...readingRows(),sliderRow("Translation text size","tx",0.85,1.6,0.05,1),sliderRow("Arabic text size","ar",1.4,3.4,0.1,2));
  $$("input[name=theme]").forEach(r=>{r.checked=r.value===(ui.theme||"auto");
    r.addEventListener("change",()=>{ui.theme=r.value;store.set("quran-ui",ui);applyUi();});});
  $("#cfg-reset").addEventListener("click",()=>{store.del("quran-cf");prefs={};build();toast("Defaults restored");});
  $("#cfg-clear").addEventListener("click",()=>{if(confirm("Remove all bookmarks and reading history from this browser?")){store.del("quran-bookmark");store.del("quran-history");toast("Cleared");}});
}

/* ---------- bookmarks ---------- */
function initBookmarks(){
  const list=$("#bm-list"),count=$("#bm-count");
  const get=()=>{const b=store.get("quran-bookmark",[]);return Array.isArray(b)?b:[];};
  const render=()=>{const b=get();list.textContent="";
    count.textContent=b.length?`${b.length} bookmark${b.length===1?"":"s"}`:"";
    if(!b.length){list.append(h("li",{text:"No bookmarks yet. Use the bookmark button on any verse."}));return;}
    b.forEach((x,i)=>{const rm=h("button",{type:"button",class:"btn small",text:"Remove","aria-label":`Remove bookmark ${x.s}:${x.a}`});
      rm.addEventListener("click",()=>{const l=get();l.splice(i,1);store.set("quran-bookmark",l);render();});
      list.append(h("li",{},h("span",{},h("a",{href:`${pad(x.s)}.html#${x.a}`,text:`${sname(x.s)} ${x.s}:${x.a}`}),h("br"),h("small",{class:"muted",text:ago(x.t)})),rm));});};
  $("#bm-clear").addEventListener("click",()=>{if(confirm("Remove all bookmarks?")){store.set("quran-bookmark",[]);render();}});
  $("#bm-export").addEventListener("click",()=>{const u=URL.createObjectURL(new Blob([JSON.stringify(get(),null,2)],{type:"application/json"}));
    const a=h("a",{href:u,download:"quran-bookmarks.json"});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),500);});
  $("#bm-import").addEventListener("change",e=>{const f=e.target.files[0];if(!f)return;const r=new FileReader();
    r.onload=()=>{try{const d=JSON.parse(r.result);if(!Array.isArray(d))throw new Error("The file is not a list of bookmarks.");
      const m=new Map(get().map(b=>[b.s+":"+b.a,b]));
      d.filter(b=>b&&b.s>=1&&b.s<=114&&b.a>=1).forEach(b=>m.set(b.s+":"+b.a,{s:+b.s,a:+b.a,n:b.n||"",t:+b.t||Date.now()}));
      store.set("quran-bookmark",[...m.values()].sort((a,b)=>b.t-a.t));render();toast("Imported");}catch(err){toast("Import failed: "+err.message);}e.target.value="";};
    r.readAsText(f);});
  render();
}

/* ---------- search ---------- */
function initSearch(){
  const form=$("#sform"),q=$("#q"),status=$("#status"),list=$("#results"),more=$("#more");
  const fields=C.tr.filter(t=>isOn(t.id)),names=fields.map(f=>f.full);
  $("#scope").append("Searching in: ",names.length?(names.length>6?`${names.slice(0,5).join(", ")} and ${names.length-5} more`:names.join(", ")):"nothing selected"," ",h("a",{href:"config.html",text:"Change"}));
  const S=[],A=[];C.suras.forEach((m,i)=>{for(let a=1;a<=m.size;a++){S.push(i+1);A.push(a);}});
  const nameN=C.suras.map(m=>norm(m.name+" "+m.meaning)),ncache={};
  let hits=[],shown=0,terms=[],arrs=[];
  const highlight=(text,ts)=>{const nm=normMap(text),R=[];
    ts.forEach(t=>{let i=0;while((i=nm.t.indexOf(t,i))!==-1){R.push([nm.m[i],nm.m[i+t.length-1]+1]);i+=t.length;}});
    R.sort((x,y)=>x[0]-y[0]);const out=document.createDocumentFragment();let pos=0;
    R.forEach(r=>{if(r[1]<=pos)return;const s=Math.max(r[0],pos);if(s>pos)out.append(text.slice(pos,s));out.append(h("mark",{text:text.slice(s,r[1])}));pos=r[1];});
    if(pos<text.length)out.append(text.slice(pos));return out;};
  const render=()=>{const end=Math.min(shown+20,hits.length);
    for(;shown<end;shown++){const i=hits[shown],s=S[i],a=A[i];
      const card=h("li",{class:"hit"},h("div",{class:"hit-head"},h("strong",{text:`${sname(s)} ${s}:${a}`}),h("a",{href:`${pad(s)}.html#${a}`,text:"Open verse"})));
      fields.forEach((f,k)=>{const t=arrs[k][i];if(t)card.append(h("p",{class:"hit-text",lang:f.lang,dir:f.rtl?"rtl":false},h("span",{class:"hit-label",text:f.full}),highlight(t,terms)));});
      list.append(card);}
    status.textContent=`${hits.length} verse${hits.length===1?"":"s"} found${hits.length>shown?`, showing ${shown}`:""}.`;
    more.hidden=shown>=hits.length;more.textContent=`Show more (${hits.length-shown} left)`;};
  const run=async()=>{const text=q.value.trim();list.textContent="";more.hidden=true;hits=[];shown=0;
    history.replaceState(null,"",text?"?q="+encodeURIComponent(text):location.pathname);
    if(!text){status.textContent="";return;}
    const ref=/^(\d{1,3})\s*[:.]\s*(\d{1,3})$/.exec(text);
    if(ref&&+ref[1]>=1&&+ref[1]<=114&&+ref[2]>=1&&+ref[2]<=C.suras[ref[1]-1].size)
      list.append(h("li",{class:"hit"},h("a",{href:`${pad(+ref[1])}.html#${+ref[2]}`,text:`Go to ${sname(+ref[1])} ${+ref[1]}:${+ref[2]}`})));
    terms=norm(text).split(/\s+/).filter(Boolean);if(!terms.length)return;
    nameN.forEach((n,i)=>{if(terms.every(t=>n.includes(t))&&list.children.length<4)list.append(h("li",{class:"hit"},h("a",{href:pad(i+1)+".html",text:`Surah ${i+1}: ${C.suras[i].name} (${C.suras[i].meaning})`})));});
    if(!fields.length){status.textContent="Select at least one edition in Settings to search verse text.";return;}
    status.textContent="Searching…";
    try{arrs=await Promise.all(fields.map(f=>load("search/"+f.id)));}catch{status.textContent="Couldn’t load search data. Check your connection and try again.";return;}
    fields.forEach((f,k)=>{if(!ncache[f.id])ncache[f.id]=arrs[k].map(norm);});
    for(let i=0;i<S.length;i++){const hay=fields.map(f=>ncache[f.id][i]).join(" ");if(terms.every(t=>hay.includes(t)))hits.push(i);}
    if(!hits.length){status.textContent="No verses found. Try fewer or simpler words.";return;}
    render();};
  form.addEventListener("submit",e=>{e.preventDefault();run();});
  more.addEventListener("click",render);
  const init=new URLSearchParams(location.search).get("q");if(init){q.value=init;run();}
}

/* ---------- offline ZIP ---------- */
function initDownload(){
  const sel=Object.fromEntries(C.tr.map(t=>[t.id,!!C.defaults[t.id]]));
  chips($("#dl-chips"),{isOn:id=>sel[id],set:(id,v)=>{sel[id]=v;}});
  const st=$("#dl-status"),prog=$("#dl-prog"),btn=$("#dl-go");
  btn.addEventListener("click",async()=>{
    if(typeof JSZip==="undefined"){st.textContent="The ZIP library could not be loaded. Check your connection.";return;}
    const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
    const from=clamp(parseInt($("#dl-from").value,10)||1,1,114),to=clamp(parseInt($("#dl-to").value,10)||114,from,114);
    const ids=C.tr.filter(t=>sel[t.id]).map(t=>t.id);
    if(!ids.length){st.textContent="Select at least one edition.";return;}
    const withSearch=$("#dl-search").checked;
    const optional=["index","bookmarks","config","sources","license"].filter(p=>$("#dl-p-"+p).checked);
    const included=new Set(optional.map(p=>p+".html"));if(withSearch)included.add("search.html");
    const excluded=new Set(["index","bookmarks","config","sources","license","search","download"].map(p=>p+".html").filter(p=>!included.has(p)));
    const jobs=[{p:"assets/style.css"},{p:"assets/app.js"},{p:"assets/catalog.js",cat:1}];
    for(let s=from;s<=to;s++){jobs.push({p:pad(s)+".html",page:1});ids.forEach(id=>jobs.push({p:`data/surah/${id}/${pad(s)}.js`}));}
    included.forEach(p=>jobs.push({p,page:1}));
    if(withSearch)ids.forEach(id=>jobs.push({p:`data/search/${id}.js`}));
    btn.disabled=true;prog.hidden=false;prog.value=0;
    const zip=new JSZip(),missing=[];let done=0;
    const clean=doc=>{$$("a[href]",doc).forEach(a=>{const href=a.getAttribute("href"),m=/^(\d{3})\.html/.exec(href),pg=href.split("#")[0].split("?")[0];
      if((m&&(+m[1]<from||+m[1]>to))||excluded.has(pg)){const li=a.closest("li");(li&&$$("a",li).length===1?li:a).remove();}});
      $$("[data-t]",doc).forEach(n=>{if(!ids.includes(n.dataset.t))n.remove();});};
    const run=async j=>{try{const r=await fetch(j.p);if(!r.ok)throw 0;let t=await r.text();
      if(j.page){const d=new DOMParser().parseFromString(t,"text/html");clean(d);t="<!DOCTYPE html>\n"+d.documentElement.outerHTML;}
      if(j.cat){const c=JSON.parse(t.slice(t.indexOf("=")+1).replace(/;\s*$/,""));
        c.tr=c.tr.filter(x=>ids.includes(x.id));c.range=[from,to];
        const keep=Object.keys(c.defaults).filter(k=>k==="audio"||ids.includes(k)&&c.defaults[k]);
        c.defaults=Object.fromEntries(keep.map(k=>[k,true]));
        if(!keep.some(k=>k!=="audio"))ids.slice(0,3).forEach(k=>c.defaults[k]=true);
        t="window.QURAN_CATALOG="+JSON.stringify(c)+";\n";}
      zip.file(j.p,t);}catch{missing.push(j.p);}
      prog.value=Math.round(++done*100/jobs.length);st.textContent=`Fetched ${done} of ${jobs.length} files`;};
    const queue=jobs.slice();await Promise.all(Array.from({length:8},async()=>{while(queue.length)await run(queue.shift());}));
    st.textContent="Compressing…";
    const blob=await zip.generateAsync({type:"blob",compression:"DEFLATE"});
    const u=URL.createObjectURL(blob),a=h("a",{href:u,download:"quran-reader-offline.zip"});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),2000);
    st.textContent=missing.length?`Done, but ${missing.length} file(s) could not be fetched (for example ${missing[0]}).`:"Done. Open index.html from the extracted folder.";
    btn.disabled=false;});
}

/* ---------- boot ---------- */
applyUi();
const top=h("button",{class:"totop",type:"button","aria-label":"Back to top",html:"&#8593;"});
top.hidden=true;top.addEventListener("click",()=>scrollTo({top:0}));document.body.append(top);
addEventListener("scroll",()=>{top.hidden=scrollY<700;},{passive:true});
try{({reader:initReader,index:initIndex,search:initSearch,config:initConfig,bookmarks:initBookmarks,download:initDownload})[document.body.dataset.page]?.();}catch(e){document.documentElement.classList.remove("book-pref");console.error(e);}
})();
