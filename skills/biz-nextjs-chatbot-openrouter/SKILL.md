---
name: biz-nextjs-chatbot-openrouter
description: "Cài chatbot AI dạng floating widget góc dưới phải vào project Next.js có sẵn (App Router hoặc Pages Router), responsive đầy đủ web + tablet + mobile, gọi LLM qua OpenRouter (mặc định google/gemini-3-flash-preview, có thể đổi sang anthropic/claude-sonnet-4.6), streaming response, có knowledge base từ FAQ + tài liệu sản phẩm/khóa học do user cung cấp để chatbot tự động trả lời khách hàng. Skill tự detect số lượng project Next.js — nếu có nhiều hơn 1 sẽ hỏi user chọn project nào để cài; tự detect TypeScript/JS, App Router/Pages Router, Tailwind/CSS module; tự tạo .env.local với OPENROUTER_API_KEY và hướng dẫn user cách lấy key. USE WHEN user says: 'tạo chatbot trên web', 'thêm chatbot vào website', 'cài chatbot cho landing page', 'add chatbot widget', 'chatbot góc dưới phải', 'floating chatbot Next.js', 'chatbot trả lời khách hàng tự động', 'chatbot FAQ khóa học', 'AI chat widget cho web', 'biz-nextjs-chatbot', 'chatbot dùng OpenRouter', 'tích hợp Gemini vào website', 'tích hợp Sonnet vào website', 'chatbot khóa học tự động', 'support bot tự động cho landing page', 'thêm AI hỗ trợ khách hàng vào trang web', 'embed chatbot vào Next.js project'. Trigger cả khi user vừa launch sales page xong và muốn thêm support bot, hoặc khi user muốn giảm tải support manual."
framework: "Next.js 13+ (App Router) hoặc Pages Router — OpenRouter REST API streaming — Tailwind hoặc CSS module fallback — mobile-first responsive"
models: "google/gemini-3-flash-preview (mặc định, nhanh + rẻ) / anthropic/claude-sonnet-4.6 (chất lượng cao hơn, đắt hơn)"
---

# Biz Next.js Chatbot OpenRouter — Cài chatbot AI floating vào website 1 phát

Skill này gắn 1 **chatbot AI dạng floating widget** vào project Next.js có sẵn. Widget nằm góc **dưới phải**, responsive đầy đủ 3 màn hình, gọi LLM qua **OpenRouter** với knowledge base từ FAQ + tài liệu khóa học/sản phẩm. Mục tiêu: solopreneur / course creator có **support bot tự động 24/7** ngay trên landing page bán khóa học, không cần code backend riêng.

> **Tinh thần**: Tự detect mọi thứ có thể (Next.js version, App/Pages Router, TS/JS, Tailwind/CSS), chỉ hỏi user 4 thứ thật sự cần: (1) project nào nếu có nhiều, (2) FAQ, (3) tài liệu sản phẩm, (4) tone/brand name. Còn lại là code → live trong vài phút.

## Khi nào dùng

User muốn:
- Gắn chatbot AI hỗ trợ khách hàng vào landing page bán khóa học / dịch vụ
- Giảm tải trả lời câu hỏi lặp lại (giá, lộ trình, hoàn tiền, đối tượng phù hợp...)
- Cần widget chat nhỏ gọn góc dưới phải, không che nội dung
- Cần chatbot hiểu chính xác nội dung khóa học / sản phẩm của họ (FAQ-driven)
- Đã có Next.js project (vừa chạy `/biz-sales-page-layout` xong, hoặc project cũ)

## Khi nào KHÔNG dùng

- Project không phải Next.js (React thuần Vite, Vue, Svelte, plain HTML) → skill này chuyên Next.js. Có thể adapt nhưng không tối ưu.
- Cần chatbot có RAG (retrieval-augmented) với knowledge base hàng ngàn trang → cần vector DB (Pinecone/Supabase pgvector), skill này dùng system prompt đơn giản phù hợp ≤ 20K token kiến thức.
- Cần chatbot voice / multimodal (gửi ảnh) → skill này text-only.
- Cần chatbot lưu lịch sử chat per-user vào DB → skill này stateless, ephemeral session, có thể mở rộng sau.
- Backend không phải Vercel-friendly (cần long polling, WebSocket persistent) → OpenRouter streaming hoạt động OK trên Vercel Edge, nhưng nếu cần WS riêng thì khác.

