# API Key Security: Removing the Hardcoded Key

**Status:** Proposed  
**Author:** Mike Pesavento  
**Audience:** Rohan Dixit (repo owner), core team

---

## The Problem

`app.js` currently contains a hardcoded OpenAI API key, base64-encoded as a minor obfuscation:

```js
// app.js line 339–341
const _k = atob('c2stcHJvai1WbH...');
let apiKey = _k;
```

Base64 is not encryption — anyone who opens the browser DevTools console can run `atob(...)` and retrieve the raw key in seconds. Because the app is hosted on GitHub Pages (a public static file server), the key is effectively public.

The key is used for two features:
1. **Sentence prediction** — `POST https://api.openai.com/v1/chat/completions` (model: `gpt-4o-mini`)
2. **Text-to-speech** — `POST https://api.openai.com/v1/audio/speech` (model: `tts-1`, voice: `nova`)

Both calls fall back gracefully to local/browser alternatives when the key is absent, so the app remains functional without the key.

### Why this matters now

- USC IRB review is approaching. Reviewers will likely ask about data flows and API usage. A compromised or uncontrolled key is a liability.
- The app is linked publicly at `https://rdixit.github.io/lief-amiga/` — any visitor can extract and use the key.
- The current key should be considered **already compromised** and revoked at the OpenAI dashboard regardless of what path is chosen below.

---

## Why "just use GitHub Secrets" doesn't work here

GitHub Actions secrets are available at build time, not runtime. GitHub Pages serves static files — there is no server executing code. Even if the key were injected into the JS at build time via a secret, it would still end up in the deployed `.js` file in plaintext, readable by anyone. **There is no way to hide a secret in a pure client-side app.**

The key must live somewhere that is not the browser.

---

## Recommended Solution: Cloudflare Workers Proxy

Deploy a small serverless proxy function on Cloudflare Workers. The frontend calls the proxy instead of OpenAI directly. The OpenAI key lives only in the Cloudflare environment — it is never sent to the browser.

```
Browser (GitHub Pages)  →  Cloudflare Worker  →  OpenAI API
                              (holds the key)
```

### Why Cloudflare Workers

- **Free tier** covers ~100,000 requests/day — more than sufficient for a research prototype
- No credit card required to start
- Deploys independently of the GitHub repo — no owner permissions needed on `rdixit/lief-amiga`
- Supports CORS origin whitelisting, so only `rdixit.github.io` can call the proxy
- Takes ~20 minutes to set up

### The proxy (one file)

```js
// worker.js — deployed to Cloudflare, not committed to the repo
export default {
  async fetch(request, env) {
    // Only allow the GitHub Pages origin
    const origin = request.headers.get('Origin') || '';
    if (origin !== 'https://rdixit.github.io') {
      return new Response('Forbidden', { status: 403 });
    }

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': 'https://rdixit.github.io',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    const { pathname } = new URL(request.url);
    const openAIUrl = `https://api.openai.com${pathname}`;

    const body = await request.arrayBuffer();
    const response = await fetch(openAIUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
        'Content-Type': request.headers.get('Content-Type'),
      },
      body,
    });

    return new Response(response.body, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type'),
        'Access-Control-Allow-Origin': 'https://rdixit.github.io',
      },
    });
  },
};
```

The `OPENAI_API_KEY` environment variable is set in the Cloudflare dashboard — it is never in the code.

### Changes to `app.js`

Three small changes:

1. **Remove the hardcoded key entirely** (lines 338–341):
   ```js
   // DELETE these lines:
   // Demo key (obfuscated)
   // NOTE(mjp): use env var for this, anyone can still decode this key
   const _k = atob('c2stcHJvai1WbH...');
   let apiKey = _k;
   ```
   Replace with:
   ```js
   const PROXY_BASE_URL = 'https://lief-amiga-proxy.YOUR_SUBDOMAIN.workers.dev';
   ```

2. **Update the prediction fetch URL** (line 780):
   ```js
   // Before:
   const response = await fetch('https://api.openai.com/v1/chat/completions', {
     headers: { 'Authorization': `Bearer ${apiKey}`, ... }
   
   // After:
   const response = await fetch(`${PROXY_BASE_URL}/v1/chat/completions`, {
     // No Authorization header — the proxy adds it
   ```

3. **Update the TTS fetch URL** (line 902):
   ```js
   // Before:
   const response = await fetch('https://api.openai.com/v1/audio/speech', {
     headers: { 'Authorization': `Bearer ${apiKey}`, ... }
   
   // After:
   const response = await fetch(`${PROXY_BASE_URL}/v1/audio/speech`, {
     // No Authorization header
   ```

The `if (apiKey)` guards can be removed or replaced with a simple `if (PROXY_BASE_URL)` check — the logic is identical since both features already fall back gracefully.

---

## Alternative: User-provided key (no infrastructure)

If standing up a Cloudflare Worker is not feasible right now, the next-safest option is to remove the hardcoded key and require users to paste their own OpenAI key into a settings UI. The key would be stored in `localStorage` (never in code).

**Tradeoffs:**
- Immediately removes the key from the codebase — good
- Bad UX for the intended users (AAC users, therapists) — they shouldn't need an OpenAI account
- `localStorage` is accessible to any JS on the page, so it is not truly secure — acceptable for a dev prototype, not acceptable for a clinical tool

This approach is reasonable as a short-term stopgap while the proxy is being set up.

---

## Recommended action sequence

1. **Immediately:** Revoke the current key in the [OpenAI dashboard](https://platform.openai.com/api-keys). It is already public.
2. **Short-term (owner action):** Create a fresh OpenAI API key scoped to `gpt-4o-mini` and `tts-1` only, with a spend limit set.
3. **20-minute setup:** Deploy the Cloudflare Worker above with the new key set as an environment variable. No changes to the GitHub repo needed yet.
4. **PR to the repo:** Update `app.js` to point to the proxy URL and remove the `apiKey` variable. This is a small diff (~10 lines changed).

Steps 3 and 4 are independent — the worker can be deployed before the PR is merged and tested against the live site.

---

## Notes on the longer-term path

The `app.js` code already contains a comment flagging the intended direction:

```js
// NOTE(mjp): replace with local SLM in later phases
```

Running a small language model locally (e.g., via WebLLM or a Transformers.js model) would eliminate the OpenAI dependency entirely — no API key, no proxy, no cost per request, and no data leaving the device. This is the right end state for a clinical AAC tool handling sensitive communication. The proxy solution described here is the correct bridge until that work is prioritized.
