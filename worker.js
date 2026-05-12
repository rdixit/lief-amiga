// Cloudflare Worker — OpenAI API proxy for LiefAAC
// Deploy via: Workers & Pages → Create → Start with Hello World!
// Set OPENAI_API_KEY as a Secret in Settings → Variables and Secrets.

const ALLOWED_ORIGINS = [
  'https://rdixit.github.io',
  'http://localhost:8000',
  'http://127.0.0.1:8000',
];

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';

    if (!ALLOWED_ORIGINS.includes(origin)) {
      return new Response('Forbidden', { status: 403 });
    }

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': origin,
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    const { pathname } = new URL(request.url);
    const openAIUrl = `https://api.openai.com${pathname}`;

    const body = await request.arrayBuffer();
    const upstream = await fetch(openAIUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
        'Content-Type': request.headers.get('Content-Type'),
      },
      body,
    });

    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        'Content-Type': upstream.headers.get('Content-Type'),
        'Access-Control-Allow-Origin': origin,
      },
    });
  },
};