## Output user sẽ nhận

Sau khi skill chạy xong:

1. **File mới trong project Next.js của user**:
   - `components/Chatbot.tsx` (hoặc `.jsx`) — widget UI
   - `app/api/chat/route.ts` (App Router) **HOẶC** `pages/api/chat.ts` (Pages Router) — API proxy gọi OpenRouter
   - `lib/chatbot-knowledge.ts` (hoặc `.js`) — knowledge base + system prompt
   - `.env.local` được tạo/append với `OPENROUTER_API_KEY=` (placeholder)
   - `.env.example` (nếu chưa có) để document biến môi trường
   - Mount `<Chatbot />` vào `app/layout.tsx` hoặc `pages/_app.tsx`

2. **Hướng dẫn rõ ràng cuối session**:
   - 3 bước user phải tự làm: (a) lấy OpenRouter API key, (b) paste vào `.env.local`, (c) `npm run dev` test
   - Cách đổi model giữa Gemini và Sonnet
   - Cách update knowledge base sau này

## Workflow

### Bước 1 — Detect Next.js project

Tìm các Next.js project candidate. Chạy:

```bash
# Tìm package.json có chứa "next" trong dependencies, độ sâu tối đa 4
find /Users/tonyhoang/Documents/GitHub -maxdepth 4 -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | xargs grep -l '"next"' 2>/dev/null | head -20
```

(Nếu user đang ở trong 1 working directory cụ thể, ưu tiên tìm từ `cwd` xuống trước, fallback ra `~/Documents/GitHub` nếu không thấy.)

**Phân nhánh**:
- **0 project**: Báo user và dừng. Đề xuất: "Anh/chị có project Next.js nào chưa? Nếu chưa, có muốn em tạo 1 cái mới với `/biz-sales-page-layout` rồi quay lại không?"
- **1 project**: Confirm path với user trước khi proceed: "Em sẽ cài chatbot vào [path]. Anh/chị OK chứ?"
- **≥ 2 project**: Liệt kê path + tên (`name` từ package.json) ra list đánh số, hỏi user pick: "Em thấy có N project Next.js. Anh/chị muốn cài vào cái nào?"

### Bước 2 — Probe project context

Sau khi user xác nhận project, đọc:

