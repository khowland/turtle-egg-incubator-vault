# Turtle-DB Performance Optimization Roadmap (v8.2.0+)

Based on the system-wide audit conducted on April 23, 2026, we have identified key areas to improve user experience and reduce perceived latency.

## 1. Network & Infrastructure

- [ ] **Streamlit Health Check Fix**: Resolve the `net::ERR_EMPTY_RESPONSE` for `/_stcore/health`. This is causing 1-2s of artificial waiting on every page transition as the client retries the connection.
  - *Recommendation*: Update Docker network bridge settings or set `server.address = "0.0.0.0"` in `config.toml`.

## 2. UI & Frontend Optimization

- [ ] **Fragmented Rendering**: Implement `st.fragment` on the Dashboard "Recent Vault Activity" and "Mortality Heatmap". This will allow the sidebar and filters to remain responsive without re-rendering heavy Plotly charts.
- [ ] **Lazy Loading Bin Observations**: The `Observations` page currently fetches all logs. Implement pagination or a "Load More" pattern to speed up the initial view.

## 3. Database & Backend

- [ ] **Pre-fetching Session Metadata**: Load user roles and settings once per session rather than per-page to save ~200ms per navigation.
- [ ] **Query Pruning**: Review `fetch_key_performance_indicators` to ensure it only selects necessary columns (already improved in v8.1.3).

## 4. Branding & Visuals

- [x] **Lightweight Spinner**: replaced default icon with animated CSS turtle emoji (Lower payload).
- [x] **Mobile Ergonomics**: Reduced top-padding by 60% for better small-screen visibility.

---
*Documented by Antigravity AI for the Turtle-DB Clinical Suite.*
