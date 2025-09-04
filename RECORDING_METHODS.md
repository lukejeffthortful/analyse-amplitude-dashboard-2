# Recording Browser Interactions for Automation

## Method 1: Playwright Codegen (Recommended)

### Start Recording:
```bash
source venv/bin/activate
playwright codegen https://hq1.appsflyer.com/auth/login
```

### Features:
- Real-time code generation
- Shows selectors for each click
- Automatically handles waits
- Can save authentication state

### Save auth for reuse:
```bash
playwright codegen --save-storage=auth.json https://hq1.appsflyer.com
# Next time, load saved auth:
playwright codegen --load-storage=auth.json https://hq1.appsflyer.com
```

## Method 2: Chrome DevTools Recorder

1. Open Chrome DevTools (F12)
2. Go to "Recorder" tab (might need to enable in settings)
3. Click "Start new recording"
4. Perform your actions
5. Export as Puppeteer/Playwright script

## Method 3: Browser Extensions

### Selenium IDE
- Chrome/Firefox extension
- Records and plays back tests
- Exports to multiple languages

### Katalon Recorder
- Free Chrome extension
- Advanced recording features
- Exports to various frameworks

## Method 4: Playwright Trace Viewer

Record a trace file and analyze it:

```python
# Start trace
await context.tracing.start(screenshots=True, snapshots=True)

# Your actions here...

# Stop and save
await context.tracing.stop(path="trace.zip")
```

View trace:
```bash
playwright show-trace trace.zip
```

## Method 5: Custom Event Recorder

Record actual click coordinates and elements:

```javascript
// Inject into page
document.addEventListener('click', (e) => {
    console.log({
        selector: getSelector(e.target),
        x: e.clientX,
        y: e.clientY,
        text: e.target.innerText
    });
});
```

## Tips for Recording

1. **Go slowly** - Give pages time to load
2. **Use unique actions** - Avoid ambiguous clicks
3. **Check generated selectors** - Ensure they're stable
4. **Test the recording** - Replay to verify it works
5. **Add waits** - Recording might be too fast

## Converting Recordings

From Chrome DevTools recording to Playwright:
```python
# Chrome records: click on "button.submit"
# Convert to: await page.click('button.submit')
```

From Selenium IDE to Playwright:
```python
# Selenium: driver.find_element(By.CSS_SELECTOR, ".button").click()
# Convert to: await page.click('.button')
```