1. `package.json` → check:
   - TypeScript (có `typescript` trong deps?)
   - Tailwind (có `tailwindcss` trong devDeps?)
   - Package manager (lockfile: `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, default `npm`)
   - Next.js version

2. Cấu trúc thư mục → check:
   - `app/` directory tồn tại → App Router
   - `pages/` directory tồn tại (và không có `app/`) → Pages Router
   - Cả 2 cùng tồn tại → ưu tiên App Router cho file mới (Next.js đang chuyển sang)
   - `src/` wrapper → adjust path (vd. `src/app/`, `src/components/`)

3. `tsconfig.json` → check path alias (`@/*` → `./src/*` hay `./*`)

4. `.env.local`, `.env.example` → check đã tồn tại chưa

**Lưu các quan sát này** thành 1 bảng nhỏ để dùng ở các bước sau.

### Bước 3 — Thu thập knowledge base từ user

**Hỏi user 4 câu** (gộp trong 1 message để user trả lời 1 lần, đỡ qua lại):

```
Để chatbot trả lời chính xác, em cần 4 thứ:

1. **FAQ** — danh sách câu hỏi thường gặp + câu trả lời (giá, lộ trình, hoàn tiền, đối tượng, thời gian học, hỗ trợ sau khóa...). 
   Anh/chị paste trực tiếp vào đây, HOẶC chỉ đường dẫn file (.md / .txt / .docx).

2. **Tài liệu sản phẩm / khóa học** — mô tả chi tiết khóa học: tên, nội dung từng module, kết quả đầu ra, giảng viên, bonus, giá tier nếu có nhiều.
   Cũng paste hoặc chỉ đường dẫn file.

3. **Brand name + tone** — Tên brand/khóa học để chatbot xưng hô (vd. "trợ lý của AI Mastery"). Tone bot dùng: thân thiện anh/chị (mặc định) / formal / casual em-bạn.

4. **Model** — mặc định `google/gemini-3-flash-preview` (nhanh, rẻ, đủ tốt cho support). Muốn dùng `anthropic/claude-sonnet-4.6` (chất lượng cao hơn, đắt hơn ~10x) cho early stage chatlượng đầu vẫn thấp thì nói em.

Anh/chị trả lời 1 lượt được không?
```

**Khi user trả lời**:
- Nếu chỉ đường dẫn file → đọc file đó bằng Read tool.
- Nếu paste nội dung trực tiếp → dùng nội dung paste.
- Nếu user nói "tự generate placeholder dùm em" → tạo FAQ placeholder generic và đánh dấu `// TODO: user fill in` để user biết phải cập nhật.
- Brand name không có → default "Trợ lý AI" và xưng anh/chị.

### Bước 4 — Generate các file vào project

Đọc các template trong `templates/` của skill này và **adapt** vào project. Các template:

- `templates/chatbot-knowledge.ts` — Module export knowledge base + systemPrompt. Inject FAQ, product info, brand name, tone vào đây.
- `templates/Chatbot.tsx` — Widget component, Tailwind-first. Nếu project KHÔNG có Tailwind → fallback dùng `templates/Chatbot-noTailwind.tsx` + `templates/chatbot.module.css`.
- `templates/chat-route-app.ts` — API route cho App Router (`app/api/chat/route.ts`).
- `templates/chat-route-pages.ts` — API route cho Pages Router (`pages/api/chat.ts`).
- `templates/env-instructions.md` — Snippet hướng dẫn lấy OpenRouter key, dùng ở bước cuối.

**Quy tắc khi adapt template**:
1. **TS vs JS**: nếu project chỉ có JS, đổi extension `.ts/.tsx` → `.js/.jsx` và **bỏ type annotations** (không chỉ đổi tên file). Đọc file mẫu, parse, bỏ types, ghi ra.
2. **Path alias**: nếu `tsconfig` map `@/*` → `./src/*`, các import trong template phải dùng `@/lib/chatbot-knowledge` và file đặt vào `src/lib/`. Nếu không có alias, dùng relative path.
3. **Model**: replace placeholder `__MODEL_ID__` bằng model user chọn (`google/gemini-3-flash-preview` hoặc `anthropic/claude-sonnet-4.6`).
4. **Brand**: replace `__BRAND_NAME__`, `__BRAND_TONE__`.
5. **Knowledge**: build `systemPrompt` từ FAQ + product info dạng cấu trúc rõ ràng (xem template).
6. **Mount widget**: 
   - App Router: edit `app/layout.tsx` (hoặc `src/app/layout.tsx`), thêm `import Chatbot from '@/components/Chatbot'` và `<Chatbot />` ngay trước `</body>`. **Đọc layout.tsx hiện tại trước khi edit** để giữ nguyên metadata, fonts, providers.
   - Pages Router: edit `pages/_app.tsx`, wrap return: `<><Component {...pageProps} /><Chatbot /></>`. Đọc `_app` trước, giữ nguyên existing providers.

### Bước 5 — Setup .env.local + .gitignore

1. Check `.env.local` đã tồn tại?
   - **Chưa**: tạo mới với:
     ```
     # OpenRouter API key — Lấy ở https://openrouter.ai/keys
     OPENROUTER_API_KEY=
     
     # Optional: site URL để OpenRouter tracking referrer (giúp rate limit tốt hơn)
     NEXT_PUBLIC_SITE_URL=http://localhost:3000
     ```
   - **Đã có**: append 2 biến trên nếu chưa có, không ghi đè biến cũ.

2. Update `.env.example` (tạo mới nếu chưa có):
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxx
   NEXT_PUBLIC_SITE_URL=https://your-domain.com
   ```

3. Check `.gitignore` đã có `.env.local`? Nếu chưa → append `.env.local` và `.env*.local`.

### Bước 6 — Báo cáo cho user

In ra **1 message tóm tắt rõ ràng** với 4 phần:

```
✅ Chatbot đã cài xong vào [project name]

📁 Files đã tạo:
  - components/Chatbot.tsx
  - app/api/chat/route.ts
  - lib/chatbot-knowledge.ts
  - .env.local (placeholder)

🔑 3 bước anh/chị cần tự làm để chatbot chạy:

1. Lấy OpenRouter API key:
   - Vào https://openrouter.ai → Sign up (có thể login bằng Google)
   - Vào https://openrouter.ai/keys → Create Key
   - Nạp credit (https://openrouter.ai/credits) — Gemini 3 Flash rẻ, $5 đủ chạy hàng nghìn câu chat
   - Copy key dạng `sk-or-v1-xxxxx`

2. Paste vào file `.env.local`:
   OPENROUTER_API_KEY=sk-or-v1-xxxxx-paste-vào-đây

3. Chạy thử:
   [npm/pnpm/yarn] run dev
   Mở http://localhost:3000 → click bong bóng góc dưới phải

🔄 Đổi model giữa Gemini ↔ Sonnet:
  Mở `app/api/chat/route.ts`, sửa biến `model:` ở đầu file.
  - `google/gemini-3-flash-preview` (mặc định, $0.075/1M input, nhanh)
  - `anthropic/claude-sonnet-4.6` (cao cấp, ~$3/1M input, chất lượng tốt hơn)

📚 Update knowledge base sau này:
  Edit `lib/chatbot-knowledge.ts` — thêm/sửa FAQ và productInfo, save, hot reload.
```

## Mobile-first responsive design

Widget **phải** đạt 3 breakpoint:

| Breakpoint | Hành vi |
|---|---|
| ≤ 640px (mobile) | Click bubble → mở **fullscreen overlay** (z-index 9999), header có nút X close. Input docked bottom với safe-area-inset để không bị che bởi keyboard. |
| 641–1023px (tablet) | Panel 380px × 70vh, anchored bottom-right margin 16px. |
| ≥ 1024px (desktop) | Panel 400px × 600px, anchored bottom-right margin 24px. Bubble 60px tròn. |

**Lý do mobile fullscreen**: VN traffic 70%+ là mobile, panel 380px trên màn 360px sẽ overflow + bàn phím che gần hết. Fullscreen là UX chuẩn (Intercom, Tidio, Crisp đều làm vậy).

Template `Chatbot.tsx` đã có sẵn các Tailwind class implement chuẩn này. Khi adapt, **giữ nguyên responsive logic**, chỉ thay đổi màu/text theo brand.

## OpenRouter API — Quick reference

OpenRouter endpoint: `https://openrouter.ai/api/v1/chat/completions`

Headers bắt buộc:
- `Authorization: Bearer <OPENROUTER_API_KEY>`
- `Content-Type: application/json`

Headers khuyến nghị (giúp rate limit + analytics):
- `HTTP-Referer: <site URL>` 
- `X-Title: <app name>` (vd. "AI Mastery Chatbot")

Body:
```json
{
  "model": "google/gemini-3-flash-preview",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "stream": true
}
```

Streaming response: SSE format (`data: {...}\n\n`). Template `chat-route-app.ts` đã handle pass-through stream từ OpenRouter về client, frontend parse SSE bằng `ReadableStream` reader. **Không cần SDK** — `fetch` thuần đủ.

Chi tiết thêm: xem `references/openrouter-api.md`.

## Edge cases cần xử lý

1. **Project có `src/` wrapper**: tất cả path phải tiền tố `src/` (vd. `src/components/Chatbot.tsx`, `src/app/layout.tsx`). Detect bằng cách check `src/app` hoặc `src/pages` tồn tại.

2. **Project đã có file trùng tên** (vd. `components/Chatbot.tsx` đã có): hỏi user — overwrite hay đổi tên (vd. `AIChatbot.tsx`). Mặc định đổi tên để không destroy work cũ.

3. **Tailwind chưa cài**: 
   - Hỏi user: cài Tailwind không (recommended), hay dùng CSS module fallback?
   - Nếu chọn Tailwind: chạy `npx tailwindcss init -p` và setup, hoặc nếu phức tạp thì dùng fallback và note lại cho user.
   - Mặc định fallback CSS module — an toàn hơn, không invasive với project.

4. **Project dùng React 19 / Server Components strict**: `Chatbot.tsx` phải có `'use client'` directive ở dòng đầu. Template đã có.

5. **Conflict với existing `/api/chat` route**: kiểm tra trước khi tạo. Nếu trùng → đổi tên route thành `/api/chatbot` hoặc tương tự, update fetch URL trong widget.

6. **Knowledge base quá dài (>15K token)**: chia thành 2 phần — `coreKnowledge` (system prompt, luôn load) và `extendedKnowledge` (optional, kèm khi user hỏi về chi tiết cụ thể). Tạm thời implement đơn giản: cảnh báo user nếu >15K chars, gợi ý cắt gọn FAQ.

7. **User trả lời thiếu** (vd. có FAQ nhưng không có product info): vẫn proceed với phần có, để placeholder `// TODO: user add product details here` ở chỗ thiếu.

## Cấu trúc system prompt (built từ knowledge base)

Template `chatbot-knowledge.ts` build systemPrompt theo cấu trúc:

```
Bạn là trợ lý AI của [BRAND_NAME].

NHIỆM VỤ:
- Trả lời câu hỏi của khách hàng về sản phẩm/khóa học của [BRAND_NAME]
- Hỗ trợ khách hàng quyết định mua / đăng ký
- KHÔNG bịa thông tin. Nếu không chắc, nói "Em sẽ kiểm tra và phản hồi anh/chị qua email/SĐT".
- KHÔNG trả lời câu hỏi off-topic (chính trị, ý kiến cá nhân, code task...). Lịch sự đổi chủ đề về sản phẩm.

GIỌNG ĐIỆU:
- Xưng [em] - gọi khách [anh/chị] (hoặc theo tone user chỉ định)
- Thân thiện, ngắn gọn, action-oriented
- Mỗi câu trả lời ≤ 4 câu trừ khi cần list chi tiết

THÔNG TIN SẢN PHẨM:
[productInfo từ user]

FAQ:
[Q-A pairs từ user]

NẾU KHÁCH MUỐN ĐĂNG KÝ / MUA:
- Hướng dẫn họ scroll lên form đăng ký trên trang (tên/SĐT/email)
- Hoặc cung cấp link đăng ký nếu có
```

Tone block thay đổi theo user input. FAQ format dạng:

```
Q: [câu hỏi]
A: [câu trả lời]
```

## Anti-patterns — tránh các sai lầm này

- **Không** hardcode API key vào code (luôn dùng `process.env.OPENROUTER_API_KEY`)
- **Không** expose key ra client (`NEXT_PUBLIC_*`) — API route chạy server-side proxy
- **Không** dùng `dangerouslySetInnerHTML` để render message — XSS risk. Render plain text hoặc dùng markdown parser an toàn (vd. `react-markdown`).
- **Không** rate limit ở client (dễ bypass) — nếu cần, thêm `Upstash Ratelimit` ở API route. Skill này skip rate limit để tối giản; lưu ý cho user.
- **Không** mount widget vào `head` hoặc trước hydration — phải client component, mount trong body.
- **Không** dùng `position: fixed` mà thiếu `safe-area-inset-bottom` trên mobile (iPhone notch).
- **Không** dùng z-index < 50 cho widget — sẽ bị các modal khác che. Mặc định z-9999.

## Khi user yêu cầu mở rộng sau này

Sau khi skill chạy xong, user có thể yêu cầu:
- **"Thêm streaming text typing effect"** → đã có sẵn trong template, chỉ cần verify
- **"Lưu lịch sử chat vào localStorage"** → thêm `useEffect` save/load `messages` từ `localStorage`
- **"Thêm rate limit"** → cài `@upstash/ratelimit` + `@upstash/redis`, wrap API route
- **"Đổi sang model khác"** (vd. `meta-llama/llama-3.3-70b-instruct`) → chỉ sửa biến `model:` trong API route
- **"Thêm RAG với knowledge dài hơn"** → setup Supabase pgvector hoặc Pinecone, embed FAQ, query top-k khi user hỏi
- **"Đa ngôn ngữ"** → detect user language, swap system prompt theo locale

Các yêu cầu này nằm ngoài scope skill base, nhưng skill đã đặt foundation tốt để mở rộng — code clean, knowledge tách module, API route stateless.
