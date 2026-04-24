export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    const corsHeaders = {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, POST, OPTIONS",
      "access-control-allow-headers": "Content-Type, x-admin-key",
      "content-type": "application/json; charset=UTF-8"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (request.method === "GET" && url.pathname === "/") {
      return new Response(JSON.stringify({
        ok: true,
        service: "lana-api",
        status: "online"
      }), {
        status: 200,
        headers: corsHeaders
      });
    }

    if (request.method === "GET" && url.pathname === "/health") {
      return new Response(JSON.stringify({
        ok: true,
        status: "healthy",
        time: new Date().toISOString()
      }), {
        status: 200,
        headers: corsHeaders
      });
    }

    if (request.method === "GET" && url.pathname === "/leads") {
      const auth = request.headers.get("x-admin-key") || "";
      if (!env.ADMIN_KEY || auth !== env.ADMIN_KEY) {
        return new Response(JSON.stringify({
          ok: false,
          error: "unauthorized"
        }), {
          status: 401,
          headers: corsHeaders
        });
      }

      const list = await env.LANA_LEADS.list({ prefix: "lead:" });
      const items = [];

      for (const key of list.keys) {
        const raw = await env.LANA_LEADS.get(key.name);
        if (raw) items.push(JSON.parse(raw));
      }

      return new Response(JSON.stringify({
        ok: true,
        count: items.length,
        items
      }), {
        status: 200,
        headers: corsHeaders
      });
    }

    if (request.method === "POST" && url.pathname === "/lead") {
      try {
        const data = await request.json();
        const required = ["name", "email", "bedarf", "nachricht"];

        for (const key of required) {
          if (!data[key] || String(data[key]).trim() === "") {
            return new Response(JSON.stringify({
              ok: false,
              error: "missing_field",
              field: key
            }), {
              status: 400,
              headers: corsHeaders
            });
          }
        }

        const id = crypto.randomUUID();
        const lead = {
          id,
          received_at: new Date().toISOString(),
          ...data
        };

        await env.LANA_LEADS.put(`lead:${id}`, JSON.stringify(lead));

        return new Response(JSON.stringify({
          ok: true,
          id,
          received_at: lead.received_at
        }), {
          status: 200,
          headers: corsHeaders
        });
      } catch (e) {
        return new Response(JSON.stringify({
          ok: false,
          error: "server_error",
          detail: String(e)
        }), {
          status: 500,
          headers: corsHeaders
        });
      }
    }

    return new Response(JSON.stringify({
      ok: false,
      error: "not_found"
    }), {
      status: 404,
      headers: corsHeaders
    });
  }
}
