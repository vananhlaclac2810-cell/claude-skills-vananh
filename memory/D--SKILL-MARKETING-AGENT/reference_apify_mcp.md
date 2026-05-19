---
name: Apify MCP đã kết nối
description: Apify MCP đã add vào Claude Code (project D:\SKILL MARKETING AGENT), token đã lưu trong .claude.json. Dùng để scrape Facebook/Instagram/TikTok data cho phân tích đối thủ.
type: reference
originSessionId: 6cf6b371-4195-4b64-9b18-4a7c696b9d50
---
Apify MCP server đã được add ngày 2026-05-12:
- Transport: HTTP
- URL: `https://mcp.apify.com`
- Token lưu trong: `C:\Users\ADMIN\.claude.json` (project-scope cho D:\SKILL MARKETING AGENT)
- Account: `vananh.laclac2810@gmail.com`

**Lưu ý quan trọng**: MCP tools (`mcp__Apify__*`) chỉ hoạt động sau khi restart Claude Code. Trong session đã add, gọi MCP tool sẽ timeout — fallback dùng REST API trực tiếp:

```powershell
# Async run
POST https://api.apify.com/v2/acts/<actor-slug-with-tilde>/runs?token=<TOKEN>
# Example: apify~facebook-posts-scraper

# Poll status
GET https://api.apify.com/v2/actor-runs/<runId>
Header: Authorization: Bearer <TOKEN>

# Fetch dataset
GET https://api.apify.com/v2/datasets/<datasetId>/items?format=json&fields=<comma-sep>
Header: Authorization: Bearer <TOKEN>
```

**Actor đã verify hoạt động**:
- `apify/facebook-posts-scraper` — scrape posts từ FB page public
  - Input: `{ startUrls: [{url: "https://www.facebook.com/<page>"}], resultsLimit: N }`
  - Output fields hữu ích: `postId, url, topLevelUrl, time, text, likes, shares, viewsCount, isVideo, reactionLikeCount, reactionLoveCount, topReactionsCount, media`
  - **Không có comments count** — engagement chỉ tính được từ likes + shares + views
  - Tốc độ: ~90 giây cho 50 posts
  - Chi phí: ~$0.0003/post

**Chi phí dự kiến**:
- 50 posts FB: $0.015
- 500 posts FB: $0.15
- Free credit $5/tháng đủ ~16,000 posts
