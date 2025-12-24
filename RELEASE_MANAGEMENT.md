# Release Management & Distribution

## Release Process

### Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0) - Breaking changes
- **MINOR** (1.1.0) - New features (backward compatible)
- **PATCH** (1.0.1) - Bug fixes

### Pre-Release Checklist

- [ ] Update version in `package.json`
- [ ] Update `CHANGELOG.md` with new features/fixes
- [ ] Run full test suite: `npm test`
- [ ] Run coverage report: `npm run test:coverage`
- [ ] Manual testing on all platforms using checklist
- [ ] Build for all platforms: `npm run build`
- [ ] Test each build locally
- [ ] All git changes committed and pushed

### Creating a Release

```bash
# 1. Update version
npm version patch  # or minor, major
# This updates package.json and creates a git tag

# 2. Build for all platforms
npm run build

# 3. Commit version bump (if not auto-committed)
git add -A
git commit -m "Bump version to 1.0.1"
git push origin master

# 4. Create GitHub Release
git push origin --tags
```

### GitHub Release Creation

1. Go to [GitHub Releases](https://github.com/your-username/baidoxe/releases)
2. Click "Draft a new release"
3. Select the tag you just created (e.g., v1.0.1)
4. Fill in release details:

```markdown
# Version 1.0.1

## 🎉 Features
- Feature 1
- Feature 2

## 🐛 Bug Fixes
- Bug fix 1
- Bug fix 2

## 📦 Installation

### Windows
Download `Baidoxe-1.0.1.exe` (installer) or `Baidoxe-1.0.1-x64-win.exe` (portable)

### macOS
Download `Baidoxe-1.0.1.dmg`

### Linux
Download `Baidoxe-1.0.1.AppImage`

## 🔧 Improvements
- Improvement 1
- Improvement 2

## ⚠️ Breaking Changes
(if any)

## 🙏 Contributors
Thank you to all contributors!
```

5. Upload release artifacts:
   - `dist/Baidoxe-1.0.1.exe` (Windows NSIS installer)
   - `dist/Baidoxe-1.0.1-x64-win.exe` (Windows portable)
   - `dist/Baidoxe-1.0.1.dmg` (macOS)
   - `dist/Baidoxe-1.0.1.AppImage` (Linux AppImage)
   - `dist/latest.yml` (auto-updater metadata)
   - `dist/latest-mac.yml` (macOS updater metadata - if created)

6. Publish release

## Changelog Maintenance

### CHANGELOG.md Format

```markdown
# Changelog

All notable changes to Baidoxe are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.1] - 2025-01-18

### Added
- New parking slot visualization
- Update notification system
- Auto-update functionality

### Fixed
- Backend connection timeout issue
- Windows portable executable path handling
- Memory leak in logs viewer

### Changed
- Improved performance monitoring
- Updated notification styling
- Refactored API error handling

### Deprecated
- Old backup format (migrate in v2.0.0)

### Removed
- Legacy test runner

### Security
- Fixed XSS vulnerability in data export
- Added input validation to all API calls

## [1.0.0] - 2025-01-10

### Added
- Initial desktop application release
- Auto-start Flask backend
- System tray integration
- React component reuse from web app
- Cross-platform builds (Windows, macOS, Linux)
```

## Distribution Channels

### Windows

**NSIS Installer:**
- Easiest for end users
- Creates Start menu shortcuts
- Creates desktop shortcut
- Handles uninstallation
- File: `Baidoxe-1.0.1.exe`

**Portable Executable:**
- No installation needed
- Can run from USB drive
- No registry entries
- File: `Baidoxe-1.0.1-x64-win.exe`

Distribution:
1. Upload both to GitHub Releases
2. Upload to software directories (Softpedia, SourceForge, etc.)
3. Create software announcement

### macOS

**DMG Installer:**
- Mount DMG file
- Drag app to Applications folder
- Standard macOS installation method
- File: `Baidoxe-1.0.1.dmg`

**ZIP Archive:**
- Alternative for archival
- File: `Baidoxe-1.0.1.zip`

Requirements:
- Code signing certificate (Developer ID)
- Notarization for Gatekeeper
- Sparkle framework for updates (optional)

Distribution:
1. Upload to GitHub Releases
2. Submit to Mac App Store (optional)
3. Host on website

### Linux

**AppImage:**
- Single executable file
- No dependencies
- Works on most Linux distributions
- File: `Baidoxe-1.0.1.AppImage`

**DEB Package:**
- For Debian/Ubuntu systems
- Standard package management
- File: `baidoxe-1.0.1.deb`

Distribution:
1. Upload to GitHub Releases
2. Create PPA (Personal Package Archive)
3. Submit to software repositories
4. List on Linux app directories

## Update Delivery

### Automatic Updates

Users with the app installed will:
1. See notification when update is available
2. Update downloads in background
3. See "Restart to Update" prompt
4. Update installs on restart

### Staged Rollout

Deploy to percentage of users:
```javascript
// In main.js
if (Math.random() < 0.1) {  // 10% of users
  autoUpdater.downloadUpdate();
}
```

Stages:
1. 1% of users (day 1)
2. 5% of users (day 2)
3. 25% of users (day 3)
4. 100% of users (day 4+)

Monitor crash reports between stages.

### Rollback

If update has critical issue:

1. Delete problematic release from GitHub
2. Keep previous version available
3. Users will remain on previous version
4. Create fixed release

## Analytics & Monitoring

### Track Updates

```javascript
autoUpdater.on('update-downloaded', (info) => {
  // Send analytics
  fetch('https://analytics.example.com/update', {
    method: 'POST',
    body: JSON.stringify({
      app: 'baidoxe',
      version: app.getVersion(),
      newVersion: info.version,
      platform: process.platform,
      timestamp: new Date().toISOString()
    })
  });
});
```

### Monitor Crashes

Integrate Sentry or similar:
```javascript
import * as Sentry from "@sentry/electron";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: isDev ? 'development' : 'production'
});
```

### Track Downloads

GitHub releases automatically track download counts.

View statistics:
- GitHub Releases page shows download count
- Google Analytics if you host downloads
- Sentry tracks crashes by version

## Continuous Deployment (CD)

### GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      
      - name: Install dependencies
        run: cd desktop && npm ci
      
      - name: Build
        run: cd desktop && npm run build
        env:
          CSC_LINK: ${{ secrets.MACOS_CERT }}
          CSC_KEY_PASSWORD: ${{ secrets.MACOS_CERT_PASSWORD }}
          WINDOWS_CERT: ${{ secrets.WINDOWS_CERT }}
          WINDOWS_CERT_PASSWORD: ${{ secrets.WINDOWS_CERT_PASSWORD }}
      
      - name: Upload Release Assets
        uses: softprops/action-gh-release@v1
        with:
          files: desktop/dist/**
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Security Considerations

### Code Signing

**Windows:**
```bash
# Create self-signed certificate for testing
signtool sign /f certificate.pfx /p password /t http://timestamp.server.com dist/*.exe
```

**macOS:**
- Requires Apple Developer ID
- Automatic signing with xcode
- Notarization required for distribution

**Linux:**
- Sign with GPG key
- Create signature files
- Publish public key

### Update Signature Verification

electron-updater automatically verifies:
- ASAR integrity
- Code signatures (macOS/Windows)
- Hash verification (all platforms)

## Support for Older Versions

### Bug Fixes in Old Versions

If critical bug found:
1. Create branch from old release tag
2. Fix bug
3. Create new release (e.g., 1.0.2 for 1.0.x branch)
4. Release separately

### Deprecation Timeline

- Latest version: Full support
- Previous major version: Security fixes only
- Older versions: No support (users should upgrade)

## Post-Release

### Day 1
- Monitor crash reports
- Check user feedback
- Monitor download count
- Verify auto-update working

### Week 1
- Stability issues → patch release
- Feature requests → document for next release
- Community feedback → engage and respond

### Monthly
- Compile analytics
- Plan next release
- Review open issues
- Update documentation

## Release Checklist

- [ ] Version bumped
- [ ] CHANGELOG.md updated
- [ ] All tests passing
- [ ] Manual testing complete
- [ ] Build successful on all platforms
- [ ] Artifacts created and verified
- [ ] GitHub release created
- [ ] Release notes written
- [ ] Announcement posted
- [ ] First-week monitoring plan
- [ ] Analytics tracking configured
- [ ] Auto-update verified working

