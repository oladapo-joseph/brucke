async function req(method, url, body) {
  const r = await fetch(url, { method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) {
    let msg = r.statusText;
    try { msg = (await r.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return r.json();
}
export const api = {
  get: (u) => req("GET", u),
  post: (u, b) => req("POST", u, b || {}),
  put: (u, b) => req("PUT", u, b),
};
