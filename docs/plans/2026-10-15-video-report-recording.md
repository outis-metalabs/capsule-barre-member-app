# Video Report Recording Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Quay video báo cáo ~3 phút trên `bao-cao-platform.html` trình bày tất cả tính năng mới của `feat/cici-gamification`.

**Architecture:** Mở `bao-cao-platform.html` trong Chrome → click qua app trong iframe → gọi `window.setCap()` từ DevTools console để cập nhật caption sau mỗi cảnh → screen record toàn bộ.

**Tech Stack:** Chrome, QuickTime Player (hoặc bất kỳ screen recorder nào), DevTools console

---

### Task 1: Cài đặt màn hình ghi

**Files:**
- Open: `capsule-barre-member-app/bao-cao-platform.html`

- [ ] **Step 1: Mở Chrome, điều hướng đến file**

  ```
  File → Open File → capsule-barre-member-app/bao-cao-platform.html
  ```

  Hoặc kéo thả file vào Chrome. App load trong iframe ở giữa, caption box phía dưới.

- [ ] **Step 2: Resize cửa sổ Chrome**

  Kéo cửa sổ Chrome ra full màn hình (không phải fullscreen F11, chỉ maximize). Caption và phone phải thấy đủ trong frame.

- [ ] **Step 3: Mở DevTools console và giữ mở**

  Phím tắt: `⌘ + Option + J` (Mac) / `Ctrl + Shift + J` (Windows)

  Dock console sang **bên phải** (click ⋮ trong DevTools → Dock side → Dock to right) để không che khuất demo.

- [ ] **Step 4: Bật screen recorder**

  - **QuickTime:** File → New Screen Recording → chọn vùng cửa sổ Chrome (không record DevTools console nếu dock right)
  - **Hoặc:** OBS / Loom / bất kỳ tool nào tương tự
  - **Quan trọng:** Chỉ capture vùng chứa phone + caption, KHÔNG capture DevTools

  > Chưa bấm Record ngay — xong Task 2 mới bắt đầu quay.

---

### Task 2: Reset trạng thái app trước khi quay

- [ ] **Step 1: Mở DevTools Application tab để xóa localStorage**

  Trong DevTools: Tab **Application** → **Local Storage** → click vào origin → tìm key `cici.ob` → Delete (hoặc right-click → Delete)

  Mục đích: Onboarding hiện lại (key này được set khi bấm "Bắt đầu" lần đầu).

- [ ] **Step 2: Set coins ban đầu về 70 qua console**

  Chuyển về tab **Console**, paste lệnh sau:

  ```js
  document.getElementById("appframe").contentWindow.ST.shopCoins = 70; document.getElementById("appframe").contentWindow.render();
  ```

  Expected: Không có lỗi. App re-render, nếu đang ở home sẽ thấy coins đổi.

- [ ] **Step 3: Reload iframe về màn hình Intro**

  ```js
  document.getElementById("appframe").src = "platform-app.html?lang=en";
  ```

  Expected: Iframe reload, Onboarding screen hiện ra (vì `cici.ob` đã xóa).

- [ ] **Step 4: Set caption ban đầu**

  ```js
  setCap("Cici · member app", "Tính năng mới", "feat/cici-gamification — báo cáo cập nhật.");
  ```

- [ ] **Step 5: Bắt đầu screen recording**

  Bấm Record trong QuickTime / OBS / Loom.

  Dừng 2 giây ở màn hình intro để caption đầu tiên hiện rõ trước khi bắt đầu click.

---

### Task 3: Record Hồi 1 — Lần đầu mở app (scenes 1–5)

Mỗi scene: gọi `setCap()` trước → click vào iframe → dừng 2–3 giây.

- [ ] **Scene 1 — Intro**

  Trong iframe đang hiện Onboarding. Cuộn lên xem màn hình chào nếu cần. Gọi:

  ```js
  setCap("Intro", "Màn hình chào", "Hai lựa chọn: đăng nhập hoặc khám phá app thành viên.");
  ```

  Dừng 3 giây.

- [ ] **Scene 2 — Onboarding (🆕)**

  ```js
  setCap("🆕 Onboarding", "Chào mừng thành viên mới", "Cici giới thiệu 3 tính năng. Màn hình này chỉ hiện đúng 1 lần — lưu qua localStorage.");
  ```

  Trong iframe: scroll qua 3 bước onboarding. Dừng 3 giây.

- [ ] **Scene 3 — Nhận 50 🪙 (🆕)**

  ```js
  setCap("🆕 Cici Coins", "Nhận 50 🪙 khi bắt đầu", "Cici Coins là tiền xu trang trí — hoàn toàn tách biệt với điểm thưởng.");
  ```

  Trong iframe: bấm nút **"Bắt đầu · +50 🪙"**. Pill `+50 🪙` nổi lên. Dừng 3 giây.

