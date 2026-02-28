import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js";

async function apiLogin(username, password) {
  const res = await fetch("/api/v1/auth/login", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (res.status === 204) return;
  if (res.status === 401) throw new Error("Invalid username or password.");
  throw new Error(`Login failed (${res.status}).`);
}

async function apiLogout() {
  const res = await fetch("/api/v1/auth/logout", {
    method: "POST",
    credentials: "include",
  });

  if (!res.ok && res.status !== 204) {
    throw new Error(`Logout failed (${res.status}).`);
  }
}

async function apiCheckSession() {
  // Requires backend endpoint: GET /api/v1/auth/session
  const res = await fetch("/api/v1/auth/session", {
    method: "GET",
    credentials: "include",
  });

  if (res.status === 200) return true;
  if (res.status === 401) return false;
  // Endpoint not present yet -> default unauthenticated
  if (res.status === 404) return false;

  return false;
}

createApp({
  data() {
    return {
      viewState: "loading", // loading | unauthenticated | authenticated
      isSubmitting: false,
      errorMessage: "",
      form: {
        username: "",
        password: "",
      },
    };
  },
  methods: {
    clearError() {
      this.errorMessage = "";
    },

    async checkSession() {
      this.viewState = "loading";
      const authenticated = await apiCheckSession();
      this.viewState = authenticated ? "authenticated" : "unauthenticated";
    },

    async submitLogin() {
      this.clearError();
      this.isSubmitting = true;
      try {
        await apiLogin(this.form.username, this.form.password);
        this.form.password = "";
        this.viewState = "authenticated";
      } catch (err) {
        this.errorMessage = err instanceof Error ? err.message : "Login failed.";
      } finally {
        this.isSubmitting = false;
      }
    },

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
  async mounted() {
    await this.checkSession();
  },
}).mount("#app");