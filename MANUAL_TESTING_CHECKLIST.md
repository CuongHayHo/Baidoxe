# Manual Testing Checklist

## Pre-Testing Setup
- [ ] Fresh build: `npm run build`
- [ ] Backend running on port 5000
- [ ] Test data prepared (cards, parking slots)
- [ ] Network connection stable
- [ ] System resources available

## Functionality Testing

### Dashboard Tab
- [ ] Page loads without errors
- [ ] Statistics display correctly (total cards, active cards, available slots)
- [ ] Real-time updates work when data changes
- [ ] No visual glitches or layout issues
- [ ] Responsive to different window sizes

### Cards Tab
- [ ] Card list loads and displays
- [ ] Can scroll through card list
- [ ] Card information is accurate (UID, status, created date)
- [ ] Status indicators show correct colors
- [ ] Search/filter works if available
- [ ] Can add new card via form
  - [ ] Form validation works
  - [ ] Success message displays
  - [ ] New card appears in list
  - [ ] Backend receives data
- [ ] Can delete card
  - [ ] Confirmation dialog shows
  - [ ] Card removed from list
  - [ ] Backend updated

### Parking Slots Tab
- [ ] Parking slot grid displays
- [ ] Slot status colors correct (available/occupied)
- [ ] Slot count matches backend
- [ ] Real-time updates when slots change
- [ ] No layout overflow on different resolutions
- [ ] Slot numbers are correct

### Logs Tab
- [ ] Log list displays with data
- [ ] Can scroll through logs
- [ ] Log entries are chronological
- [ ] Timestamp format is readable
- [ ] Can filter/search logs if available
- [ ] Large log files load without freezing
- [ ] "Clear Logs" button works (with confirmation)

### Admin Tab
- [ ] Admin panel displays without errors
- [ ] All admin buttons visible and clickable

#### Backup Operations
- [ ] "Create Backup" button works
  - [ ] Backup file created
  - [ ] File timestamp accurate
  - [ ] Confirmation message shows
  - [ ] Backup appears in list
- [ ] "Restore Backup" works
  - [ ] Restore dialog opens
  - [ ] Select backup file
  - [ ] Restoration completes
  - [ ] Data restored correctly
- [ ] "Delete Backup" works
  - [ ] Confirmation dialog shows
  - [ ] Backup removed
  - [ ] List updates

#### System Operations
- [ ] "Fix Data" button executes
  - [ ] Processing indicator shows
  - [ ] Completion message displays
  - [ ] Data integrity verified
- [ ] "Clear Logs" button works
  - [ ] Confirmation dialog shows
  - [ ] Logs cleared after confirmation
  - [ ] Logs tab shows empty
- [ ] "Export Report" button works
  - [ ] File save dialog opens
  - [ ] JSON file created with valid data
  - [ ] File readable with valid structure
- [ ] "Reset System" button works
  - [ ] Warning dialog shows
  - [ ] Requires confirmation
  - [ ] System resets to default state
  - [ ] All data cleared

## Native Features Testing

### Notifications
- [ ] Notification appears when triggered
- [ ] Notification displays correct title and message
- [ ] Notification auto-dismisses after timeout
- [ ] Can click to dismiss manually
- [ ] Multiple notifications queue properly
- [ ] No notification overlaps on screen

### File Dialogs
- [ ] File open dialog filters correct file types
- [ ] Can navigate directories
- [ ] File selection works
- [ ] File save dialog shows default filename
- [ ] Can change save location
- [ ] Can change filename
- [ ] File saved to correct location

### Data Export
- [ ] Export creates valid JSON file
- [ ] JSON is properly formatted
- [ ] All data fields included
- [ ] File is readable by other applications
- [ ] Large exports complete without error

### System Tray (Windows/Linux)
- [ ] Tray icon visible when minimized
- [ ] Right-click context menu appears
- [ ] "Show" option restores window
- [ ] "Exit" option closes app properly
- [ ] Window can be restored from tray
- [ ] Tray icon shows correct state

### Menu Bar (macOS)
- [ ] Application menu appears
- [ ] All menu items functional
- [ ] Keyboard shortcuts work

## Backend Integration Testing

### Initial Connection
- [ ] App detects running backend on startup
- [ ] Backend status indicator shows correct state
- [ ] If backend not running, appropriate message shown
- [ ] Auto-start backend works (if configured)
- [ ] Connection retries if backend delayed

### API Communication
- [ ] All data loads correctly from API
- [ ] Timestamps are accurate
- [ ] Data updates reflect backend changes
- [ ] Error responses handled gracefully
- [ ] Timeouts don't freeze UI
- [ ] Fallback URLs work if primary fails

### Backend Shutdown
- [ ] Can gracefully shutdown backend from app
- [ ] System state saved before shutdown
- [ ] Backend restarts properly
- [ ] No data loss on restart

## Cross-Platform Testing

