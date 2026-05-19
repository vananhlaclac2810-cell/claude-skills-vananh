---
name: fb-actionable-post-core
description: Bộ nguyên tắc nền tảng để viết bài Facebook dạng actionable list post tiếng Việt — hook, scan-ability mobile, ẩn dụ sinh động, chốt cảm xúc, công thức ngôn ngữ Việt, anti-patterns. Dùng skill này MỖI KHI người dùng yêu cầu viết, biên tập, hoặc cải thiện bài Facebook dạng danh sách (list post, bài liệt kê, bài cẩm nang, bài "X điều cần biết", "đặc sản", "dấu hiệu nhận biết"), kể cả khi họ không gọi tên cụ thể. Cũng kích hoạt khi từ khoá xuất hiện: "viết bài FB", "viết caption", "bài liệt kê", "list post", "viral post", "bài đăng fanpage", "content Facebook", "viết content mẹ bỉm", "viết content cho fanpage". Hai skill chuyên biệt `fb-megalist-post` và `fb-relatable-numbered-post` đều tham chiếu vào đây — nếu một trong hai đang được dùng, MẶC ĐỊNH đọc thêm skill này.
---

# Core: Facebook Actionable List Post (tiếng Việt)

Đây là bộ **nguyên tắc nền tảng** dùng cho mọi bài Facebook dạng list post tiếng Việt. Hai skill chị em (`fb-megalist-post`, `fb-relatable-numbered-post`) chuyên cho 2 dạng cụ thể — đều dựa trên các nguyên tắc ở đây.

Mục tiêu của bài actionable list post là khiến người đọc làm **một trong ba việc**: **lưu lại** (bài tra cứu), **share** (bài đồng cảm), hoặc **comment "đúng tui luôn"** (bài relatable). Nếu một bài không đạt ít nhất một trong ba, nó là bài thông tin khô, không phải actionable post.

## 1. Cấu trúc xương sống

Mọi bài list post tiếng Việt hiệu quả đều có 4 lớp:

```
[Tiêu đề]      ← bắt mắt khi scroll, hứa hẹn giá trị cụ thể
[Hook 1-3 câu] ← chốt người đọc dừng lại, đọc tiếp
[Body danh sách] ← phần chính, mỗi item có công thức cứng
[Kết chốt]     ← cảm xúc hoặc triết lý, để lại dư âm
```

Đừng bỏ lớp nào. Đặc biệt **kết chốt** — đây là phần khiến bài "có hồn", phân biệt với content AI tạo máy móc.

## 2. Tiêu đề: 3 công thức đã chứng minh

Tiêu đề phải làm được 2 việc trong 1-2 giây scroll: **(a) cho biết bài này về cái gì** và **(b) gợi ra cảm xúc / lợi ích cụ thể**.

**Công thức A — Megalist trấn an:**
```
[TỔNG HỢP / TOÀN BỘ / DANH SÁCH] [chủ đề] – [thông điệp trấn an / cảnh báo]
```
Ví dụ: "TỔNG HỢP CÁC HIỆN TƯỢNG SINH LÝ BÌNH THƯỜNG Ở TRẺ SƠ SINH – MẸ ĐỪNG HOẢNG"

**Công thức B — Relatable đồng cảm:**
```
"[Cụm từ ẩn dụ]" của [đối tượng] – [hứa hẹn cảm xúc]
```
Ví dụ: "Đặc sản của em bé dưới 1 tháng tuổi – mẹ nào trải qua rồi sẽ cười trong nước mắt 😆"

**Công thức C — Con số + Pain point:**
```
[Số] [thứ] mà [đối tượng] [tình huống] – [gợi ý lợi ích]
```
Ví dụ: "7 sai lầm mẹ bỉm hay mắc khi tắm con sơ sinh – cái số 3 ai cũng tưởng đúng"

Khi nào dùng cái nào: xem skill `fb-megalist-post` (A) và `fb-relatable-numbered-post` (B). Công thức C dùng được cho cả hai.

## 3. Hook 3 giây

Sau tiêu đề là **1-3 câu hook**. Đây là phần Facebook hiển thị trước khi user phải bấm "xem thêm". Nếu hook nhạt, user scroll tiếp, bài chết.

**4 dạng hook hiệu quả:**

