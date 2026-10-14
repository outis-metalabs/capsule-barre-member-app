import json
from playwright.sync_api import sync_playwright
U='http://localhost:8851/platform-app.html'
R=[]
def chk(name,cond,info=''):
  R.append((name,bool(cond),info)); 
with sync_playwright() as p:
  b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':844});E=[]
  pg.on('console',lambda m:E.append(m.text) if m.type in('error','warning') else None);pg.on('pageerror',lambda e:E.append(str(e)))
  def fresh(lang,tab='home'):
    pg.goto(U);pg.evaluate(f"()=>{{localStorage.clear();setLang('{lang}');ST.tab='{tab}';render()}}");pg.wait_for_timeout(80)
  def last(cid): return pg.evaluate(f"()=>{{const m=CH['{cid}'].msgs;return m[m.length-1]}}")
  def thread(cid): return pg.evaluate(f"()=>document.getElementById('th-{cid}').innerText")
  def send(cid,q): pg.evaluate("([c,q])=>__plat.chatSend(c,q)",[cid,q]); pg.wait_for_timeout(30)
  def tapchip(cid,label_sub):
    return pg.evaluate("""([c,s])=>{const m=CH[c].msgs;const i=m.length-1;const j=(m[i].chips||[]).findIndex(x=>x.label.includes(s));if(j<0)return false;chatChip(c,i,j);return true}""",[cid,label_sub])
  # 1. every example chip and Ask chip, every language: no false safety line, booking progresses
  for lang in ['en','vi','ko']:
    fresh(lang,'book')
    chips=pg.evaluate("()=>[...exampleChips().map(c=>c.val.say)]")
    fresh(lang,'ask'); ask=pg.evaluate("()=>[...document.querySelectorAll('[data-act=askq]')].map(e=>e.dataset.v)")
    for q in chips+ask:
      for cid in ['book','ask']:
        fresh(lang,cid);send(cid,q);m=last(cid)
        exp_care = any(k in q for k in ['knee','đầu gối','무릎'])
        chk(f'chip[{lang}|{cid}] {q}', bool(m.get('care'))==exp_care, m['text'][:70])
  # 2. cancel in chat, 3 languages, confirmation step
  for lang,q,store in [('en','cancel my haircut','salon'),('vi','hủy lịch cắt tóc','salon'),('ko','커트 취소해줘','salon'),('vi','huy lich cham soc da','skin'),('en','cancel my court on Thursday','pickle')]:
    fresh(lang,'ask');n0=pg.evaluate(f"()=>B.filter(b=>b.store==='{store}'&&b.status==='confirmed').length")
    send('ask',q);m=last('ask')
    chk(f'cancel asks to confirm [{lang}] {q}', m.get('bk') and len(m.get('chips',[]))==2 and pg.evaluate(f"()=>B.filter(b=>b.store==='{store}'&&b.status==='confirmed').length")==n0, m['text'][:90])
    pg.evaluate("()=>{const m=CH.ask.msgs;chatChip('ask',m.length-1,0)}")
    chk(f'cancel done after tap [{lang}] {q}', pg.evaluate(f"()=>B.filter(b=>b.store==='{store}'&&b.status==='confirmed').length")==n0-1, last('ask')['text'][:80])
    chk(f'cancel reply localized [{lang}]', lang=='en' or 'Cancelled' not in thread('ask'))
  # keep path
  fresh('en','ask');send('ask','cancel my facial');pg.evaluate("()=>{const m=CH.ask.msgs;chatChip('ask',m.length-1,1)}")
  chk('keep it leaves booking', pg.evaluate("()=>B.filter(b=>b.store==='skin'&&b.status==='confirmed').length")==1)
  # ambiguous cancel
  fresh('vi','ask');send('ask','hủy lịch');m=last('ask');chk('bare hủy lịch asks which booking', len(m.get('chips',[]))>=4, m['text'])
  # bare cancel mid-draft drops the draft
  fresh('en','book');send('book','haircut with Linh');send('book','cancel');chk('bare cancel mid-draft = nothing booked', last('book')['text']=='Okay, nothing booked.')
  # cancel policy question is not a cancel
  fresh('en','ask');send('ask','what is the cancel policy at Capsule?');chk('cancel policy question not a cancel', not last('ask').get('bk'), last('ask')['text'][:60])
  # 3. move in chat
  for lang,q in [('en','move my facial to Sunday'),('vi','dời lịch chăm sóc da sang chủ nhật'),('ko','페이셜 일요일로 옮겨줘'),('en','reschedule my haircut'),('vi','doi lich cat toc')]:
    fresh(lang,'ask');before=pg.evaluate("()=>JSON.stringify(B.map(b=>[b.d,b.m]))")
    send('ask',q);m=last('ask');ok=len(m.get('chips',[]))>0
    # pick first day if asked, then first time
    if any(c['val'].get('act')=='moveday' for c in m['chips']) and not any(c['val'].get('act')=='movepick' for c in m['chips']): pg.evaluate("()=>{const m=CH.ask.msgs;chatChip('ask',m.length-1,0)}")
    pg.evaluate("()=>{const m=CH.ask.msgs;const i=m.length-1;const j=m[i].chips.findIndex(c=>c.val.act==='movepick');chatChip('ask',i,j)}")
    m=last('ask'); chk(f'move confirm card [{lang}] {q}', m.get('confirm') and m['confirm'].get('move') and pg.evaluate("()=>JSON.stringify(B.map(b=>[b.d,b.m]))")==before, m['text'][:80])
    btn=pg.evaluate("()=>{const e=[...document.querySelectorAll('[data-act=chatbook]')].pop();return e&&e.innerText}")
    chk(f'move button label [{lang}]', btn and btn.strip()==pg.evaluate("()=>t('move')"), btn)
    pg.evaluate("()=>{const m=CH.ask.msgs;const i=m.map(x=>!!x.confirm).lastIndexOf(true);chatBook('ask',i)}")
    after=pg.evaluate("()=>JSON.stringify(B.map(b=>[b.d,b.m]))")
    chk(f'move applied, same count [{lang}] {q}', after!=before and pg.evaluate("()=>B.length")==4, last('ask')['text'][:80])
  # 4. Barre with Yuna chip lands on Yuna
  for lang in ['en','vi','ko']:
    fresh(lang,'book');pg.locator('[data-act=again][data-i="0"]').click();pg.wait_for_timeout(100)
    who=pg.evaluate("()=>[...document.querySelectorAll('.sheet [data-act=slot]')].map(e=>e.innerText.split('\\n').join(' '))")
    chk(f'Yuna chip slots only Yuna [{lang}]', who and all('Yuna' in w for w in who), who[:3])
    pg.locator('.sheet [data-act=slot]').first.click();pg.wait_for_timeout(80)
    chk(f'Yuna chip confirm shows Yuna [{lang}]','Yuna' in pg.evaluate("()=>document.querySelector('.sheet').innerText"))
  # 5. multi-intent
  for lang,q in [('en','haircut and a massage on Saturday'),('vi','cắt tóc và massage thứ bảy'),('ko','토요일에 커트하고 마사지')]:
    fresh(lang,'book');send('book',q);m=last('book')
    chk(f'multi first part progresses with note [{lang}]', m.get('note') and ('“' in m['note']), (m.get('note') or '')[:90]+' | '+m['text'][:60])
    # tap first time chip -> confirm -> book
    for _ in range(3):
      m=last('book')
      if m.get('confirm'): break
      pg.evaluate("()=>{const m=CH.book.msgs;chatChip('book',m.length-1,0)}")
    m=last('book');ok=bool(m.get('confirm'))
    if ok:
      pg.evaluate("()=>{const m=CH.book.msgs;chatBook('book',m.length-1)}")
      m=last('book');nx=[c for c in m.get('chips',[]) if c['val'].get('next')]
      chk(f'multi offers next after booking [{lang}]', nx, [c['label'] for c in m.get('chips',[])])
      if nx:
        pg.evaluate("()=>{const m=CH.book.msgs;const i=m.length-1;chatChip('book',i,m[i].chips.findIndex(c=>c.val.next))}")
        chk(f'multi second request continues [{lang}]', pg.evaluate("()=>{const d=CH.book.draft;return d&&(d.store||d.cands)?1:0}") ,last('book')['text'][:70])
    else: chk(f'multi reached confirm [{lang}]',False,m['text'])
  # 6. KO aliases
  for q,st in [('토요일 오후 린 커트','linh'),('린 디자이너로 커트 예약','linh'),('코이 커트 내일','khoi'),('호아 마사지','hoa'),('유나 바레 내일','yuna')]:
    fresh('ko','book');chk(f'KO alias {q}', pg.evaluate("q=>parse(q).staff",q)==st, pg.evaluate("q=>parse(q).staff",q))
  # 7. notifications
  fresh('en','home')
  d=pg.evaluate("()=>deliver().map(r=>[r.n.type,r.n.s,r.why,r.held||false,r.urgentNow||false,r.at])")
  chk('marketing off by default', all(x[2] for x in d if x[0] in ('nudge','winback','event')), d)
  w=[x for x in d if x[0]=='waitlist'][0];chk('waitlist 21:30 sent right away', not w[2] and not w[3] and w[4] and w[5]==1290, w)
  pg.evaluate("()=>{NSET.types.nudge=true;NSET.types.winback=true;NSET.types.event=true;NSET.optin.capsule=true}")
  d=pg.evaluate("()=>deliver().map(r=>[r.n.type,r.n.s,r.why])")
  chk('opted-in store gets suggestions, others held optin', [x for x in d if x[0]=='nudge' and x[1]=='capsule'][0][2] is None and [x for x in d if x[0]=='nudge' and x[1]=='spa'][0][2]=='optin', d)
  pg.evaluate("()=>{NSET.optin.spa=true;NSET.optin.pickle=true}")
  d=pg.evaluate("()=>deliver().map(r=>[r.n.type,r.n.s,r.n.day,r.why])")
  spa=[x for x in d if x[1]=='spa' and x[0] in ('nudge','winback') and x[3] is None]
  chk('per-store cap 2/week', len(spa)<=2, d)
  chk('global cap 1/day', all(sum(1 for x in d if x[0] in('nudge','winback','event') and x[2]==day and x[3] is None)<=1 for day in range(7)), d)
  pg.evaluate("()=>{ST.page='nset';render()}")
  chk('settings has per-store opt-in switches off', pg.evaluate("()=>[...document.querySelectorAll('[data-act=noptin]')].length>=5"))
  fresh('en','home');pg.evaluate("()=>{ST.page='nset';render()}")
  chk('fresh settings: optins unchecked', pg.evaluate("()=>[...document.querySelectorAll('[data-act=noptin]')].every(e=>!e.checked)") and pg.evaluate("()=>['nudge','winback','event'].every(k=>!document.querySelector(`[data-act=ntype][data-v=${k}]`).checked)"))
  fresh('en','home');feed=pg.evaluate("()=>NFEED.map(n=>n.tx[0]).join(' ')")
  chk('no "spots left" scarcity copy in feed', 'spots left' not in feed and 'only' not in feed.lower())
  # join consent opt-in sets per-store opt-in
  fresh('en','home');pg.evaluate("()=>{joinConsent('nails')}");pg.locator('#optin').check();pg.locator('[data-act=joinok]').click()
  chk('join consent offers box opts store in', pg.evaluate("()=>NSET.optin.nails===true"))
  # 8. free-cancel ended
  fresh('en','home')
  pg.evaluate("()=>{openBook('capsule','barre',{})}")
  txt=pg.evaluate("()=>{BS.d=0;renderBook();return document.querySelector('.sheet').innerText}")
  past=pg.evaluate("()=>slotsFor('capsule','barre',0,{}).filter(z=>!freeNow('capsule',0,z.m)).length")
  chk('slot rows: no past deadline shown', ('Free cancel ended' in txt) if past else True, txt[-200:])
  dl=pg.evaluate("""()=>{let bad=0;for(const sid of ['salon','skin','spa','pickle','capsule'])for(let d=0;d<2;d++){openBook(sid,S[sid].svcs[0].id,{});BS.d=d;renderBook();for(const z of slotsFor(sid,S[sid].svcs[0].id,d,bsOpts())){const x=deadline(sid,d,z.m);if(x.abs<=nowMin()){const e=document.querySelector(`.sheet [data-m="${z.m}"]`);if(e&&e.innerText.includes(fWhen(x.d,x.m)))bad++;}}}closeSheet();return bad}""")
  chk('no expired deadline text anywhere in slot sheets', dl==0, dl)
  # 9. discover accent-insensitive
  for lang in ['en','vi','ko']:
    fresh(lang,'discover')
    for q,exp in [('cat toc','salon'),('cắt tóc','salon'),('mat xa','spa'),('mát xa','spa'),('cham soc da','skin'),('pickleball','pickle'),('lam mong','nails'),('커트','salon'),('may hair','salon')]:
      got=pg.evaluate("q=>{ST.q=q;return discList()}",q); chk(f'discover[{lang}] "{q}" finds {exp}', exp in got, got)
  # 10. call demos
  for lang in ['en','vi','ko']:
    for kind,store in [('court','pickle'),('hair','salon'),('spa','spa')]:
      fresh(lang,'ask');pg.evaluate("()=>openCall()");pg.wait_for_selector('[data-act=callpick]',timeout=15000)
      pg.locator(f'[data-act=callpick][data-v={kind}]').click();pg.wait_for_selector('[data-act=callyes]',timeout=20000)
      caps=pg.evaluate("()=>document.getElementById('caps').innerText")
      pg.locator('[data-act=callyes]').click();pg.wait_for_timeout(200)
      pg.evaluate("()=>endCall()")
      nb=pg.evaluate(f"()=>B.filter(b=>b.store==='{store}'&&b.source==='voice').length")
      chk(f'call {kind} [{lang}] books by voice after Yes', nb==1, caps[-160:])
    fresh(lang,'ask');pg.evaluate("()=>openCall()");pg.wait_for_selector('[data-act=callpick]',timeout=15000)
    pg.locator('[data-act=callpick][data-v=unclear]').click();pg.wait_for_selector('[data-act=callpick]',timeout=20000)
    pg.locator('[data-act=callpick][data-v=unclear]').click()
    pg.wait_for_function("()=>document.getElementById('call').hidden",timeout=30000)
    chk(f'call handoff after 2 misses [{lang}]', pg.evaluate("()=>B.filter(b=>b.source==='voice').length")==0 and pg.evaluate("()=>/Nari|데모/.test(INBOX[0].text)"), pg.evaluate("()=>document.getElementById('toast').innerText"))
  # 11. imported customer
  for lang in ['en','vi','ko']:
    fresh(lang,'home');chk(f'import card shown [{lang}]', pg.locator('[data-act=impok]').count()==1)
    chk(f'import not linked before accept [{lang}]', not pg.evaluate("()=>S.barber.joined"))
    pg.locator('[data-act=impok]').click();chk(f'import accept links + keeps offers off [{lang}]', pg.evaluate("()=>S.barber.joined&&S.barber.visits===2&&!NSET.optin.barber"))
    fresh(lang,'home');pg.locator('[data-act=impno]').click();chk(f'import Not me links nothing [{lang}]', not pg.evaluate("()=>S.barber.joined") and pg.locator('[data-act=impok]').count()==0)
  print('ERR',E)
ok=sum(1 for r in R if r[1]);print('flows',ok,'/',len(R))
for r in R:
  if not r[1]: print('FAIL',r)
json.dump(R,open('/workspace/pr10fix/flows-results.json','w'),ensure_ascii=False,indent=1)
