# Rach Scope - Build Instructions

## Prerequisites

Before building, make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

## Building for Windows (.exe)

### Option 1: Using PyInstaller Spec File (Recommended)

```bash
# Build single-file executable
pyinstaller RachScope.spec

# The executable will be in: dist/RachScope.exe
```

### Option 2: Direct Command Line

```bash
# Build single-file executable without console
pyinstaller --onefile --noconsole --name RachScope --add-data "assets;assets" main.py

# The executable will be in: dist/RachScope.exe
```

### Creating a .exe installer (Optional)

For creating an installer, you can use [NSIS](https://nsis.sourceforge.io/):

1. Build the exe first: `pyinstaller RachScope.spec`
2. Create an NSIS script to package `dist/RachScope.exe`
3. Build the installer with NSIS

## Building for MacOS (.app / .dmg)

### Option 1: Using PyInstaller Spec File (Recommended)

```bash
# Build single-file application bundle
pyinstaller RachScope.spec

# The app will be in: dist/RachScope.app
```

### Option 2: Direct Command Line

```bash
# Build single-file application bundle without console
pyinstaller --onefile --noconsole --windowed --name RachScope --add-data "assets:assets" main.py

# The app will be in: dist/RachScope.app
```

### Creating a .dmg Disk Image

After building the .app, create a DMG:

```bash
# Install create-dmg tool (if not installed)
brew install create-dmg

# Create DMG from the app
create-dmg "dist/RachScope.app" "RachScope-1.0.0.dmg"

# The DMG will be created in: RachScope-1.0.0.dmg
```

Alternative method using hdiutil:

```bash
# Create a temporary directory
mkdir -p dmg_temp

# Copy the app to the temporary directory
cp -R dist/RachScope.app dmg_temp/

# Create the DMG
hdiutil create -volname "Rach Scope" -srcfolder dmg_temp -ov -format UDZO "RachScope-1.0.0.dmg"

# Clean up
rm -rf dmg_temp
```

## Building for Linux (Optional)

```bash
# Build single-file executable
pyinstaller RachScope.spec

# The executable will be in: dist/RachScope
```

## Adding Application Icon

### Windows (.ico)
1. Prepare your icon file: `assets/icon.ico`
2. Update the `icon` parameter in `RachScope.spec`:
   ```python
   icon='assets/icon.ico',
   ```

### MacOS (.icns)
1. Prepare your icon file: `assets/icon.icns`
2. Update the `icon` parameter in `RachScope.spec`:
   ```python
   icon='assets/icon.icns',
   ```

To create .icns from .png:
```bash
# Install iconutil
brew install iconutil

# Create iconset folder
mkdir -p icon.iconset

# Generate different sizes
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# Convert to .icns
iconutil -c icns icon.iconset -o icon.icns

# Move to assets folder
mv icon.icns assets/
rm -rf icon.iconset
```

## File Locations After Build

When the packaged application runs, data files will be stored in:

| Platform | Settings (settings.json) | Logs (hardware.log, data_manager.log) | Data Exports |
|----------|--------------------------|-------------------------------------|---------------|
| **Windows** | `%APPDATA%\RachScope\settings.json` | `%LOCALAPPDATA%\RachScope\logs\` | `%LOCALAPPDATA%\RachScope\` |
| **MacOS** | `~/Library/Preferences/RachScope/settings.json` | `~/Library/Logs/RachScope/` | `~/Library/Application Support/RachScope/` |
| **Linux** | `~/.config/RachScope/settings.json` | `~/.local/share/RachScope/logs/` | `~/.local/share/RachScope/` |

## Troubleshooting

### Build Errors

**Error: "ModuleNotFoundError: No module named 'xxx'"**
- Add the missing module to `hiddenimports` in `RachScope.spec`

**Error: "Icon not found"**
- Make sure the icon file exists in the `assets` folder
- Verify the icon format is correct (.ico for Windows, .icns for MacOS)

### Runtime Errors

**Error: "Permission denied" when writing settings/logs**
- The PathManager should handle this automatically
- If issues persist, check the user home directory permissions

**Error: "Application won't start" (MacOS)**
- The app may need to be unquarantined:
  ```bash
  xattr -cr dist/RachScope.app
  ```
- Or right-click the app and select "Open" from Finder

**Error: "Connection failed"**
- Verify the HF2211 device is reachable at the configured IP
- Check firewall settings
- Review `hardware.log` in the logs directory for details

## Clean Build Artifacts

To clean up build artifacts:

```bash
# Remove build directories
rm -rf build/
rm -rf dist/

# On Windows
rmdir /s /q build
rmdir /s /q dist
```

## Testing the Build

Before distribution, test the built executable:

1. **Windows:**
   ```bash
   dist\RachScope.exe
   ```

2. **MacOS:**
   ```bash
   open dist/RachScope.app
   ```

3. **Linux:**
   ```bash
   ./dist/RachScope
   ```

Verify:
- Application launches correctly
- Settings are saved to the correct location
- Logs are being written
- Hardware connection works
- CSV save/load functions work

## Signing the Application (Optional)

### Windows Code Signing

Use a code signing certificate and tools like `signtool` (included with Inno Setup):

```bash
signtool sign /f "dist/RachScope.exe" /d "Rach Scope" /du "https://your-website.com"
```

### MacOS Code Signing

```bash
# Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/RachScope.app

# For distribution, notarize the app (requires Apple Developer account)
xcrun notarytool submit dist/RachScope.app.dmg --apple-id your@email.com --password app-specific-password --team-id TEAMID --wait

# Staple the notarization ticket
xcrun stapler staple dist/RachScope.app.dmg
```

## Distribution

### Windows
- Package `dist/RachScope.exe` in a ZIP file
- Or create an installer using NSIS or Inno Setup

### MacOS
- Package `RachScope-1.0.0.dmg` for distribution
- The DMG should contain just the `RachScope.app`

### Linux
- Package `dist/RachScope` in a tar.gz or AppImage
- Create a .desktop file for desktop integration
