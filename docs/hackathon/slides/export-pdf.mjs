import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();

await page.setViewport({ width: 1920, height: 1080 });
await page.goto('file://' + join(__dirname, 'index.html'), { waitUntil: 'networkidle0' });

// Get all slides
const slideCount = await page.evaluate(() => document.querySelectorAll('.slide').length);
console.log('Found ' + slideCount + ' slides');

// Export as PDF with each slide as a page
await page.pdf({
  path: join(__dirname, 'PrecisionBOM_Deck.pdf'),
  width: '1920px',
  height: '1080px',
  printBackground: true,
});

console.log('PDF exported to PrecisionBOM_Deck.pdf');
await browser.close();
