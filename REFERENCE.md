# SAP O2C Graph System - Quick Reference Card

**Version:** 2.0.0 (3D Interactive Edition)  
**Last Updated:** March 23, 2026

---

## 🚀 One-Line Pitch

Transform fragmented SAP O2C data into an immersive 3D graph and explore it using natural language queries.

**📸 Screenshot:** [docs/screenshot.png](docs/screenshot.png)  
**🎥 Video Demo:** [docs/20260322-2234-54.9297511.mp4](docs/20260322-2234-54.9297511.mp4)

---

## ⚡ Quick Start (5 Minutes)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate                    # Windows
pip install -r requirements.txt
$env:GEMINI_API_KEY="your_key_here"     # Get from ai.google.dev
python app.py                            # Runs on :8000
```

### Frontend
```bash
cd frontend
npm install
npm start                                # Runs on :3000
```

### Browser
```
http://localhost:3000
```

---

## 📦 Dataset Setup

**⚠️ CRITICAL**: Dataset folders must be in parent directory!

**Correct Structure:**
```
sap-o2c-data/                    ← Parent folder
├── sales_order_headers/         ← Dataset folders
├── billing_document_headers/
├── products/
├── ... (all dataset folders)
└── sap-o2c-graph-system/        ← Application folder
    ├── backend/
    └── frontend/
```

**📥 Download Dataset:**  
[Google Drive Link](https://drive.google.com/file/d/1UqaLbFaveV-3MEuiUrzKydhKmkeC1iAL/view)

**Verification:**
```bash
# From sap-o2c-data/ directory
ls -la  # Should show both dataset folders and sap-o2c-graph-system/
```

---

## 🎮 3D Controls Cheat Sheet

| Action | Control |
|--------|---------|
| **Rotate** | Left-click + drag |
| **Pan** | Right-click + drag |
| **Zoom** | Mouse scroll |
| **Select Node** | Left-click on node |
| **View Details** | Hover 150ms |
| **Fit All** | Click "Fit View" |
| **Reset** | Click "Reset View" |
| **Isometric** | Click "Isometric" |

---

## 💬 Query Examples

**Counting:**
- "How many sales orders are there?"
- "Count invoices for customer 320000082"

**Finding:**
- "Find sales order 740533"
- "Show me all products from plant WB05"

**Tracing:**
- "Trace the flow of invoice 90504248"
- "Follow sales order 740533 from start to payment"

**Analysis:**
- "Which products have the most orders?"
- "Find sales orders without deliveries"
- "Identify broken payment flows"

---

## 🎨 Visual Legend

| Color | Entity Type |
|-------|-------------|
| 🔴 Pink | Customer |
| 🔵 Blue | SalesOrder |
| 🟢 Green | Invoice |
| 🟣 Purple | JournalEntry |
| 🟡 Yellow | Product |
| 🟠 Orange | Delivery |
| 🔷 Cyan | Payment |
| 🟤 Brown | Plant |
| ⚪ Gray | Address |

**Special Colors:**
- 🟡 Yellow Ring = Highlighted (from query)
- 🔴 Red Ring = Selected (clicked)

---

## 🏗️ Architecture at a Glance

```
User Browser (React + Three.js)
         ↓
    REST API (FastAPI)
         ↓
   Graph Store (NetworkX) ←→ LLM (Gemini-2.5-Flash)
         ↓
   JSONL Files (Raw Data)
```

**Data Flow:**
```
JSONL → Parse → Build Graph → Serve API → Render 3D → User
                                    ↑
                               Query LLM
```

---

## 📊 Key Statistics

- **Nodes:** 1,226 entities
- **Edges:** 5,146 relationships
- **Query Time:** <500ms
- **Graph Build:** ~2-3 seconds
- **Render FPS:** 60 (lightweight dataset)

---

## 🐛 Troubleshooting (Top 3)

### 1. Graph Not Loading
```bash
# Check backend console for errors
# Verify dataset path in config.py
# Wait 10-15s for initial build
```

### 2. Poor Performance / Low FPS
```bash
# Update graphics drivers
# Use Chrome (best WebGL support)
# Close other GPU apps
# Reduce browser zoom to 100%
```

### 3. API Key Error
```bash
# Get free key: https://ai.google.dev
# Set in terminal: $env:GEMINI_API_KEY="key"
# Restart backend after setting
```

---

## 🔗 Useful Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | System status |
| `GET /api/graph/data` | Full graph |
| `GET /api/graph/stats` | Statistics |
| `POST /api/query` | Natural language query |
| `GET /api/analyze/broken-flows` | Find incomplete flows |

---

## 📁 Project Structure

```
sap-o2c-graph-system/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── graph_builder.py    # Graph construction
│   ├── query_engine.py     # LLM integration
│   └── requirements.txt    # Python deps
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── GraphVisualization.js  # 3D graph
│   │   └── App.js
│   └── package.json        # Node deps
├── docs/
│   └── screenshot.png      # System demo
├── README.md               # Full documentation
├── CHANGELOG.md            # Version history
└── QUICKSTART.md           # Setup guide
```

---

## 🎯 Use Cases

✅ Explore complex business relationships  
✅ Trace document flows end-to-end  
✅ Identify data quality issues  
✅ Understand SAP O2C data structure  
✅ Demo graph database concepts  
✅ Research NL query interfaces  

---

## 🔧 Configuration Hot Spots

**Hover Sensitivity** (`GraphVisualization.js`):
```javascript
const HOVER_DELAY = 150;  // ms before tooltip
```

**Camera Speed** (`GraphVisualization.js`):
```javascript
controls.rotateSpeed = 0.5;  // Rotation
controls.zoomSpeed = 0.8;     // Zoom
```

**Node Size** (`GraphVisualization.js`):
```javascript
getNodeSize(type) // Returns 4-12
```

**Force Strength** (`GraphVisualization.js`):
```javascript
d3Force={{ charge: { strength: -200 } }}
```

---

## 📚 Documentation

- **Full README**: `README.md` (comprehensive guide)
- **Quick Start**: `QUICKSTART.md` (setup only)
- **Architecture**: `ARCHITECTURE.md` (technical details)
- **Deployment**: `DEPLOYMENT.md` (production guide)
- **Changelog**: `CHANGELOG.md` (version history)

---

## 🆘 Getting Help

1. Check `README.md` troubleshooting section
2. Review browser console (F12) for errors
3. Verify backend console for API errors
4. Test with example queries first
5. Check system requirements are met

---

## ⚙️ System Requirements

**Minimum:**
- 8GB RAM
- Integrated Graphics
- Dual-Core CPU
- Chrome 90+

**Recommended:**
- 16GB RAM
- GTX 1060 or equivalent
- Quad-Core CPU
- 1920x1080 display

---

## 🎓 Learning Path

1. ✅ Run quick start
2. ✅ Try example queries
3. ✅ Explore 3D graph
4. ✅ Read architecture section
5. ✅ Modify configuration
6. ✅ Add custom features

---

## 🚦 Version Info

**Current:** 2.0.0 (3D Edition)  
**Release:** March 2026  
**Previous:** 1.0.0 (2D Edition)  
**Next:** 2.1.0 (Query Templates)

**Major Changes:**
- ✅ 2D → 3D visualization
- ✅ Smart hover debouncing
- ✅ Enhanced tooltips
- ✅ Multiple camera views
- ✅ Custom 3D rendering

---

**Need more details?** → See `README.md`  
**First time here?** → See `QUICKSTART.md`  
**Deploying?** → See `DEPLOYMENT.md`

---

*Built with ❤️ for SAP O2C Data Analysis*