- [ ] **Scene 4 — Đăng nhập**

  ```js
  setCap("Auth", "Đăng nhập", "Form phone + password. Luồng xác thực không thay đổi.");
  ```

  Trong iframe: điền số phone mẫu + password → bấm **Get code** → nhập code 6 chữ số → **Continue**. Dừng 2 giây.

- [ ] **Scene 5 — Home (🆕 coins badge)**

  ```js
  setCap("🆕 Home", "Nhiệm vụ hàng ngày + Coins", "Mission card giờ hiện số Cici Coins hiện tại. 3 nhiệm vụ: Stretch, Attend, New place.");
  ```

  Trong iframe: xem tab Today, thấy mission card với `🪙 120`. Dừng 3 giây.

---

### Task 4: Record Hồi 2 — Nhiệm vụ & kiếm coins (scenes 6–10)

- [ ] **Scene 6 — Stretch**

  ```js
  setCap("Missions", "Stretch — giãn cơ 2 phút", "Bấm Start để mở sheet giãn cơ với Cici và đồng hồ đếm ngược.");
  ```

  Trong iframe: bấm **Start** trên mission Stretch. Sheet mở ra. Dừng 2 giây.

- [ ] **Scene 7 — Stretch done (🆕 +10 🪙)**

  ```js
  setCap("🆕 Missions", "Hoàn thành → nhận điểm + coins", "Missions giờ tặng cả điểm thưởng lẫn Cici Coins. Stretch: +10 🪙.");
  ```

  Trong iframe: bấm **Finish (demo: skip the timer)**. Confetti + toast hiện. Dừng 3 giây.

- [ ] **Scene 8 — Attend demo (🆕 Demo ›)**

  ```js
  setCap("🆕 Missions", "Attend — nút Demo để demo nhanh", "Không cần lịch đặt thật. Bấm Demo › để simulate check-in tức thì. +20 🪙.");
  ```

  Trong iframe: bấm **Demo ›** trên mission **Attend**. Toast `+20 🪙` hiện. Dừng 3 giây.

- [ ] **Scene 9 — New place demo (🆕 Demo ›)**

  ```js
  setCap("🆕 Missions", "New place — thử studio mới", "Bấm Demo › simulate visit mới. +30 🪙.");
  ```

  Trong iframe: bấm **Demo ›** trên mission **New place**. Toast `+30 🪙` hiện. Dừng 3 giây.

- [ ] **Scene 10 — Coins tích lũy**

  ```js
  setCap("Coins", "Tổng kết coins", "Sau 3 nhiệm vụ: 120 → 130 → 150 → 180 🪙. Sẵn sàng vào shop.");
  ```

  Trong iframe: scroll lên mission card, chỉ vào `🪙 180`. Dừng 3 giây.

---

### Task 5: Record Hồi 3 — Shop & trang trí (scenes 11–16)

- [ ] **Scene 11 — Tab You (🆕 initials + Shop)**

  ```js
  setCap("🆕 You", "Profile mới", "Avatar chữ cái thay ảnh. Nút shop hiện số coins. Tên có thể chỉnh sửa.");
  ```

  Trong iframe: bấm tab **You** (bottom nav). Thấy avatar initials + `🪙 180 coins...`. Dừng 3 giây.

- [ ] **Scene 12 — Cici Shop (🆕 toàn bộ)**

  ```js
  setCap("🆕 Cici Shop", "17 items trang trí", "Hình nền · Khung avatar · Bạn đồng hành · Nhạc · Boost. Lọc theo loại.");
  ```

  Trong iframe: bấm **🪙 180 coins...**. Shop mở. Click từng filter chip để thấy các danh mục. Dừng 4 giây.

- [ ] **Scene 13 — Mua Sakura bg (🆕)**

  ```js
  setCap("🆕 Shop", "Mua hình nền Sakura — 80 🪙", "Coins trừ ngay, item vào inventory.");
  ```

  Trong iframe: filter **Nền** → bấm **Buy** trên Sakura (80 🪙). Toast xác nhận. Dừng 3 giây.

- [ ] **Scene 14 — Equip Sakura (🆕 realtime)**

  ```js
  setCap("🆕 Shop", "Equip → đổi nền ngay lập tức", "Không cần reload. Background thay đổi realtime trên toàn app.");
  ```

  Trong iframe: bấm **Equip** trên Sakura. Nền app đổi sang hoa anh đào. Dừng 3 giây.

- [ ] **Scene 15 — Silver frame (🆕)**

  ```js
  setCap("🆕 Shop", "Khung avatar — Silver frame — 60 🪙", "Equip → viền bạc xuất hiện quanh avatar chữ cái.");
  ```

  Trong iframe: filter **Khung** → Buy Silver frame (60 🪙) → Equip. Quay lại **You** tab để thấy khung. Dừng 3 giây.

