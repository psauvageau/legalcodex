function notImplemented(name) {
  throw new Error(`${name} is not implemented yet.`);
}

export async function apiListSessions() {
  const res = await fetch("/api/v1/chat/sessions", {
    method: "GET",
    credentials: "include",
  });

  if (res.status === 200) {
    return await res.json();
  }

  let detail = "Failed to list chat sessions.";
  try {
    const payload = await res.json();
    if (payload && typeof payload.detail === "string") {
      detail = payload.detail;
    }
  } catch {
    // Ignore parse errors and keep fallback message.
  }

  throw new Error(detail);
}

export async function apiCreateSession(options = {}) {
  const res = await fetch("/api/v1/chat/sessions", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  });

  if (res.status === 200 || res.status === 201) {
    return await res.json();
  }

  let detail = "Failed to create chat session.";
  try {
    const payload = await res.json();
    if (payload && typeof payload.detail === "string") {
      detail = payload.detail;
    }
  } catch {
    // Ignore parse errors and keep fallback message.
  }

  throw new Error(detail);
}

export async function apiGetContext(_sessionId) {
  const res = await fetch(`/api/v1/chat/sessions/${encodeURIComponent(_sessionId)}/context`, {
    method: "GET",
    credentials: "include",
  });

  if (res.status === 200) {
    return await res.json();
  }

  let detail = "Failed to load chat context.";
  try {
    const payload = await res.json();
    if (payload && typeof payload.detail === "string") {
      detail = payload.detail;
    }
  } catch {
    // Ignore parse errors and keep fallback message.
  }

  throw new Error(detail);
}

export async function apiSendMessage(_sessionId, _message) {
  notImplemented("apiSendMessage");
}

export async function apiResetContext(_sessionId) {
  notImplemented("apiResetContext");
}

export async function apiCloseSession(_sessionId) {
  notImplemented("apiCloseSession");
}
