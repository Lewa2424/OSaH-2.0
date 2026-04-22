# Legacy Desktop UI — Migration Layer

## ⚠️ DEPRECATED — This layer is no longer the primary UI

This directory contains the original **Tkinter/CustomTkinter-based desktop interface** for OSaH 2.0.

### Current Status

**As of stabilization step (2026-04-22):**
- ✅ **Desktop UI is fully functional** and contains mature implementations of security flow, work permits, training records, medical records, and PPE tracking
- ⚠️ **Desktop UI is NOT the active production UI anymore**
- 🆕 **The new PySide6 Qt UI** (`src/osah/ui/qt/`) is now the single primary working frontend
- 🔄 **Migration in progress:** Mature features from this layer are being ported to Qt

### What You Should Know

1. **Do NOT** add new features to this layer
2. **Do NOT** start new development in `ui/desktop/` 
3. **Use this layer only for:**
   - Reference implementations (especially security patterns)
   - Temporary debugging
   - Historical understanding of UI flows

### Security Flow Reference

This layer has working implementations of:
- Initial security setup screen (`security/render_initial_security_setup_screen.py`)
- Login screen with role selection (`security/render_login_screen.py`)
- Recovery/reset access screen (`security/render_access_reset_screen.py`)
- Authenticated shell routing (`run_desktop_application.py`)

These patterns are being **ported to PySide6** in `src/osah/ui/qt/security/` and should be used as reference only.

### Future

This directory will eventually be:
1. Moved to `archived/` or `deprecated/`
2. Removed entirely after full migration to Qt
3. Replaced by `src/osah/ui/qt/` as the single UI layer

---

**For all new development, work in:** `src/osah/ui/qt/`
