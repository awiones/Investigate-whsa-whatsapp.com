const puppeteer = require('puppeteer');
const fs = require('fs');

// The target URL
const url = 'https://dyieok9.xyz/aps/';

// Define a realistic mobile device to emulate
const mobileDevice = puppeteer.KnownDevices['Pixel 5'];

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  console.log(`Emulating a ${mobileDevice.name}...`);
  await page.emulate(mobileDevice);

  console.log(`Navigating to ${url}...`);
  try {
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });

    console.log('Page loaded successfully. Waiting for dynamic content...');

    // Wait for the loading animation to disappear and iframe to load
    console.log('Waiting for loading animation to complete...');
    await page.waitForFunction(() => {
      const loadingElement = document.querySelector('#res-loading');
      return loadingElement && loadingElement.style.display === 'none';
    }, { timeout: 30000 }).catch(() => {
      console.log('Loading animation timeout, continuing anyway...');
    });

    // Wait additional time for iframe content to load
    console.log('Waiting for iframe content to load...');
    await new Promise(resolve => setTimeout(resolve, 10000));

    // Try to access iframe content if possible
    try {
      const frames = await page.frames();
      console.log(`Found ${frames.length} frames on the page`);
      
      if (frames.length > 1) {
        const iframe = frames[1]; // Usually the first frame is the main page, second is the iframe
        console.log('Waiting for iframe to be ready...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    } catch (iframeError) {
      console.log('Could not access iframe content (likely cross-origin):', iframeError.message);
    }

    console.log('Taking screenshots at different intervals...');

    // Take multiple screenshots to capture different states
    await page.screenshot({ path: 'mobile_view_initial.png' });
    console.log('Initial screenshot saved as mobile_view_initial.png');

    await new Promise(resolve => setTimeout(resolve, 5000));
    await page.screenshot({ path: 'mobile_view_5s.png' });
    console.log('5-second screenshot saved as mobile_view_5s.png');

    await new Promise(resolve => setTimeout(resolve, 10000));
    await page.screenshot({ path: 'mobile_view_15s.png' });
    console.log('15-second screenshot saved as mobile_view_15s.png');

    // Save the current HTML state
    const pageContent = await page.content();
    fs.writeFileSync('page_source.html', pageContent);
    console.log('Final page source code saved as page_source_final.html');

    // Try to get network activity information
    console.log('Monitoring network activity for 10 more seconds...');
    const responses = [];
    page.on('response', response => {
      responses.push({
        url: response.url(),
        status: response.status(),
        headers: response.headers()
      });
    });

    await new Promise(resolve => setTimeout(resolve, 10000));
    
    // Save network activity log
    fs.writeFileSync('network_activity.json', JSON.stringify(responses, null, 2));
    console.log(`Captured ${responses.length} network responses in network_activity.json`);

  } catch (error) {
    console.error('Error during page interaction:', error);
  } finally {
    await browser.close();
    console.log('Browser closed after extended monitoring.');
  }
})();