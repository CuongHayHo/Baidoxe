# Quality Assurance Guidelines

## QA Process Overview

### Phase 1: Unit & Integration Testing
- Run automated test suite
- Check code coverage targets
- Verify mock data and API integration
- Test error handling paths

### Phase 2: Manual Testing
- Execute test checklist
- Test across platforms
- Verify all features working
- Check user experience

### Phase 3: Performance Testing
- Monitor startup time
- Check memory usage
- Verify CPU usage
- Load test with large datasets

### Phase 4: Security Testing
- Review IPC security
- Check data protection
- Verify no credentials exposed
- Test error messages for info leakage

### Phase 5: Release Preparation
- Final regression testing
- Documentation review
- Build verification
- Release notes creation

## Test Coverage Guidelines

### Minimum Coverage Targets
```
Global threshold:
- Branches: 70%
- Functions: 80%
- Lines: 80%
- Statements: 80%

Critical path (API, IPC): 90%+
UI components: 70%+
Utilities: 90%+
```

### Coverage Report
```bash
npm run test:coverage
```

View coverage in: `desktop/coverage/lcov-report/index.html`

## Automated Testing

### Unit Tests
- React component rendering
- Hook behavior
- Utility functions
- API client methods

```bash
npm test -- --testPathPattern="/__tests__/"
```

### Integration Tests
- API + Component interaction
- IPC bridge communication
- State management
- Error scenarios

```bash
npm test -- --testPathPattern="/integration"
```

### E2E Tests
- Complete user workflows
- Multi-step operations
- Native features
- Performance metrics

```bash
npm run test:e2e
```

## Manual Testing Protocol

### Setup
1. Use fresh build: `npm run build`
2. Ensure backend running
3. Have test data prepared
4. Document OS/browser/hardware

### Execution
1. Follow MANUAL_TESTING_CHECKLIST.md
2. Document any issues
3. Take screenshots of failures
4. Note reproduction steps
5. Record performance metrics

### Reporting
- Use issue template in repository
- Include OS, version, build number
- Attach screenshots/logs
- Provide reproduction steps
- Specify severity level

### Severity Levels

**Critical:** 
- App crashes
- Data loss
- Security vulnerability
- Complete feature failure
→ Block release

**High:**
- Feature doesn't work as documented
- Major UI/UX issue
- Performance problem (>10 sec)
→ Fix before release (if possible)

**Medium:**
- Minor feature issue
- UI inconsistency
- Performance degradation (2-10 sec)
→ Document and may release

**Low:**
- Cosmetic issues
- Minor text problems
- Documentation gaps
→ Nice to fix but not blocking

## Performance Benchmarks

### Acceptable Metrics

| Metric | Target | Maximum |
|--------|--------|---------|
| Startup Time | 2-3s | 5s |
| Tab Switch Time | <100ms | 500ms |
| Initial Data Load | <2s | 5s |
| Memory (Idle) | <200MB | 300MB |
| Memory (Running) | <400MB | 600MB |
| CPU (Idle) | <1% | 5% |
| CPU (Operation) | <30% | 50% |

### Profiling

```bash
# Enable DevTools in main.js
# Then in app: Ctrl+Shift+I

# Check Performance tab:
# - Record operation
# - Analyze flame chart
# - Look for long tasks
# - Verify memory growth
```

## Cross-Platform Testing

### Windows Testing
```
OS Versions: 7, 8, 10, 11
Architectures: x64, x86
Installer types: NSIS, Portable
```

### macOS Testing
```
OS Versions: 10.12+, latest major version
Architectures: Intel, Apple Silicon (native)
Notarization: Required for distribution
```

### Linux Testing
```
Distributions: Ubuntu, Fedora, Debian
Architectures: x64, ARM64
Package formats: AppImage, DEB
```

## Git Workflow for Testing

### Test Branch
```bash
# Create test branch from main
git checkout -b test/v1.0.0

# Make test-specific changes
# Run full test suite

# If all pass
git checkout main
git merge test/v1.0.0

# If failures
# Fix issues, commit to test branch
# Merge once fixed
```