| Dạng | Cách làm | Khi nào dùng |
|---|---|---|
| **Setup context** | "👉 Giai đoạn [X], cơ thể bé [Y] nên sẽ xuất hiện [Z]..." | Bài cẩm nang, bài kiến thức |
| **Đảo ngược kỳ vọng** | "Nếu ai đó nói với bạn [niềm tin phổ biến], thì... xin chúc mừng, bạn sắp..." | Bài relatable, bài viral |
| **Câu hỏi nhói** | "Bạn có để ý con thường [hành vi X] không? Đây có thể là..." | Bài cảnh báo, bài giáo dục |
| **Số liệu sốc** | "90% mẹ bỉm không biết rằng [sự thật Y]..." | Bài myth-busting |

**Không dùng**: hook kiểu "Hôm nay mình muốn chia sẻ với các mẹ về..." — đây là cách mở bài học sinh viết văn, không phải copywriter.

## 4. Body — phần dài nhất, phải scan được

Đây là chỗ skill phụ phân hoá. Nhưng nguyên tắc chung cho mọi list post:

**4.1. Mỗi item có công thức cứng**
Mỗi mục trong list phải có **cùng một cấu trúc** lặp lại. Người đọc scan trong 2 giây phải hiểu pattern. Ví dụ:
- Megalist: `[Tên]: [giải thích 1 dòng]`
- Relatable: `[Tên ẩn dụ]\n[Mô tả tình huống đối lập]\n[Emoji cảm xúc]`

Đừng đổi format giữa chừng. Đổi format = người đọc phải nghĩ = scroll tiếp.

**4.2. Một dòng / một ý**
Không viết câu dài 3 dòng trong list item. Câu dài bẻ xuống dòng. Xuống dòng nhiều = bài "thở được" trên mobile.

**4.3. Số / mốc thời gian / con số cụ thể luôn thắng từ ngữ chung chung**
- ❌ "Sụt cân một chút trong những ngày đầu"
- ✅ "Sụt cân sinh lý: 5–10% cân nặng trong tuần đầu, sau đó tăng lại trong 10–14 ngày"

Con số làm bài có "trọng lượng", khiến reader tin và lưu lại.

**4.4. Emoji có chủ đích, không spam**
- Dùng emoji để **đánh dấu cấu trúc** (1️⃣ 2️⃣ 3️⃣ cho bài đánh số, 👉 cho hook, ❤️ cho kết)
- Dùng emoji để **chốt cảm xúc cuối câu** (😆 🥲 😌 ❤️)
- Không rải emoji giữa câu cho "đẹp" — gây nhiễu khi đọc

## 5. Ngôn ngữ Việt — 5 quy tắc

**5.1. Đại từ thân mật, đúng đối tượng**
- Mẹ bỉm: "mẹ", "con", "bé", "bạn"
- Người trẻ: "bạn", "mình", "tụi mình"
- Phụ huynh tuổi cao: "anh chị", "các bậc phụ huynh"

Chọn 1, giữ nhất quán suốt bài. Đừng nửa "mẹ" nửa "các bạn".

**5.2. Ẩn dụ sinh động > tính từ chung chung**
Tính từ "khó chịu", "phiền phức", "đáng yêu" — yếu. Ẩn dụ có hình ảnh — mạnh.

- ❌ "Bé hay bú, mẹ mệt"
- ✅ "Mẹ cảm giác mình không phải là mẹ, mà là 'bình sữa di động' 🍼"

- ❌ "Bé hay tỉnh giấc khi đặt xuống"
- ✅ "Như con có 'cảm biến đặt giường' vậy đó"

Khi nghĩ ra ẩn dụ, hỏi: "Cái này giống cái gì trong đời thường?" Càng cụ thể càng tốt (đèn pha, ninja, ông cụ non, bảng nhạc).

**5.3. Micro-scene > mô tả trừu tượng**
Một micro-scene = 2 vế đối lập / 1 chuỗi nhân quả ngắn.

- "Vừa bưng cơm lên → con khóc / Vừa vào toilet → con ọ ẹ / Vừa định ngủ → con tỉnh"
- "Ban ngày: ngủ ngoan, đặt đâu ngủ đó / Ban đêm: mở mắt sáng như đèn pha"

Reader đọc xong thấy "đúng nhà mình luôn" → comment / share.

