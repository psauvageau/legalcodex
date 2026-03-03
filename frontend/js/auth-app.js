import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js";
// Side-effect import to ensure chat API module is loaded early.
// This keeps module wiring in place while chat methods are added incrementally.
import "./chat-api.js";

/**
 * POST /auth/login
 * Keep this helper thin and deterministic so UI logic can map status codes
 * to user-facing errors in one place.
 */
async function apiLogin(username, password) {
  const res = await fetch("/api/v1/auth/login", {
    method: "POST",
    credentials: "include", // Required for cookie-based session auth.
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  // Backend returns 204 on success (no body expected).
  if (res.status === 204) return;
  // Expected auth failure path.
  if (res.status === 401) throw new Error("Invalid username or password.");
  // Any other status is treated as unexpected and surfaced for debugging.
  throw new Error(`Login failed (${res.status}).`);
}

/**
 * POST /auth/logout
 * Best-effort invalidation of server cookie session.
 */
async function apiLogout() {
  const res = await fetch("/api/v1/auth/logout", {
    method: "POST",
    credentials: "include",
  });

  // Accept 204 explicitly; reject other non-OK responses for diagnostics.
  if (!res.ok && res.status !== 204) {
    throw new Error(`Logout failed (${res.status}).`);
  }
}

/**
 * GET /auth/session
 * Returns boolean only, so the calling code can stay simple.
 * Unknown responses intentionally fail closed (unauthenticated).
 */
async function apiCheckSession() {
  const res = await fetch("/api/v1/auth/session", {
    method: "GET",
    credentials: "include",
  });

  if (res.status === 200) return true;
  if (res.status === 401) return false;
  // Endpoint might not exist in some environments.
  if (res.status === 404) return false;

  // Defensive default: do not assume authenticated on ambiguous failures.
  return false;
}

createApp({
  /**
   * Vue reactive state.
   * Anything returned here is tracked and can be bound in template.
   * Keep state flat and explicit to simplify debugging in Vue devtools.
   */
  data() {
    return {
      // View gate for template branches.
      viewState: "loading", // loading | unauthenticated | authenticated

      // Shared submission lock for login/logout buttons.
      isSubmitting: false,

      // Auth form/user feedback state.
      errorMessage: "",
      form: {
        username: "",
        password: "",
      },

      // Chat state scaffold (wired in later tasks).
      sessions: [],
      currentSessionId: null,
      messages: [],
      draft: "",
      isSending: false,
      chatError: "",
      sidebarOpen: true,
    };
  },

  methods: {
    /**
     * Clears only auth error text.
     * Keep this narrowly scoped to avoid hiding unrelated chat errors.
     */
    clearError() {
      this.errorMessage = "";
    },

    /**
     * Initial auth probe and state transition.
     * Centralizing this flow avoids duplicated login-check logic.
     */
    async checkSession() {
      this.viewState = "loading";
      const authenticated = await apiCheckSession();
      this.viewState = authenticated ? "authenticated" : "unauthenticated";
    },

    /**
     * Login submit handler.
     * Uses try/finally to guarantee UI unlock even if network errors occur.
     */
    async submitLogin() {
      this.clearError();
      this.isSubmitting = true;
      try {
        await apiLogin(this.form.username, this.form.password);

        // Minimize sensitive data retention in reactive memory.
        this.form.password = "";
        this.viewState = "authenticated";
      } catch (err) {
        this.errorMessage = err instanceof Error ? err.message : "Login failed.";
      } finally {
        this.isSubmitting = false;
      }
    },

    /**
     * Logout handler.
     * UI always returns to unauthenticated in finally to prevent stale
     * authenticated rendering if logout fails server-side.
     */
    async submitLogout() {
      this.isSubmitting = true;
      this.clearError();
      try {
        await apiLogout();
      } finally {
        this.isSubmitting = false;
        this.viewState = "unauthenticated";
      }
    },
  },

  /**
   * Vue lifecycle hook: runs once after initial render.
   * Used to bootstrap auth state before user interaction.
   */
  async mounted() {
    await this.checkSession();
  },
}).mount("#app");