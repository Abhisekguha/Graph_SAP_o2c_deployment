# Documentation Assets

This folder contains documentation assets for the SAP O2C Graph System.

## 📸 Screenshot

**File:** `screenshot.png`

The main system screenshot showing:
- 3D graph visualization with 1,226 nodes and 5,146 edges
- Color-coded entity types (Customer, SalesOrder, Invoice, etc.)
- Query assistant panel with example conversation
- Statistics panel showing real-time metrics
- Interactive 3D controls and legend

## 🎥 Video Demonstration

**File:** `20260322-2234-54.9297511.mp4`

Full system demonstration video showcasing:
- 3D graph interaction (rotate, zoom, pan)
- Natural language query processing with Gemini-2.5-Flash
- Real-time node highlighting
- Document flow tracing
- Interactive tooltips and node details
- Multiple camera view presets
- Live statistics and graph metrics

**Duration:** ~2-3 minutes  
**Resolution:** 1920x1080  
**Format:** MP4 (H.264)

## 📊 Graph Statistics (Current Dataset)

Based on the actual system deployment:

**Nodes:** 1,226
- Customer: 8
- SalesOrder: 100
- SalesOrderItem: 167
- Delivery: 86
- DeliveryItem: 137
- Invoice: 163
- InvoiceItem: 245
- JournalEntry: 123
- Payment: 76
- Product: 69
- Plant: 44
- Address: 8

**Edges:** 5,146
- AVAILABLE_AT: 3,036
- HAS_ITEM: 549
- REFERS_TO: 412
- BILLS: 245
- PRODUCED_AT: 167
- BILLED_TO: 163
- SHIPPED_FROM: 137
- POSTED_AS: 123
- CLEARED_BY: 120
- PLACED: 100
- FULFILLED_BY: 86
- HAS_ADDRESS: 8

## 📁 File Management

### Adding New Screenshots

1. Take a screenshot at 1920x1080 or higher resolution
2. Ensure split view (graph + chat) is visible
3. Save as PNG format for best quality
4. Name descriptively (e.g., `feature-xyz.png`)
5. Update this README with description

### Adding New Videos

1. Record at 1920x1080 resolution
2. Keep duration under 5 minutes for file size
3. Use MP4 format with H.264 codec
4. Show clear use cases and interactions
5. Add audio narration if helpful
6. Update this README with details

## 🔗 Usage in Documentation

**In README.md:**
```markdown
![Screenshot](docs/screenshot.png)
[Video Demo](docs/20260322-2234-54.9297511.mp4)
```

**In Presentations:**
- Use screenshot for static slides
- Embed video for live demonstrations
- Reference specific timestamps for features

## 📋 Asset Inventory

| Asset | Type | Size | Purpose |
|-------|------|------|---------|
| screenshot.png | PNG Image | ~500KB | Main system visualization |
| 20260322-2234-54.9297511.mp4 | MP4 Video | ~10-20MB | Full system demo |
| README.md | Documentation | ~3KB | This file |

---

**Last Updated:** March 23, 2026  
**Maintained By:** SAP O2C Graph System Team
