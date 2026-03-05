# Manual QA Checklist

Use this checklist to verify all UI/UX improvements are working correctly.

---

## Pre-Check (Before Testing)

- [ ] All Python files compile without errors: `python -c "import streamlit_app"` ✓
- [ ] No new dependencies in requirements.txt
- [ ] Git status shows only modified .py files and new .md file (no generated files)

---

## Launch & Initial Appearance

- [ ] App starts: `streamlit run streamlit_app.py` (waits for you to navigate to browser)
- [ ] Hero section displays: "Barzel Analytics — Dubai (V2)"
- [ ] Subtitle: "Institutional analytical cockpit. Premium analytics for funds and family offices."
- [ ] Coverage line visible below hero: "Coverage: N listings • K districts"
- [ ] No debug captions ("Rows: ...", "Columns: ...", "Districts: ...")
- [ ] No warning/error messages in Streamlit logs

---

## Navigation Bar (P0 — Critical)

### Appearance
- [ ] Navigation is horizontal, NOT vertical or wrapped
- [ ] Left side shows "Barzel Analytics" with "Dubai" subtitle (bold, clean)
- [ ] Center shows pill-style buttons: Executive Snapshot | Compare | Map & Micro | PDF Report
- [ ] Right side shows "Institutional Suite" subtitle
- [ ] Buttons have rounded corners (border-radius: 999px)
- [ ] Selected button has teal/green accent color
- [ ] Unselected buttons are subtle (low opacity)
- [ ] No lines or harsh dividers between nav elements

### Functionality
- [ ] Clicking each nav item switches pages without errors
- [ ] Selected page persists across reloads (session state works)
- [ ] Navigation bar does NOT wrap to multiple lines on laptop (1920px wide screen)
- [ ] Hover effect on nav pills is smooth and visible (color change)

---

## Landing Page / Executive Snapshot (Page 1)

### Content
- [ ] Page title: "Executive Snapshot"
- [ ] Subtitle: "High-level view of key market metrics and dynamics."
- [ ] Selection bar visible at top: "Districts" selector (thin, subtle card)
- [ ] 2 rows of 5 KPI cards each (10 total):
  - [ ] Row 1: Listings, Median AED/sqm, Median DOM, Net Yield (median), Service Charge (median)
  - [ ] Row 2: Quick Sales ≤30d, Quick Sales ≤60d, Liquidity Depth, Price Consistency, Yield Efficiency
- [ ] All KPI values have 3-4 significant digits (no excessive decimals)
- [ ] Yield Efficiency shows as "X.XXX%" (e.g., "0.060%") NOT "0.0006"

### Charts
- [ ] No Plotly toolbar visible on any chart (no zoom/pan/save icons)
- [ ] Charts render clearly with proper colors
- [ ] Section headers: "Distribution: AED/sqm", "Distribution: Days on Market", "Pricing Discipline", etc.
- [ ] Spacing: Blank line (no divider) between chart sections instead of full divider
- [ ] Typology composition chart is a DONUT (hole in center) NOT a pie
- [ ] Donut legend oriented HORIZONTALLY below chart (not cluttered on side)

### Dividers
- [ ] Only major sections have dividers (between KPI wall and charts, between major chart groups)
- [ ] No divider spam (not every small section has a divider)
- [ ] Dividers are subtle color (rgba(255,255,255,0.06))

### Data Quality
- [ ] All KPI numbers match original implementation (not altered)
- [ ] Charts show same data as before (only visual formatting changed)

---

## Compare Page (Page 2)

### Content
- [ ] Page title: "Compare"
- [ ] Subtitle: "Side-by-side district analysis across key metrics."
- [ ] Selection bar at top: "Districts" selector (same style as Executive Snapshot)
- [ ] 4 KPI cards summarizing selection

### Charts
- [ ] No Plotly toolbar visible
- [ ] Bar charts for pricing, liquidity, yield, operating costs
- [ ] Line chart for product type pricing (if available)
- [ ] All charts have descriptive titles

### Consistency
- [ ] Same typography and spacing as Executive Snapshot
- [ ] Selection bar styling matches Executive Snapshot

---

## Map & Micro Page (Page 3)

