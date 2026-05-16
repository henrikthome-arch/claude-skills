#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import sharp from 'sharp';

const { values } = parseArgs({
  options: {
    prompt: { type: 'string' },
    model: { type: 'string', default: 'flux' },
    aspect: { type: 'string', default: '1:1' },
    output: { type: 'string' },
  },
});

if (!values.prompt || !values.output) {
  console.error('Usage:');
  console.error('  node --env-file=.env.local scripts/generate-image.mjs \\');
  console.error('    --prompt "..." \\');
  console.error('    --output output/file.webp \\');
  console.error('    [--model flux|nb2] \\');
  console.error('    [--aspect 1:1|4:5|9:16|16:9]');
  process.exit(1);
}

const apiKey = process.env.OPENROUTER_API_KEY;
if (!apiKey) {
  console.error('OPENROUTER_API_KEY is not set.');
  console.error('Run ./setup.sh, and invoke with `node --env-file=.env.local …`.');
  process.exit(1);
}

const MODELS = {
  flux: { id: 'black-forest-labs/flux.2-pro', modalities: ['image'] },
  nb2:  { id: 'google/gemini-3.1-flash-image-preview', modalities: ['image', 'text'] },
};

const cfg = MODELS[values.model];
if (!cfg) {
  console.error(`Unknown model "${values.model}". Use "flux" or "nb2".`);
  process.exit(1);
}

const VALID_ASPECTS = ['1:1', '4:5', '9:16', '16:9'];
if (!VALID_ASPECTS.includes(values.aspect)) {
  console.error(`Unknown aspect "${values.aspect}". Use one of: ${VALID_ASPECTS.join(', ')}`);
  process.exit(1);
}

async function callOpenRouter(attempt = 1) {
  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'HTTP-Referer': 'https://sonetel.com',
      'X-Title': 'Sonetel Ad Images',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: cfg.id,
      messages: [{ role: 'user', content: values.prompt }],
      modalities: cfg.modalities,
      image_config: { aspect_ratio: values.aspect },
    }),
  });

  const transient = res.status === 429 || res.status >= 500;
  if (transient && attempt <= 3) {
    const delay = 2000 * 2 ** (attempt - 1);
    console.error(`OpenRouter ${res.status}. Retrying in ${delay}ms (retry ${attempt}/3)…`);
    await new Promise((r) => setTimeout(r, delay));
    return callOpenRouter(attempt + 1);
  }

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`OpenRouter ${res.status}: ${body.slice(0, 500)}`);
  }

  return res.json();
}

const data = await callOpenRouter();
const images = data.choices?.[0]?.message?.images;
if (!images?.length) {
  console.error('No image in OpenRouter response. First 500 chars of payload:');
  console.error(JSON.stringify(data).slice(0, 500));
  process.exit(1);
}

const dataUrl = images[0]?.image_url?.url;
if (!dataUrl) {
  console.error('Image entry has an unexpected shape. First entry:');
  console.error(JSON.stringify(images[0]).slice(0, 300));
  process.exit(1);
}
const b64 = dataUrl.replace(/^data:image\/\w+;base64,/, '');
const png = Buffer.from(b64, 'base64');
const webp = await sharp(png).webp({ quality: 85 }).toBuffer();

await mkdir(dirname(values.output), { recursive: true });
await writeFile(values.output, webp);

console.log(`Saved: ${values.output} (${(webp.length / 1024).toFixed(1)} KB, model=${values.model}, aspect=${values.aspect})`);
