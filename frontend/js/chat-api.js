function notImplemented(name) {
  throw new Error(`${name} is not implemented yet.`);
}

export async function apiListSessions() {
  notImplemented("apiListSessions");
}

export async function apiCreateSession(_options = {}) {
  notImplemented("apiCreateSession");
}

export async function apiGetContext(_sessionId) {
  notImplemented("apiGetContext");
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