### Windows
- [ ] Installer runs without errors
- [ ] Desktop shortcut created
- [ ] Start menu shortcut created
- [ ] App launches from shortcuts
- [ ] Portable version works
- [ ] Uninstaller removes app properly
- [ ] Registry entries correct (if applicable)
- [ ] System tray works
- [ ] Window buttons (minimize, maximize, close) work
- [ ] Right-click context menu works

### macOS
- [ ] DMG mounts and installs
- [ ] App launches from Applications folder
- [ ] Notarization passes
- [ ] Sandbox settings correct
- [ ] Permissions dialog appears for file access
- [ ] Keyboard shortcuts work correctly
- [ ] Menu bar integration works
- [ ] Can drag app to dock

### Linux
- [ ] AppImage extracts and runs
- [ ] Desktop entry created
- [ ] App appears in application menu
- [ ] System integration works
- [ ] File dialogs use native file manager
- [ ] System tray integration works
- [ ] Scaling works on HiDPI displays

## Performance Testing

### Launch Time
- [ ] App starts in < 5 seconds
- [ ] First screen renders quickly
- [ ] No lag during initial load
- [ ] Progress indicator visible if delay needed

### Runtime Performance
- [ ] Smooth scrolling in lists
- [ ] No freezing during operations
- [ ] Tab switching is responsive
- [ ] Data loading doesn't block UI
- [ ] Multiple simultaneous operations work

### Memory Management
- [ ] Memory usage stable over time
- [ ] No memory leaks after 1 hour
- [ ] Large datasets (1000+ cards) handled
- [ ] Export doesn't cause memory spike
- [ ] Repeated operations don't leak memory

### CPU Usage
- [ ] CPU minimal when idle
- [ ] Normal operations don't spike CPU
- [ ] Monitoring doesn't cause high CPU
- [ ] Export completes without hanging

## Error Handling & Recovery

### Network Errors
- [ ] Network disconnect shows appropriate message
- [ ] App doesn't crash
- [ ] Auto-reconnect attempts
- [ ] UI remains responsive
- [ ] Data from before disconnection preserved

### Backend Errors
- [ ] Backend crash handled gracefully
- [ ] Error message displayed to user
- [ ] User can attempt reconnect
- [ ] No data corruption on backend error

### Data Corruption
- [ ] Corrupted data detected and reported
- [ ] Repair option available
- [ ] System recovers without data loss
- [ ] User notified of any data issues

### Edge Cases
- [ ] Empty data sets handled
- [ ] Very large data sets handled
- [ ] Special characters in data work
- [ ] Null/undefined values handled
- [ ] Rapid user actions don't break app

## Accessibility Testing

### Keyboard Navigation
- [ ] All controls accessible via keyboard
- [ ] Tab order is logical
- [ ] Enter key activates buttons
- [ ] Escape key closes dialogs
- [ ] Shortcuts clearly indicated

### Screen Reader Support
- [ ] ARIA labels present on controls
- [ ] Form inputs have associated labels
- [ ] Icons have alt text where appropriate
- [ ] Error messages are announced

### Visual
- [ ] Contrast ratios meet WCAG standards
- [ ] Text size is readable (min 12px)
- [ ] Colors don't convey information alone
- [ ] Focus indicators visible

## Security Testing

### Data Protection
- [ ] Sensitive data not logged to console
- [ ] Backup files encrypted if needed
- [ ] No credentials in local storage
- [ ] Database connections secure

### IPC Security
- [ ] Only whitelisted IPC channels exposed
- [ ] Input validation on all IPC messages
- [ ] No arbitrary code execution possible
- [ ] API calls have proper error handling

### File Operations
- [ ] File dialogs can't access system files
- [ ] Export files have correct permissions
- [ ] No path traversal vulnerabilities
- [ ] Temp files cleaned up

## Documentation Testing

### Help & Instructions
- [ ] Help docs are accessible
- [ ] Instructions are clear and accurate
- [ ] Links in docs work
- [ ] Examples are correct
- [ ] Troubleshooting section helpful

### Version Information
- [ ] Version number displayed correctly
- [ ] Build information available
- [ ] About dialog complete
- [ ] License displayed

## Regression Testing

### Previous Features
- [ ] All previously working features still work
- [ ] No visual regressions
- [ ] No performance regressions
- [ ] Previous bugs haven't reappeared

### API Backwards Compatibility
- [ ] Older API versions still work (if supported)
- [ ] Deprecation warnings clear
- [ ] Migration path documented

## Sign-Off

**Tested by:** _______________
**Date:** _______________
**Build Version:** _______________
**Platform:** Windows / macOS / Linux
**OS Version:** _______________

**Overall Status:**
- [ ] All tests passed - Ready for release
- [ ] Minor issues - Document and release with known issues
- [ ] Critical issues - Do not release, fix and retest

**Issues Found:**
1. 
2. 
3. 

**Recommendations:**

