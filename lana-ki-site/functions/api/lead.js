export async function onRequestPost(context) {
  try {
    const data = await context.request.json();
    const lead = {
      id: crypto.randomUUID(),
      created_at: new Date().toISOString(),
      ip: context.request.headers.get("CF-Connecting-IP") || "",
      ...data
    };
    // Hier wird der Lead verarbeitet (später an KV oder E-Mail)
    return new Response(JSON.stringify({ ok: true, lead_id: lead.id }), {
      status: 200, headers: { "content-type": "application/json" }
    });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "server_error" }), { status: 500 });
  }
}
