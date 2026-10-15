# Video Report Script — Cici Gamification Update

**Date:** 2026-10-15  
**Project:** AICC MVP — platform-app.html (`feat/cici-gamification`)  
**Format:** Screen recording, ~3 min, no voiceover, 3-panel layout (nav left / phone center / annotation right)  
**Reference:** `bao-cao-hana.mp4`  
**Audience:** Internal — báo cáo sếp

---

## Update Highlights (text gửi kèm)

So với phiên bản cũ platform-app, bản này bổ sung:

1. **Onboarding màn hình chào** — hiện 1 lần khi mở lần đầu, tặng 50 🪙 (lưu localStorage)
2. **Cici Coins (🪙)** — tiền xu trang trí riêng biệt, không liên quan điểm thưởng
3. **Cici Shop** — 17 items: hình nền (4), khung avatar (4), companion (4), nhạc (3), boost (2)
4. **Mua & trang trí realtime** — equip item → thay đổi ngay trên app (bg, frame, companion badge)
5. **Missions có nút Demo ›** — attend & new place có thể demo nhanh không cần đặt lịch thật
6. **Kiếm coins từ missions** — stretch +10 🪙, attend +20 🪙, new place +30 🪙
7. **Chỉnh tên profile** — edit name từ tab You

---

## Structure: Two Acts

```
HỒI 1: Lần đầu mở app   (~1:20)  screens 1–5
HỒI 2: Nhiệm vụ & kiếm coins  (~1:00)  screens 6–10
HỒI 3: Shop & trang trí    (~0:50)  screens 11–16
```

---

## Scene-by-Scene Script

### HỒI 1 — Lần đầu mở app (~1:20)

| # | Nav (trái) | Annotation (phải) | Update |
|---|-----------|-------------------|--------|
| 1 | Intro | Màn hình chào. Hai lựa chọn: đăng nhập hoặc mở app thành viên. | — |
| 2 | Onboarding | App chào thành viên mới — Cici xuất hiện, giới thiệu 3 tính năng chính. | 🆕 Màn hình onboarding mới, chỉ hiện 1 lần |
| 3 | Nhận 50 🪙 | Bấm "Bắt đầu" → nhận 50 Cici Coins. Pill +50 🪙 nổi lên. | 🆕 Hệ thống Cici Coins (tách biệt với điểm thưởng) |
| 4 | Đăng nhập | Form đăng nhập — phone + password. Unchanged. | — |
| 5 | Home | Tab Today: thấy ngay 3 nhiệm vụ hàng ngày + số coins hiện tại. | 🆕 Coins badge trên mission card |

**Actions cần thực hiện:**
- Xóa localStorage (`cici.ob`) trước khi quay để onboarding hiện lại
- Bấm "Member app" (không phải "Đã có tài khoản")
- Đọc qua 3 bước onboarding → bấm "Bắt đầu · +50 🪙"
- Đăng nhập bình thường

---

### HỒI 2 — Nhiệm vụ & kiếm coins (~1:00)

| # | Nav (trái) | Annotation (phải) | Update |
|---|-----------|-------------------|--------|
| 6 | Stretch | Bấm Start → sheet giãn cơ với Cici, đếm ngược. Bấm Finish (demo). | — |
| 7 | Stretch done | Confetti + toast: điểm thưởng **và** +10 🪙. | 🆕 Missions giờ tặng coins |
| 8 | Attend demo | Bấm "Demo ›" trên nhiệm vụ Attend → check-in tức thì, +20 🪙. | 🆕 Nút Demo để demo nhanh |
| 9 | New place demo | Bấm "Demo ›" trên New place → +30 🪙. | 🆕 |
| 10 | Coins tích lũy | Coins counter trên card tăng: 120 → 130 → 150 → 180 🪙. | — |

**Actions cần thực hiện:**
- Mission card hiển thị 🪙 110 sau khi hoàn thành cả 3
- Dừng 1 giây ở mỗi toast để annotation đọc kịp

---

### HỒI 3 — Shop & trang trí (~0:50)

| # | Nav (trái) | Annotation (phải) | Update |
|---|-----------|-------------------|--------|
| 11 | Tab You | Profile: avatar chữ cái, tên, điểm — và nút Shop mới. | 🆕 Avatar initials + nút Shop |
| 12 | Cici Shop | 17 items: hình nền / khung / companion / nhạc / boost. Filter theo loại. | 🆕 Toàn bộ shop mới |
| 13 | Mua Sakura bg | Bấm Buy (80 🪙) → toast xác nhận, coins trừ. | 🆕 |
| 14 | Equip & live | Bấm Equip → nền app đổi sang hoa anh đào ngay lập tức. | 🆕 Áp dụng realtime |
| 15 | Equip frame | Mua Gold frame → khung avatar đổi màu vàng. | 🆕 |
| 16 | Companion | Equip Cat companion → badge 🐱 hiện trên màn hình Cici. | 🆕 |

**Actions cần thực hiện:**
- Từ tab You → bấm "🪙 110 coins..."
- Filter chip "Nền" → mua Sakura (80 🪙)
- Filter chip "Khung" → mua Gold frame (120 🪙) — cần đủ coins: tổng có 110, gold = 120 → **mua Silver frame (60 🪙) thay thế**
- Filter chip "Bạn đồng hành" → mua + equip Cat
- Quay lại tab Cici để thấy badge 🐱

---

## Pre-recording Checklist

- [ ] Mở `platform-app.html` trên Chrome, zoom phù hợp
- [ ] Xóa localStorage key `cici.ob` (DevTools → Application → Local Storage → delete)
- [ ] Set `ST.shopCoins = 70` qua DevTools Console trước khi bắt đầu quay (không đổi code) — xem Coin Budget bên dưới
- [ ] Coins sau missions: 70 + 50 + 10 + 20 + 30 = 180 🪙 → đủ mua Sakura (80) + Silver frame (60) + Cat (40)
- [ ] Test run 1 lần trước khi record

---

## Coin Budget (demo path)

| Event | Delta | Balance |
|-------|-------|---------|
| Start (default tăng lên 70) | +70 | 70 🪙 |
| Onboarding done | +50 | 120 🪙 |
| Stretch mission | +10 | 130 🪙 |
| Attend demo | +20 | 150 🪙 |
| New place demo | +30 | 180 🪙 |
| Buy Sakura bg (80) | -80 | 100 🪙 |
| Buy Silver frame (60) | -60 | 40 🪙 |
| Buy Cat companion (40) | -40 | **0 🪙** ✓ |

---

## Out of Scope

- Member acquisition flow (discover → shop-profile → trial → convert) — chưa implement, không demo
- Cici AI chat tab — giữ nguyên từ bản cũ, không cần highlight