### Test Tags
```bash
# Tag release candidate
git tag -a v1.0.0-rc1 -m "Release candidate 1"

# Tag final release
git tag -a v1.0.0 -m "Version 1.0.0 released"

# Push tags
git push origin --tags
```

## Bug Reporting Template

```markdown
## Bug Title
[Clear, concise description]

## Environment
- OS: Windows/macOS/Linux
- OS Version: 10/11/Big Sur/Ubuntu 20.04
- App Version: 1.0.0
- Build #: abc123

## Reproduction Steps
1. ...
2. ...
3. ...

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Screenshots/Logs
[Attach images, error logs]

## Additional Context
[Any other relevant info]

## Severity
[ ] Critical
[ ] High
[ ] Medium
[ ] Low
```

## Test Report Template

```markdown
# QA Report - Version X.X.X
Date: YYYY-MM-DD
Tested By: [Name]
Build: [Build number]

## Executive Summary
[High-level overview of testing results]

## Test Coverage
- Unit Tests: XX%
- Integration Tests: Complete/Partial/None
- E2E Tests: Complete/Partial/None
- Manual Tests: XX% of checklist

## Platform Testing
| Platform | Status | Issues | Notes |
|----------|--------|--------|-------|
| Windows 11 | ✅/⚠️/❌ | [count] | |
| macOS 13 | ✅/⚠️/❌ | [count] | |
| Linux (Ubuntu) | ✅/⚠️/❌ | [count] | |

## Issues Found

### Critical (Block Release)
[List any critical issues]

### High Priority
[List high priority issues]

### Medium Priority
[List medium priority issues]

### Low Priority
[List low priority issues]

## Performance Results
- Startup Time: X.Xs
- Memory Usage: XMB (idle), XMB (loaded)
- CPU Usage: X% (idle), X% (running)
- Data Load Time: Xs (1000 items)

## Recommendations
[List recommendations for next release]

## Sign-Off
- [ ] Ready for Release
- [ ] Ready with Known Issues
- [ ] Not Ready - Requires Fixes

Approved by: ________________
Date: ________________
```

## Continuous Integration / Continuous Deployment

### GitHub Actions Workflow

```yaml
name: Test & Build
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      
      - name: Install dependencies
        run: cd desktop && npm ci
      
      - name: Run tests
        run: cd desktop && npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./desktop/coverage/lcov.info
      
      - name: Build
        run: cd desktop && npm run build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: desktop/dist/

  e2e:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      
      - name: Install dependencies
        run: cd desktop && npm ci
      
      - name: Build
        run: cd desktop && npm run build
      
      - name: Run E2E tests
        run: cd desktop && npm run test:e2e
      
      - name: Upload E2E results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-results-${{ matrix.os }}
          path: desktop/e2e/
```

## Testing Tools & Commands

### Run All Tests
```bash
cd desktop
npm test                    # All tests
npm run test:watch        # Watch mode
npm run test:coverage     # With coverage
npm run test:debug        # Debug mode
npm run test:e2e          # E2E only
```

### Individual Test File
```bash
npm test -- Dashboard.test.tsx
npm test -- integration.test
npm test -- api.test
```

### Generate Coverage Report
```bash
npm run test:coverage
# Open: coverage/lcov-report/index.html
```

### Debug Tests
```bash
npm run test:debug
# Open: chrome://inspect
```

## Quality Metrics Dashboard

### Track These Metrics
- Test pass rate (%)
- Code coverage (%)
- Critical bugs (count)
- Average bug fix time (hours)
- Performance metrics (startup, memory, CPU)
- User-reported issues (count)

### Monthly Review
- Compile metrics from all testing phases
- Identify trends and patterns
- Plan improvements for next cycle
- Document lessons learned
- Update testing procedures based on findings

## Post-Release Monitoring

### First Week
- Monitor user reports
- Check crash logs (if enabled)
- Verify no critical issues
- Track performance metrics
- Respond to user feedback

### Ongoing
- Monthly QA metrics review
- Update test suite based on new features
- Refactor tests as codebase evolves
- Archive test reports
- Plan next testing cycle

