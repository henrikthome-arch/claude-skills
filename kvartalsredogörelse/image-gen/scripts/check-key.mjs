#!/usr/bin/env node
const key = process.env.OPENROUTER_API_KEY;
if (!key) {
  console.log('NO_KEY');
  process.exit(1);
}

try {
  const res = await fetch('https://openrouter.ai/api/v1/auth/key', {
    headers: { Authorization: `Bearer ${key}` },
  });
  if (res.ok) {
    console.log('OK');
    process.exit(0);
  }
  console.log(`FAIL ${res.status}`);
  process.exit(1);
} catch (err) {
  console.log(`ERROR ${err.message}`);
  process.exit(1);
}
