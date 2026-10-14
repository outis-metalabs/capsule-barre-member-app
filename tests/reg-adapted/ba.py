def _np(b,**k):
  pg=b.new_page(**k);pg.add_init_script("try{localStorage.removeItem('nari.thread')}catch(e){}");return pg
import json,re,sys
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8851/platform-app.html';R={}
def ok(k,c,d=''): R[k]=[bool(c),str(d)[:300]]
OLD=re.compile(r'₫|VND|\bđ\b|Zalo|District|Quận|Thảo Điền|Bình Thạnh|Thủ Đức|Mây Hair|Sen Spa|Lá Nail|Mộc Spa|센 ?스파|마이 ?헤어|라 ?네일|목 ?스파|1군|Motorbike|xe máy')
with sync_playwright() as p:
  b=p.chromium.launch()
  def page(q='',lang=None,w=390):
    pg=_np(b,viewport={'width':w,'height':800});pg.E=[];pg.on('pageerror',lambda e:pg.E.append(str(e)));pg.on('console',lambda m:pg.E.append(m.text) if m.type=='error' else None)
    pg.goto(B+q);pg.evaluate("localStorage.clear()");pg.goto(B+q)
    if lang: pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
    return pg
  pg=page();ok('KR default lang ko',pg.evaluate("L")=='ko',pg.evaluate("L"))
  for lang in ['en','vi','ko']:
    pg=page('',lang);pg.evaluate("()=>{ST.tab='you';ST.page='points';render()}");t=pg.inner_text('#view')  # points detail now opens from the You points line
    ok(f'P1 earned+how [{lang}]',pg.locator('#pv-earned').count() and pg.locator('#pv-how').count(),pg.inner_text('#pv-how') if pg.locator('#pv-how').count() else '')
    ok(f'P3 no bare 0 pts/noCash/claim [{lang}]',not re.search(r'(^|\n)0 ?(points|điểm|포인트)',t) and not re.search('no cash value|giá trị quy đổi tiền mặt|현금 가치',t) and not pg.locator('[data-act=pvclaim]').count(),re.findall(r'.{0,20}0 ?(?:points|điểm|포인트).{0,5}',t)[:3])
    ok(f'P5 no toggle/store app [{lang}]',not pg.locator('#pv-flag').count() and not pg.locator('[data-act=pvstore]').count())
    leg=pg.inner_text('#pv-legacy') if pg.locator('#pv-legacy').count() else '';earned=pg.inner_text('#pv-earned')
    pg.evaluate("()=>{setTab('you');render()}");ban=pg.inner_text('#pv-notes') if pg.locator('#pv-notes').count() else ''  # since PR #15 the migration notice sits at the top of You
    order=pg.evaluate("()=>{const n=document.querySelector('#pv-notes'),h=document.querySelector('.scene,.hero,[class*=hero]');return n&&h?!!(h.compareDocumentPosition(n)&Node.DOCUMENT_POSITION_FOLLOWING):null}")
    nlines=pg.evaluate("()=>{const n=document.querySelector('#pv-notes p');return n?Math.round(n.getBoundingClientRect().height/parseFloat(getComputedStyle(n).lineHeight||20)):0}")
    num=re.findall(r'[\d.,]+',leg)
    ok(f'P4 banner shown on You, not after a hero [{lang}]',bool(ban) and order in (None,True),f'ban={ban!r} earned={earned!r} leg={leg!r} order={order} lines={nlines}')
    ok(f'P4 banner wording consistent [{lang}]',not re.search(r'coins are now points|xu của bạn đã chuyển|코인이 포인트로',ban),ban)
    pg.click('[data-act=pvseen]');pg.reload();pg.evaluate(f"()=>{{setLang('{lang}');render()}}");ok(f'P4 dismissed after reload [{lang}]',not pg.locator('#pv-notes').count())
    # D
    alltxt=''
    for tab in ['home','discover','book','ask','you']:
      pg.evaluate(f"()=>{{ST.tab='{tab}';ST.store=null;render()}}");alltxt+=pg.inner_text('body')+' '.join(pg.evaluate("[...document.querySelectorAll('[aria-label]')].map(e=>e.getAttribute('aria-label'))"))
    for sid in pg.evaluate("Object.keys(S)"):
      pg.evaluate(f"()=>{{ST.store='{sid}';render()}}");alltxt+=pg.inner_text('body')
    ok(f'D3 no "no ads" claim [{lang}]',not re.search(r'no ads|광고 없음|không quảng cáo|không có quảng cáo',alltxt,re.I),re.findall(r'.{0,20}(?:no ads|광고 없음|không (?:có )?quảng cáo).{0,10}',alltxt,re.I)[:3])
    ok(f'D2 no "Ad/광고/Sponsored" label [{lang}]',not re.search(r'\bSponsored\b|\bAd\b|광고|Quảng cáo|Tài trợ',alltxt),re.findall(r'.{0,25}(?:\bSponsored\b|\bAd\b|광고|Quảng cáo|Tài trợ).{0,10}',alltxt)[:4])
    ok(f'Currency KR consistent [{lang}]',not OLD.search(alltxt) and '₩' in alltxt,sorted(set(OLD.findall(alltxt))))
    pg.evaluate("()=>{ST.tab='discover';ST.store=null;render()}")
    # PR #14: real (sample) photos; a store without a photo, or a failed load, falls back to brand tint + initials. Never a spinner.
    ok(f'D1 discover photos (initials fallback), no spinner [{lang}]',pg.evaluate("()=>{const ph=[...document.querySelectorAll('.dphoto')];return ph.length>0&&ph.every(e=>!e.querySelector('.spin')&&((e.querySelector('img.dimg[alt]')&&e.querySelector('img.dimg').alt.length>3)||(e.classList.contains('dinit')&&e.querySelector('span')&&!e.querySelector('svg'))))&&ph.some(e=>e.querySelector('img.dimg'))}"))
    ok(f'D1b discover photos actually loaded (naturalWidth > 0) [{lang}]',pg.evaluate("async()=>{const im=[...document.querySelectorAll('.dphoto img.dimg')].filter(i=>{const r=i.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0});if(!im.length)return false;await Promise.all(im.map(i=>i.decode().catch(()=>0)));return im.every(i=>i.complete&&i.naturalWidth>0)}"))
    # H
    for cid in ['ask','book']:
      pg.evaluate(f"()=>{{ST.tab='{cid}';render()}}")
      ok(f'H1 no red bar, help link [{lang}|{cid}]',not pg.locator('.sosbar').count() and pg.locator('[data-act=helpsheet]').count()==1 and pg.evaluate("()=>{const h=document.querySelector('[data-act=helpsheet]'),f=document.querySelector('.chatbox');return !!(f.compareDocumentPosition(h)&Node.DOCUMENT_POSITION_FOLLOWING)&&!/rgb\\((1[5-9]\\d|2\\d\\d), ?\\d{1,2}, ?\\d{1,2}\\)/.test(getComputedStyle(h).color)}"),pg.evaluate("()=>getComputedStyle(document.querySelector('[data-act=helpsheet]')).color"))
    pg.evaluate("()=>{ST.tab='ask';render()}");pg.click('[data-act=helpsheet]');hs=pg.inner_text('.sheet')
    ok(f'H2 help sheet guidance, no number [{lang}]',not re.search(r'\d{3}',hs) and re.search(r'doctor|bác sĩ|의사',hs) and re.search(r'instructor|huấn luyện|강사',hs),hs[:200])
    pg.close()
  # H3/H4/N via chat
  P={'en':{'N':["Is it okay to go to barre alone for the first time?","What should I wear to barre?","How early should I arrive for barre?","What should I wear for a massage at Soom Spa?"],'H3':["I have chest pain during class","I feel dizzy and might faint"],'H4':["i want to take my own life"],'H5':["book a haircut"]},
     'vi':{'N':["Lần đầu đi barre một mình được không?","Đi barre nên mặc gì?","Nên đến sớm bao lâu cho lớp barre?"],'H3':["Tôi bị đau ngực khi tập"],'H4':["tôi muốn tự tử"],'H5':["đặt lịch cắt tóc"]},
     'ko':{'N':["처음인데 바레 혼자 가도 괜찮아요?","바레 갈 때 뭐 입어요?","바레 몇 분 전에 가야 돼요?","소옴 스파 마사지 받을 때 뭐 입어요?"],'H3':["수업 중에 가슴이 아파요"],'H4':["죽고 싶어요"],'H5':["커트 예약"]}}
  for lang,d in P.items():
    for cid in ['ask','book']:
      for kind,qs in d.items():
        for q in qs:
          pg=page('',lang);pg.evaluate(f"()=>{{ST.tab='{cid}';render()}}");pg.evaluate("([c,q])=>__plat.chatSend(c,q)",[cid,q]);pg.wait_for_timeout(60)
          m=pg.evaluate(f"()=>{{const m=CH['{cid}'].msgs;return m[m.length-1]}}");txt=m.get('text','');chips=[c['label'] for c in m.get('chips') or []]
          ent=f'{kind} [{lang}|{cid}] {q}'
          if kind=='N': ok(ent,m.get('faq') or re.search(r"don't have that|không có điều này|정보에 그 내용",txt),txt[:160]+' | '+str(chips))
          elif kind in('H3','H4'): ok(ent,not re.search(r'\d{3}',txt) and not m.get('confirm') and not any(re.search(r'\d{1,2}:\d\d|Book|Đặt|예약|point|điểm|포인트',c) for c in chips) and not re.search(r'point|điểm|포인트',txt),txt[:160]+' | '+str(chips))
          else: ok(ent,not re.search(r'doctor|emergency|bác sĩ|cấp cứu|의사|응급|stop exercising',txt,re.I),txt[:120])
          pg.close()
  # VN market & demo mode
  pg=page('?market=vn','en');t=pg.inner_text('body');pg.evaluate("()=>{ST.tab='you';render()}");t+=pg.inner_text('body');ok('market=vn: ₫, no ₩',('₫' in t) and '₩' not in t)
  pg=page('?demo=1','en');pg.evaluate("()=>{ST.tab='you';ST.page='points';render()}");ok('?demo=1 shows toggle+store app',pg.locator('#pv-flag').count() and pg.locator('[data-act=pvstore]').count())
  pg=page('?realRewards=1','ko');pg.evaluate("()=>{ST.tab='you';ST.page='vouchers';ST.vseg='more';render()}");t=pg.inner_text('body');ok('flag on KO: vouchers in ₩, no ₫',('₩' in t) and '₫' not in t,re.findall(r'.{0,15}[₩₫].{0,5}',t)[:5])
json.dump(R,open('ba.json','w'),ensure_ascii=False,indent=1)
print(sum(v[0] for v in R.values()),'/',len(R))
for k,v in R.items():
  if not v[0]: print('FAIL',k,v[1])
