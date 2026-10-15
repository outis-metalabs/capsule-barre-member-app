"""PR19-5: the payment reply lists KR methods (card, KakaoPay, Naver Pay, Toss) in the KR market and MoMo only in VN. Usage: pay_market.py [base_url]"""
import sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
R = []; ok = lambda n, c, d='': (R.append(c), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {d}')))
Q = {'en': ['Can I pay with MoMo?', 'do you take kakao pay'], 'vi': ['Thanh toán bằng MoMo được không?'], 'ko': ['모모로 결제돼요?', '카카오페이 돼요?', '간편결제 되나요?']}
with sync_playwright() as p:
  b = p.chromium.launch()
  for mk in ['kr', 'vn']:
    for lang, qs in Q.items():
      for q in qs:
        g = b.new_page(viewport={'width': 390, 'height': 844}); u = U + ('?market=vn' if mk == 'vn' else '')
        g.goto(u); g.evaluate('localStorage.clear()'); g.goto(u); g.wait_for_timeout(200)
        g.evaluate(f"()=>{{setLang('{lang}');go('tab:cici');__plat.chatSend('cici',{q!r})}}"); g.wait_for_timeout(150)
        t = g.evaluate("[...document.querySelectorAll('#th-cici .msg.n')].pop().innerText")
        if mk == 'kr': ok(f'KR [{lang}] {q}: KR methods, no MoMo', all(w in t for w in (['카드','카카오페이','네이버페이','토스'] if lang=='ko' else ['KakaoPay','Naver Pay','Toss'])) and not any(w in t for w in ['MoMo','모모']), t)
        else: ok(f'VN [{lang}] {q}: MoMo, no KR wallets', 'MoMo' in t and not any(w in t for w in ['KakaoPay','카카오페이','Toss','토스']), t)
        g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