**5.4. Câu nói trực tiếp tạo immersion**
Chèn câu thoại tưởng tượng vào bài, bằng dấu ngoặc kép:
- Mẹ đứng hình: "Ủa ai làm gì con???"
- "Ước gì được ôm lại cái cục nhỏ xíu... thêm lần nữa."

Câu thoại làm bài "có người", không phải bài AI.

**5.5. Tránh từ cứng nhắc văn phong báo chí**
- ❌ "Đối với trẻ sơ sinh, các bậc phụ huynh cần lưu ý rằng..."
- ✅ "Bé sơ sinh giai đoạn này, mẹ chỉ cần nhớ..."

## 6. Kết chốt — phần làm bài "có hồn"

Sau khi list xong, **đừng kết thúc đột ngột**. Cần 1-3 câu chốt. Có 3 dạng:

**6.1. Triết lý / đúc kết** (cho bài cẩm nang)
> "Nuôi trẻ sơ sinh không phải là thấy gì cũng tìm cách 'sửa', mà là đủ hiểu để biết cái gì là bình thường và bình tĩnh đi qua giai đoạn đó."

**6.2. Chuyển tông hài → sâu lắng** (cho bài relatable)
> "Nuôi em bé dưới 1 tháng không hề 'nhẹ nhàng' như tưởng tượng, nhưng cũng chính những cái 'đặc sản dở khóc dở cười' này… sau này lại là thứ mẹ nhớ nhất."

**6.3. Call to action mềm** (cho bài có brand/sản phẩm)
> "Mẹ nào đang trong giai đoạn này thì lưu lại đọc dần nhé, đừng tự làm khó mình."

Tránh CTA cứng kiểu "Comment 'CẦN' để được tư vấn!" trừ khi đó là bài bán hàng. Bài giá trị → CTA mềm → trust → bán sau.

## 7. Anti-patterns — TRÁNH

Khi viết hoặc sửa bài, kiểm tra xem có rơi vào những lỗi này không:

1. **Bài đều như sách giáo khoa** — không emoji, không xuống dòng, không ẩn dụ → không ai đọc hết
2. **Bài rải emoji loạn xạ** — mỗi câu 3 emoji "cho vui" → nhìn rối, mất chuyên nghiệp
3. **Bài đổi đại từ giữa chừng** — đoạn đầu "mẹ", đoạn sau "các bạn", đoạn cuối "chúng ta" → reader bối rối
4. **Bài liệt kê không có công thức cứng** — item 1 viết 1 dòng, item 2 viết 5 dòng, item 3 lại 2 dòng → mất pattern, khó scan
5. **Bài không có hook** — vào thẳng list → reader scroll qua mất
6. **Bài không có kết** — list xong là hết → bài "hụt", không có dư âm
7. **Bài dùng từ Hán Việt nặng nề** — "phụ huynh cần ý thức rằng..." → ngôn ngữ FB là ngôn ngữ nói, không phải báo
8. **Bài chèn quảng cáo giữa list** — đang đọc list giá trị thì gặp "Hãy mua sản phẩm X..." → reader unfollow

## 8. Workflow khi viết / sửa bài

Khi user yêu cầu viết bài FB list post:

1. **Xác định dạng**: cẩm nang/tra cứu (→ skill `fb-megalist-post`) hay đồng cảm/viral (→ skill `fb-relatable-numbered-post`)? Đọc skill chuyên biệt tương ứng.
2. **Hỏi 3 câu nếu thiếu**: (a) Đối tượng cụ thể là ai? (b) Brand voice / ngôn ngữ xưng hô? (c) Có CTA cuối không, hay chỉ content giá trị?
3. **Draft theo cấu trúc 4 lớp**: tiêu đề → hook → body (theo công thức cứng) → kết chốt
4. **Tự rà 8 anti-patterns** ở mục 7 trước khi đưa cho user
5. **Đếm số items** trong body — megalist nên 15-40 items, numbered relatable nên 8-15 items. Quá ít = bài mỏng, quá nhiều = mệt đọc

Khi user yêu cầu sửa / cải thiện một bài có sẵn:
1. Đọc bài hiện tại
2. Đối chiếu 8 anti-patterns
3. Đối chiếu 4 lớp cấu trúc — thiếu lớp nào?
4. Đề xuất sửa cụ thể, không sửa lan man toàn bài nếu user chỉ hỏi sửa 1 phần