- [ ] **Scene 16 — Cat companion (🆕)**

  ```js
  setCap("🆕 Shop", "Bạn đồng hành — Cat — 40 🪙", "Equip → badge 🐱 xuất hiện trên màn hình Cici.");
  ```

  Trong iframe: filter **Bạn đồng hành** → Buy Cat (40 🪙) → Equip → bấm tab **Cici** (hoặc tab có Cici). Badge 🐱 hiện. Dừng 3 giây.

---

### Task 6: Kết thúc & xuất file

- [ ] **Step 1: Set caption kết thúc**

  ```js
  setCap("feat/cici-gamification", "Tổng kết", "Onboarding · Cici Coins · Item Shop · Mission demo shortcuts · Equip realtime.");
  ```

  Dừng 4 giây cho caption đọc kịp.

- [ ] **Step 2: Dừng screen recording**

  Bấm Stop trong QuickTime / OBS / Loom.

- [ ] **Step 3: Trim**

  - Xóa phần đầu trước khi caption Scene 1 hiện ổn định (< 1 giây)
  - Xóa phần cuối sau 4 giây caption kết thúc
  - Cắt bỏ bất kỳ đoạn nào bấm nhầm hoặc lag

- [ ] **Step 4: Export**

  Lưu thành: `bao-cao-platform-v2.mp4`

  Recommend: H.264, 1080p, ~12MB (tương đương bao-cao-hana.mp4)

---

## Cheatsheet Console — Dán sẵn trước khi quay

Copy paste block này vào console để có tất cả `setCap` calls sẵn sàng:

```js
// === PRE-RECORDING SETUP ===
// 1. Xóa cici.ob trong Application → Local Storage
// 2. Reload iframe:
document.getElementById("appframe").src = "platform-app.html?lang=en";
// 3. Sau khi iframe load xong, set coins (chạy lần này):
// document.getElementById("appframe").contentWindow.ST.shopCoins = 70;
// document.getElementById("appframe").contentWindow.render();

// === CAPTIONS — chạy từng cái theo thứ tự ===
// S1:  setCap("Intro", "Màn hình chào", "Hai lựa chọn: đăng nhập hoặc khám phá app thành viên.");
// S2:  setCap("🆕 Onboarding", "Chào mừng thành viên mới", "Cici giới thiệu 3 tính năng. Chỉ hiện 1 lần — lưu qua localStorage.");
// S3:  setCap("🆕 Cici Coins", "Nhận 50 🪙 khi bắt đầu", "Cici Coins là tiền xu trang trí — tách biệt với điểm thưởng.");
// S4:  setCap("Auth", "Đăng nhập", "Form phone + password. Luồng xác thực không thay đổi.");
// S5:  setCap("🆕 Home", "Nhiệm vụ hàng ngày + Coins", "Mission card hiện số Cici Coins. 3 nhiệm vụ: Stretch, Attend, New place.");
// S6:  setCap("Missions", "Stretch — giãn cơ 2 phút", "Bấm Start để mở sheet giãn cơ với Cici và đồng hồ đếm ngược.");
// S7:  setCap("🆕 Missions", "Hoàn thành → nhận điểm + coins", "Missions giờ tặng cả điểm thưởng lẫn Cici Coins. Stretch: +10 🪙.");
// S8:  setCap("🆕 Missions", "Attend — nút Demo để demo nhanh", "Không cần lịch đặt thật. Demo › simulate check-in tức thì. +20 🪙.");
// S9:  setCap("🆕 Missions", "New place — thử studio mới", "Bấm Demo › simulate visit mới. +30 🪙.");
// S10: setCap("Coins", "Tổng kết coins", "Sau 3 nhiệm vụ: 120 → 130 → 150 → 180 🪙. Sẵn sàng vào shop.");
// S11: setCap("🆕 You", "Profile mới", "Avatar chữ cái thay ảnh. Nút shop hiện số coins. Tên có thể chỉnh sửa.");
// S12: setCap("🆕 Cici Shop", "17 items trang trí", "Hình nền · Khung avatar · Bạn đồng hành · Nhạc · Boost. Lọc theo loại.");
// S13: setCap("🆕 Shop", "Mua hình nền Sakura — 80 🪙", "Coins trừ ngay, item vào inventory.");
// S14: setCap("🆕 Shop", "Equip → đổi nền ngay lập tức", "Không cần reload. Background thay đổi realtime trên toàn app.");
// S15: setCap("🆕 Shop", "Khung avatar — Silver frame — 60 🪙", "Equip → viền bạc xuất hiện quanh avatar chữ cái.");
// S16: setCap("🆕 Shop", "Bạn đồng hành — Cat — 40 🪙", "Equip → badge 🐱 xuất hiện trên màn hình Cici.");
// END: setCap("feat/cici-gamification", "Tổng kết", "Onboarding · Cici Coins · Item Shop · Mission demo shortcuts · Equip realtime.");
```
