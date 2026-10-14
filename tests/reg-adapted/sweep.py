import json,re
from playwright.sync_api import sync_playwright
U='http://localhost:8851/platform-app.html'
SCR=[('home',"ST.tab='home'"),('discover',"ST.tab='discover'"),('discover-map',"ST.tab='discover';discAct('dview',{v:'map'})"),('discover-hair',"ST.tab='discover';discAct('dtype',{v:'hair'})"),('nari',"ST.tab='nari'"),('you',"ST.tab='you'"),('you-wallet',"ST.tab='you';ST.page='wallet'"),('you-vouchers',"ST.tab='you';ST.page='vouchers';ST.vseg='mine'"),('you-vouchers-more',"ST.tab='you';ST.page='vouchers';ST.vseg='more'"),('you-settings',"ST.tab='you';ST.page='settings'"),('notif',"ST.page='notif'"),('nset',"ST.page='nset'")]
for s in ['capsule','salon','skin','spa','pickle','nails','yoga','barber','moc','rally']: SCR.append(('store-'+s,f"ST.store='{s}'"))
CLK=[('sheet-join','home','joinsheet'),('sheet-qr','discover','joinsheet+qr'),('sheet-link','home','joinsheet+linkjoin'),('sheet-stretch','home','stretch'),('sheet-manage','home','managebk'),('call','nari','nmore+calldemo'),('slots-again0','nari','nagain'),('confirm','nari','nagain'),('success','nari','nagain+chatbook'),('bookings','home','mybk'),('rate','home','mybk+bkpast+rate'),('cancel','home','mybk+cancelask'),('sheet-lang','home','lang')]
AUD=r"""(()=>{
 const vis=e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!='hidden'&&cs.display!='none'&&!e.closest('[hidden]')};
 const small=[...document.querySelectorAll('button,a[href],input,select,textarea,[role=button],[role=switch],label.row')].filter(vis).filter(e=>{const r=e.getBoundingClientRect();return (r.width<44||r.height<44)&&!(e.type=='checkbox'&&e.closest('label')&&e.closest('label').getBoundingClientRect().height>=44)}).map(e=>(e.dataset.act||e.tagName)+':'+(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,20)+':'+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height));
 const lum=c=>{const m=c.match(/[\d.]+/g);if(!m)return null;const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b};
 const bgOf=e=>{for(let x=e;x;x=x.parentElement){const c=getComputedStyle(x).backgroundColor;const m=c.match(/[\d.]+/g);if(m&&(m.length<4||+m[3]>0.5))return c;}return 'rgb(255,255,255)'};
 const low=[];const tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;const texts=[];
 while(n=tw.nextNode()){const t=n.textContent.trim();if(!t)continue;const e=n.parentElement;if(!vis(e)||e.closest('.vh'))continue;texts.push(t);
   const cs=getComputedStyle(e);const L1=lum(cs.color),L2=lum(bgOf(e));if(L1==null)continue;const cr=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);const fs=parseFloat(cs.fontSize),bold=+cs.fontWeight>=700;const need=(fs>=24||(fs>=18.66&&bold))?3:4.5;if(cr<need&&+cs.opacity>0.5)low.push(t.slice(0,25)+':'+cr.toFixed(2)+':'+cs.color+'/'+bgOf(e));}
 const attrs=[...document.querySelectorAll('[aria-label],[placeholder],[title],img[alt]')].filter(vis).map(e=>e.getAttribute('aria-label')||e.getAttribute('placeholder')||e.getAttribute('title')||e.getAttribute('alt'));
 const clip=[...document.querySelectorAll('body *')].filter(vis).filter(e=>{const cs=getComputedStyle(e);return (cs.overflow.includes('hidden')||cs.textOverflow=='ellipsis')&&e.scrollWidth>e.clientWidth+1&&e.innerText&&e.children.length<3}).map(e=>e.innerText.trim().slice(0,30));
 const over=[...document.querySelectorAll('#app *')].filter(vis).filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&!e.closest('.scroll,.chips,.hscroll,[class*=scroll]')}).map(e=>(e.className||e.tagName)+':'+(e.innerText||'').trim().slice(0,20)).slice(0,6);
 const ads=[...document.querySelectorAll('.spons,.adtag,.tag.sp')].filter(vis).length;
 return {small:[...new Set(small)],low:[...new Set(low)].slice(0,12),texts,attrs,clip:[...new Set(clip)],over,wide:document.documentElement.scrollWidth>innerWidth,ads,title:document.title}})()"""
EN=re.compile(r"\b(the|your|you|with|and|for|book|booked|cancel|free|until|left|class|place|places|today|tomorrow|store|pay|deposit|time|open|more|get|owned|sample|court|room|staff|minutes?|min|done|undo|back|close|next|week|rest|start|show|try|new|join|scan|link|search|message|sent|level|missions?|streak|coins|notifications?|settings?|why|this|ad|sponsored|map|list|filters?|players?|anyone|any)\b",re.I)
O={}
with sync_playwright() as p:
  b=p.chromium.launch()
  for vw in [(390,844),(320,568)]:
   for lang in ['en','vi','ko']:
    for rm in ([False,True] if lang=='en' else [False]):
     c=b.new_context(viewport={'width':vw[0],'height':vw[1]},reduced_motion='reduce' if rm else 'no-preference');pg=c.new_page();E=[];V=[]
     pg.on('console',lambda m:E.append(m.type+':'+m.text) if m.type in('error','warning') else None);pg.on('pageerror',lambda e:E.append('PAGEERR '+str(e)))
     pg.on('response',lambda r:E.append(f'{r.status} {r.url}') if r.status>=400 else None)
     pg.on('request',lambda r:V.append(r.url.split('/')[-1]) if r.url.endswith(('.webm','.mp4')) else None)
     tag=f'{vw[0]}|{lang}{"|rm" if rm else ""}'
     for name,js in SCR+[(x[0],None) for x in CLK]:
       pg.goto(U);pg.evaluate("()=>localStorage.clear()");pg.goto(U);pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
       if js: pg.evaluate(f"()=>{{{js};render();scrollTo(0,0)}}")
       else:
         tab,act=[(x[1],x[2]) for x in CLK if x[0]==name][0]
         pg.evaluate(f"()=>{{ST.tab='{tab}';render()}}")
         for a in act.split('+'):
           sel={'nagain':'[data-act=nagain][data-i="1"]','chatbook':'[data-act=chatbook]','bkpast':'[data-act=bkseg][data-v=past]','rate':'[data-act=rate]','cancelask':'[data-act=cancelask]','again':'[data-act=again][data-i="1"]','slot':'.sheet [data-act=slot]','dobook':'.sheet [data-act=dobook]','qr':'.sheet [data-act=qr]','linkjoin':'.sheet [data-act=linkjoin]'}.get(a,f'[data-act={a}]')
           pg.locator(sel).first.click();pg.wait_for_timeout(200)
       pg.wait_for_timeout(250)
       a=pg.evaluate(AUD);a['err']=list(E);E.clear()
       if lang!='en': a['eng']=[t for t in a['texts']+[x for x in a['attrs'] if x] if EN.search(t) and not re.search(r'[À-ỹ가-힣]',t)][:25]
       a.pop('texts');a.pop('attrs')
       O[f'{tag}|{name}']=a
       if not rm: pg.screenshot(path=f's-{vw[0]}-{lang}-{name}.png',full_page=name.startswith(('home','discover','store-capsule','nset','you')))
     O[f'{tag}|_video']=V
     c.close()
json.dump(O,open('sweep.json','w'),ensure_ascii=False,indent=1)
print('done',len(O))