### Content
- [ ] Page title: "Map & Micro"
- [ ] Subtitle: "Geospatial and micro-level market insights."
- [ ] Selection bar at top with "Districts" selector
- [ ] 4 KPI cards (Listings, Geo Coverage, Price Data, Time Data)

### Map
- [ ] Mapbox map renders correctly
- [ ] No Plotly toolbar
- [ ] Listings colored by AED/sqm
- [ ] Zoom/pan responsive

### Additional Charts
- [ ] Floor premium line chart (if data available)
- [ ] Top Buildings table (clean, readable)

### Consistency
- [ ] Selection bar matches other pages
- [ ] Typography consistent

---

## PDF Report Page (Page 4)

### Content
- [ ] Page title: "PDF Report Builder"
- [ ] Subtitle: "Generate comprehensive analyst report with scores and recommendations."
- [ ] Professional layout with sections:
  - [ ] "Report Configuration" section
  - [ ] Investor Profile dropdown
  - [ ] Dataset info (N listings, K districts)
  - [ ] Districts selection bar
  - [ ] Analyst Context text area

### Functionality
- [ ] Can select investor profile (Capital Preservation / Core / Core+ / Opportunistic)
- [ ] Can select/deselect districts
- [ ] Can enter analyst notes
- [ ] "Generate PDF Report" button is present and clickable
- [ ] PDF generation works (download button appears)
- [ ] No errors during PDF generation

---

## Global CSS & Styling

### Colors & Contrast
- [ ] All text is readable (white/light gray on dark background)
- [ ] KPI cards have subtle background and border (not jarring)
- [ ] Teal/green accent color (rgba(0,229,168,...)) is used for:
  - [ ] Selected nav pill
  - [ ] Hover states on interactive elements
  - [ ] Links and emphasis

### Typography
- [ ] Page titles: Large (2.1rem), bold, letter-spacing negative
- [ ] Section headers: Medium size, proper weight
- [ ] Captions/labels: Small (12-13px), muted color
- [ ] Font: system sans-serif (Segoe UI, Helvetica, etc.)

### Spacing
- [ ] Consistent padding in cards and containers
- [ ] Section spacing uses empty markdown instead of dividers where appropriate
- [ ] No excessive whitespace or cramped layout

---

## Performance & Stability

- [ ] App loads within 3-5 seconds on first load
- [ ] Page switching is responsive (< 1 second)
- [ ] Selecting districts updates content smoothly
- [ ] No console errors in browser dev tools
- [ ] No Streamlit rerun loops (app doesn't refresh excessively)

---

## Responsive Design (Laptop Width)

- [ ] At 1920px wide: All content visible, no horizontal scroll
- [ ] At 1440px wide: All content visible, nav doesn't wrap
- [ ] At 1200px wide: Nav still horizontal, content still legible
- [ ] Max-width is respected (content doesn't stretch edge-to-edge)

---

## Final Verification

### No Logic Changes
- [ ] All KPI calculations are identical to original
- [ ] All thresholds unchanged (e.g., 30-day liquidity = same logic)
- [ ] All data transformations unchanged
- [ ] All scoring/recommendation rules unchanged

### No New Dependencies
- [ ] requirements.txt is unchanged
- [ ] App runs with same setup as before
- [ ] No new import errors

### Prototype Signals Removed
- [ ] No debug captions visible
- [ ] No "prototype" language in copy
- [ ] No Plotly toolbars visible
- [ ] Professional terminology throughout (e.g., "Quick Sales" vs "Fast-sale")

---

## Sign-Off

| Item | Checker | Date | Status |
|------|---------|------|--------|
| All checks passed | _______ | _______ | ☐ PASS |
| Ready for demo | _______ | _______ | ☐ YES |
| No outstanding issues | _______ | _______ | ☐ YES |

---

## Known Limitations / Future Improvements

- Pages 5-9 (Pricing, Liquidity, Yield, Costs, Data) are not in main navigation but still accessible via direct URL if needed
- Radio button CSS styling may need tweaks on older browsers (tested on Chrome/Safari/Edge)
- Mobile responsiveness not optimized (dashboard assumes laptop/desktop resolution)
