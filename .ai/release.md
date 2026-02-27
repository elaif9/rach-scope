# Release & Build Documentation

## Overview

RachScope menggunakan GitHub Actions untuk **automated cross-platform build**. Build hanya akan dijalankan ketika **Release baru dibuat**, dan file hasil build akan otomatis diupload ke halaman Release.

## Supported Platforms

| Platform | Output File | Format |
|----------|-------------|--------|
| Windows | `RachScope-Windows.zip` | ZIP berisi `RachScope.exe` |
| MacOS | `RachScope-MacOS.dmg` | DMG installer |

## Workflow Trigger

| Trigger | Deskripsi |
|---------|-----------|
| `release: created` | Otomatis build saat **Release baru dibuat** |
| `workflow_dispatch` | Manual trigger via GitHub UI (untuk testing) |

---

## Cara Membuat Release & Build

### Method 1: Via GitHub Web UI (Rekomendasi)

1. Buka repository di GitHub
2. Klik **Releases** di sidebar kanan → **Create a new release**
3. Isi form:
   - **Choose a tag**: `v1.0.0` (wajib diawali dengan `v`)
   - **Target**: Pilih branch (misal: `main`)
   - **Release title**: `RachScope v1.0.0`
   - **Description**: (opsional) tulis changelog
4. Klik **Publish release**

Build akan otomatis berjalan ±10-15 menit.

### Method 2: Via Git Command

```bash
# 1. Tag versi
git tag v1.0.0

# 2. Push tag ke GitHub
git push origin v1.0.0

# 3. Buat release (via GitHub CLI)
gh release create v1.0.0 \
  --title "RachScope v1.0.0" \
  --notes "Initial release"
```

### Method 3: Via GitHub CLI (Single Command)

```bash
# Install GitHub CLI jika belum
# MacOS: brew install gh
# Windows: winget install --id GitHub.cli

# Login
gh auth login

# Buat release (otomatis tag dan build)
gh release create v1.0.0 \
  --title "RachScope v1.0.0" \
  --notes "First stable release"
```

---

## Memantau Build Progress

Setelah release dibuat:

1. Buka **Actions** tab di GitHub repository
2. Klik workflow run terbaru "Build RachScope"
3. Lihat progress real-time:
   - ✅ `build-windows` - Build Windows executable
   - ✅ `build-macos` - Build MacOS application

Status:
- ⏳ **Queued** - Menunggu runner tersedia
- 🔵 **In progress** - Sedang build
- ✅ **Success** - Build selesai, file tersedia
- ❌ **Failed** - Build gagal, cek log error

---

## Download File Build

Setelah build sukses, file tersedia di:

```
https://github.com/[USERNAME]/[REPO]/releases/tag/v1.0.0
```

Di halaman release akan ada:
- ✅ `RachScope-Windows.zip` - Untuk Windows
- ✅ `RachScope-MacOS.dmg` - Untuk MacOS

### Windows

1. Download `RachScope-Windows.zip`
2. Extract ZIP file
3. Jalankan `RachScope.exe`
4. (Opsional) Pindahkan ke folder permanent (misal: `C:\Program Files\RachScope`)

### MacOS

1. Download `RachScope-MacOS.dmg`
2. Double-click `.dmg` untuk mount
3. Drag `RachScope.app` ke folder **Applications**
4. Buka dari Launchpad atau Applications folder

---

## Versioning Convention

Gunakan **Semantic Versioning** untuk tagging:

| Tag | Contoh | Artinya |
|-----|--------|---------|
| Major | `v1.0.0` → `v2.0.0` | Perubahan besar, breaking changes |
| Minor | `v1.0.0` → `v1.1.0` | Fitur baru, backward compatible |
| Patch | `v1.0.0` → `v1.0.1` | Bug fix, minor improvements |

Contoh:
- `v0.1.0` - Alpha release
- `v0.5.0` - Beta release
- `v1.0.0` - First stable release
- `v1.1.0` - Added new feature
- `v1.0.1` - Fixed bug

---

## Testing Build Tanpa Release

Untuk testing workflow tanpa membuat release:

1. Buka repository → **Actions** tab
2. Pilih workflow "Build RachScope"
3. Klik **Run workflow**
4. Pilih branch (misal: `main`)
5. Klik **Run workflow**

Build akan berjalan tapi **TIDAK upload ke release page**. Gunakan ini untuk:
- Testing code sebelum release
- Debugging workflow issues
- Verifikasi build works

---

## Changelog Template

Gunakan template ini untuk deskripsi release:

```markdown
## RachScope v1.0.0

### New Features
- Feature 1 description
- Feature 2 description

### Bug Fixes
- Fixed bug description

### Improvements
- Improved performance
- Updated dependencies

### System Requirements
- Windows 10/11
- MacOS 10.15+ (Catalina)
- 4GB RAM minimum

### Installation
- Windows: Download .zip, extract, run exe
- MacOS: Download .dmg, install to Applications

### Notes
- Notes about this release
```

---

## Troubleshooting

### Build Failed

Jika build gagal:
1. Buka Actions tab → Klik failed workflow
2. Klik job yang gagal (misal: `build-windows`)
3. Scroll ke bawah → Lihat error message

Common errors:
- **"Module not found"** → Tambah modul ke `RachScope.spec` (hiddenimports)
- **"Build timeout"** → Build terlalu lama (>6 jam)
- **"Permission denied"** → Cek `permissions: contents: write` di workflow

### File Tidak Muncul di Release

Jika file tidak muncul:
1. Pastikan release **dibuat dari tag** (bukan dari commit)
2. Cek Actions → Pastikan workflow success
3. Cek logs → Search "Upload to Release" step

### Build Terlalu Lama

Normal build time:
- Windows: ±5-10 menit
- MacOS: ±5-10 menit

Jika lebih dari 30 menit:
- Cek logs di Actions
- Mungkin ada dependency issue
- Pertimbangkan update `RachScope.spec`

---

## File Locations After Installation

| Platform | Settings (settings.json) | Logs | Data Exports |
|----------|--------------------------|------|---------------|
| **Windows** | `%APPDATA%\RachScope\settings.json` | `%LOCALAPPDATA%\RachScope\logs\` | `%LOCALAPPDATA%\RachScope\` |
| **MacOS** | `~/Library/Preferences/RachScope/settings.json` | `~/Library/Logs/RachScope/` | `~/Library/Application Support/RachScope/` |

---

## Signing Application (Optional)

Untuk production release, pertimbangkan signing:

### Windows Code Signing

Menghindari Windows SmartScreen warning:
```powershell
# Sign exe with certificate
signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.digicert.com dist/RachScope.exe
```

### MacOS Code Signing

Untuk menghindari quarantine warning:
```bash
# Sign app
codesign --deep --force --verify --verbose --sign "Developer ID" dist/RachScope.app

# Notarize (memerlukan Apple Developer account)
xcrun notarytool submit "RachScope-MacOS.dmg" --apple-id your@email.com --password app-specific-password --team-id TEAMID --wait

# Staple notarization
xcrun stapler staple "RachScope-MacOS.dmg"
```

---

## Quick Reference

```bash
# Tag dan release
git tag v1.0.0 && git push origin v1.0.0

# Release dengan GitHub CLI
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes"

# Lihat semua tags
git tag -l

# Delete tag (jika salah tag)
git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0
```

---

## Support

Jika mengalami masalah:
1. Cek [Actions tab](https://github.com/[USERNAME]/[REPO]/actions) untuk build logs
2. Lihat [BUILD.md](./BUILD.md) untuk instruksi build manual
3. Buka issue di GitHub repository

---

**Happy Roasting! ☕**
