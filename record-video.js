const { chromium } = require('playwright');
const APP = 'http://127.0.0.1:8767';
const PAUSE = ms => new Promise(r => setTimeout(r, ms));

async function cap(page, kicker, title, line) {
  await page.evaluate(([k,t,l]) => setCap(k,t,l), [kicker, title, line]);
}

async function clk(fl, sel, timeout=8000) {
  const el = fl.locator(sel).first();
  await el.waitFor({ state:'visible', timeout });
  await PAUSE(100);
  await el.click();
  console.log(' ✓', sel.slice(0,60));
}

async function tryClk(fl, sel) {
  try { await clk(fl, sel, 2000); return true; }
  catch { return false; }
}

async function shopBuyEquip(page, fl, fr, itemId, filterK) {
  // Reliable buy+equip: set filter via evaluate, then click buy/equip
  await fr.evaluate(k => { ST.shopFilter = k; render(); }, filterK);
  await PAUSE(600);

  // Check if already owned (show equip instead of buy)
  const owned = await fr.evaluate(id => ST.shopInventory.includes(id), itemId);
  console.log(`  ${itemId} owned:${owned} coins:${await fr.evaluate(() => ST.shopCoins)}`);

  if (!owned) {
    await clk(fl, `[data-act="buy-shopitem"][data-id="${itemId}"]`);
    await PAUSE(1000);
  }
  // Equip
  await clk(fl, `[data-act="equip-shopitem"][data-id="${itemId}"]`);
  await PAUSE(500);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 700, height: 960 },
    recordVideo: { dir: '/tmp/pwvideo/', size: { width: 700, height: 960 } }
  });
  const page = await ctx.newPage();

  console.log('Loading...');
  await page.goto(`${APP}/bao-cao-platform.html`);
  const appFL = page.frameLocator('iframe#appframe');
  await appFL.locator('#view').waitFor({ state:'visible', timeout:15000 });
  await PAUSE(1500);
  console.log('Iframe loaded');

  const fr = page.frames().find(f => f.url().includes('platform-app'));
  await fr.waitForFunction(() => typeof ST !== 'undefined' && ST.shopCoins !== undefined, { timeout:10000 });

  await fr.evaluate(() => {
    try { localStorage.removeItem('cici.ob'); } catch(e){}
    ST.shopCoins = 150;
    ST.firstRun = true;
    ST.miss = { stretch:false, attend:false, newplace:false };
    ST.shopInventory = [];
    ST.shopEquipped = { bg:null, frame:null, companion:null, music:null };
    ST.page = 'onboard';
    render();
  });
  await PAUSE(1500);
  console.log('State reset. coins =', await fr.evaluate(() => ST.shopCoins));

  // ── HỒI 1 ──────────────────────────────────
  await cap(page,'Intro','Màn hình chào','Thành viên mới mở app lần đầu. Cici chào và giới thiệu tính năng.');
  await PAUSE(3000);

  await cap(page,'🆕 Onboarding','Chào mừng thành viên mới','Màn hình mới — xuất hiện đúng 1 lần, lưu qua localStorage.');
  await PAUSE(3000);

  await cap(page,'🆕 Cici Coins','Nhận 50 🪙 khi bắt đầu','Cici Coins là tiền xu trang trí — tách biệt với điểm thưởng.');
  await clk(appFL, '[data-act="onboard-done"]');
  await PAUSE(3000);

  await cap(page,'🆕 Home','Nhiệm vụ hàng ngày + Coins','Mission card hiển thị số Cici Coins. 3 nhiệm vụ: Stretch, Attend, New place.');
  await PAUSE(3500);

  // ── HỒI 2 ──────────────────────────────────
  await cap(page,'Missions','Stretch — giãn cơ 2 phút','Bấm Start → sheet giãn cơ với Cici và đồng hồ đếm ngược.');
  await clk(appFL, '[data-act="stretch"]');
  await PAUSE(3000);

  await cap(page,'🆕 Missions','Hoàn thành → điểm + coins','Missions tặng điểm thưởng lẫn Cici Coins. Stretch: +10 🪙.');
  await clk(appFL, '[data-act="stretchdone"]');
  await PAUSE(3500);
  await tryClk(appFL, '[data-act="close"]');
  await PAUSE(500);

  await cap(page,'🆕 Missions','Attend — nút Demo để demo nhanh','Demo › simulate check-in tức thì. +20 🪙.');
  await clk(appFL, '[data-act="attend-demo"]');
  await PAUSE(3000);
  await tryClk(appFL, '[data-act="close"]');
  await PAUSE(400);

  await cap(page,'🆕 Missions','New place — thử studio mới','Demo › simulate visit mới. +30 🪙.');
  await clk(appFL, '[data-act="newplace-demo"]');
  await PAUSE(3000);

  await cap(page,'Coins','Tổng kết coins hôm nay','Sau 3 nhiệm vụ: 200→210→230→260 🪙. Sẵn sàng vào shop.');
  await PAUSE(3500);

  // ── HỒI 3 ──────────────────────────────────
  await cap(page,'🆕 You','Profile mới','Avatar chữ cái thay ảnh. Nút shop hiện số coins. Tên có thể chỉnh sửa.');
  await clk(appFL, '[data-act="tab"][data-v="you"]');
  await PAUSE(3000);

  // Open shop, browse filters
  await cap(page,'🆕 Cici Shop','17 items trang trí','Hình nền · Khung · Companion · Nhạc · Boost. Lọc theo loại.');
  await clk(appFL, '[data-act="open-shop"]');
  await PAUSE(1500);
  for (const k of ['frame','companion','bg']) {
    await fr.evaluate(k => { ST.shopFilter = k; render(); }, k);
    await PAUSE(700);
  }

  // Buy & equip Sakura
  await cap(page,'🆕 Shop','Mua hình nền Sakura — 80 🪙','Coins trừ ngay, item vào inventory.');
  await shopBuyEquip(page, appFL, fr, 'bg-sakura', 'bg');
  await PAUSE(1000);

  // Show equip live
  await cap(page,'🆕 Shop','Equip → đổi nền ngay lập tức','Không cần reload. Background thay đổi realtime.');
  await PAUSE(3000);

  // Silver frame
  await cap(page,'🆕 Shop','Khung avatar — Silver frame — 60 🪙','Equip → viền bạc xuất hiện quanh avatar chữ cái.');
  await shopBuyEquip(page, appFL, fr, 'frame-silver', 'frame');
  await PAUSE(1000);

  // Back to You → show framed avatar
  await clk(appFL, '[data-act="back"]');
  await PAUSE(2500);

  // Cat companion
  await cap(page,'🆕 Shop','Bạn đồng hành — Lucky Cat — 100 🪙','Equip → badge 🐱 xuất hiện trên màn hình Cici.');
  await clk(appFL, '[data-act="open-shop"]');
  await PAUSE(1000);
  await shopBuyEquip(page, appFL, fr, 'comp-cat', 'companion');
  await PAUSE(1000);
  await clk(appFL, '[data-act="back"]');
  await PAUSE(500);
  await tryClk(appFL, '[data-act="tab"][data-v="cici"]');
  await PAUSE(3000);

  // End
  await cap(page,'feat/cici-gamification','Tổng kết','Onboarding · Cici Coins · Item Shop 17 items · Demo shortcuts · Equip realtime.');
  await PAUSE(4000);

  console.log('Done. Final coins:', await fr.evaluate(() => ST.shopCoins));
  const vidPath = await page.video().path();
  await ctx.close();
  await browser.close();
  console.log('WebM:', vidPath);

  const { execSync } = require('child_process');
  const out = '/Users/josh/Downloads/aicc_mvp/capsule-barre-member-app/bao-cao-platform-v2.mp4';
  execSync(`ffmpeg -i "${vidPath}" -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p "${out}" -y`, { stdio:'inherit' });
  console.log('✓ MP4 saved:', out);
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
