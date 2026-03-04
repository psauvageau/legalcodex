import { createApp } from "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js";
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import DOMPurify from "https://cdn.jsdelivr.net/npm/dompurify@3.2.6/+esm";
import { createLogger } from "./logger.js";
import {
  apiCloseSession,
  apiCreateSession,
  apiGetContext,
  apiListSessions,
  apiResetContext,
  apiSendMessage,
} from "./chat-api.js";

marked.setOptions({ gfm: true, breaks: true });
const logger = createLogger("chat-ui");

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
      chatToast: "",
      toastTimerId: null,
      sidebarOpen: true,
    };
  },

  methods: {
    isNarrowViewport() {
      return window.matchMedia("(max-width: 860px)").matches;
    },

    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },

    closeSidebar() {
      this.sidebarOpen = false;
    },

    closeSidebarOnMobile() {
      if (this.isNarrowViewport()) {
        this.closeSidebar();
      }
    },

    onGlobalKeydown(event) {
      if (event.key === "Escape" && this.sidebarOpen && this.isNarrowViewport()) {
        this.closeSidebar();
      }
    },

    setChatError(message) {
      this.chatError = message;
      this.showToast(message);
    },

    showToast(message) {
      this.chatToast = message;
      if (this.toastTimerId) {
        clearTimeout(this.toastTimerId);
      }

      this.toastTimerId = setTimeout(() => {
        this.chatToast = "";
        this.toastTimerId = null;
      }, 2500);
    },

    formatRole(role) {
      if (role === "assistant") return "Assistant";
      if (role === "system") return "System";
      return "User";
    },

    formatTimestamp(timestampMs) {
      return new Date(timestampMs).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    },

    /**
     * Render a raw chat message as safe HTML for display in `v-html`.
     *
     * Intention:
     * - Convert Markdown authored by user/assistant into presentable HTML.
     * - Sanitize generated HTML so untrusted content cannot inject scripts.
     * - Add a copy-action wrapper around fenced code blocks for UX consistency.
     *
     * Preconditions:
     * - `content` is expected to be a string (or null/undefined, treated as empty).
     * - `marked` is configured and available.
     * - `DOMPurify` is available and should sanitize all generated markup.
     *
     * Postconditions (returned document shape):
     * - Returns a sanitized HTML string safe to bind with `v-html`.
     * - Fenced code blocks are wrapped as:
     *   `<div class="chat-code-block"><button class="chat-copy-code">Copy</button><pre><code>...</code></pre></div>`
     * - Non-code Markdown remains standard sanitized HTML (`p`, `ul`, `em`, etc.).
     */
    renderMarkdown(content) {
      const rawHtml = marked.parse(content ?? "");
      const sanitizedHtml = DOMPurify.sanitize(rawHtml);
      const template = document.createElement("template");
      template.innerHTML = sanitizedHtml;

      // Select every <code> element that is a direct child of <pre>,
      // i.e. fenced code blocks rendered by Markdown as <pre><code>...</code></pre>.
      const preCodeBlocks = template.content.querySelectorAll("pre > code");
      preCodeBlocks.forEach((codeElement) => {
        const preElement = codeElement.parentElement;
        if (!preElement) {
          logger.debug("Skipping code block without <pre> parent", { codeElement });
          return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "chat-code-block";

        const copyButton = document.createElement("button");
        copyButton.type = "button";
        copyButton.className = "chat-copy-code";
        copyButton.textContent = "Copy";

        preElement.replaceWith(wrapper);
        wrapper.append(copyButton, preElement);
      });

      const withCopyButtons = template.innerHTML;

      logger.debug("Rendered markdown", {
        hasCodeFence: /```/.test(content ?? ""),
        hasPreTag: preCodeBlocks.length > 0,
        hasCopyButton: template.content.querySelectorAll(".chat-copy-code").length > 0,
      });

      return withCopyButtons;
    },

    /**
     * Ensure rendered message HTML contains copy controls for fenced code blocks.
     *
     * Intention:
     * - Post-process already-rendered chat message DOM and wrap each `<pre>`
     *   inside `.chat-message-content` with a `.chat-code-block` container.
     * - Inject a `.chat-copy-code` button so users can copy block content.
     *
     * Preconditions:
     * - Vue has rendered message content (`v-html`) into the document.
     * - This method is called after message list updates (hence `await this.$nextTick()`).
     *
     * Postconditions:
     * - Every eligible `<pre>` is wrapped once (idempotent behavior).
     * - Existing wrapped blocks are left untouched.
     */
    async decorateCodeBlocks() {
      await this.$nextTick();

      const root = this.$el;
      if (!(root instanceof HTMLElement)) {
        return;
      }

      const codeBlocks = root.querySelectorAll(".chat-message-content pre");
      logger.debug("Decorating code blocks", { preCount: codeBlocks.length });
      codeBlocks.forEach((preElement) => {
        if (!(preElement instanceof HTMLElement)) {
          return;
        }

        if (preElement.parentElement?.classList.contains("chat-code-block")) {
          return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "chat-code-block";

        const copyButton = document.createElement("button");
        copyButton.type = "button";
        copyButton.className = "chat-copy-code";
        copyButton.textContent = "Copy";

        preElement.replaceWith(wrapper);
        wrapper.append(copyButton, preElement);
      });

      logger.debug("Code block decoration done", {
        wrapperCount: root.querySelectorAll(".chat-code-block").length,
        copyButtonCount: root.querySelectorAll(".chat-copy-code").length,
      });
    },

    createMessage(role, content, timestampMs = Date.now()) {
      return {
        id: `${timestampMs}-${Math.random().toString(36).slice(2)}`,
        role,
        content,
        rendered: this.renderMarkdown(content),
        timestampMs,
      };
    },

    /**
     * Handle delegated clicks inside rendered message HTML.
     *
     * Intention:
     * - Intercept clicks on `.chat-copy-code` buttons embedded in message content.
     * - Copy the associated `<code>` block text to the clipboard.
     *
     * Preconditions:
     * - `event` originates from `.chat-message-content`.
     * - Copy buttons follow the structure created by markdown decoration
     *   (`.chat-copy-code` within `.chat-code-block` containing `<code>`).
     *
     * Postconditions:
     * - On success: code text is copied and button text briefly changes to `Copied!`.
     * - On failure: no exception escapes; a warning is logged and a toast is shown.
     */
    async onMessageContentClick(event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) {
        return;
      }

      const button = target.closest(".chat-copy-code");
      if (!(button instanceof HTMLButtonElement)) {
        return;
      }

      const codeBlock = button.parentElement?.querySelector("code");
      if (!(codeBlock instanceof HTMLElement)) {
        return;
      }

      try {
        await navigator.clipboard.writeText(codeBlock.innerText);
        logger.info("Copied code block to clipboard");
        const originalText = button.textContent;
        button.textContent = "Copied!";
        setTimeout(() => {
          button.textContent = originalText;
        }, 900);
      } catch {
        logger.warn("Clipboard copy failed");
        this.showToast("Copy failed.");
      }
    },

    resetChatState() {
      this.sessions = [];
      this.currentSessionId = null;
      this.messages = [];
      this.draft = "";
      this.isSending = false;
      this.chatError = "";
      this.chatToast = "";
      if (this.toastTimerId) {
        clearTimeout(this.toastTimerId);
        this.toastTimerId = null;
      }
    },

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

      if (authenticated) {
        await this.loadSessions();
      } else {
        this.resetChatState();
      }
    },

    async loadSessions() {
      this.chatError = "";

      try {
        const sessions = await apiListSessions();
        this.sessions = Array.isArray(sessions) ? sessions : [];

        if (this.sessions.length === 0) {
          const createdSession = await apiCreateSession({});
          this.sessions = [createdSession];
          await this.openSession(createdSession.session_id);
          return;
        }

        await this.openSession(this.sessions[0].session_id);
      } catch (err) {
        this.setChatError(err instanceof Error ? err.message : "Unable to load sessions.");
        this.sessions = [];
        this.currentSessionId = null;
      }
    },

    async createSession() {
      this.chatError = "";

      try {
        const createdSession = await apiCreateSession({});
        this.sessions = [...this.sessions, createdSession];
        await this.openSession(createdSession.session_id);
      } catch (err) {
        this.setChatError(err instanceof Error ? err.message : "Unable to create session.");
      }
    },

    async resetSession() {
      if (!this.currentSessionId || this.isSending) {
        return;
      }

      this.chatError = "";

      try {
        await apiResetContext(this.currentSessionId);
        this.messages = [];
      } catch (err) {
        this.setChatError(err instanceof Error ? err.message : "Unable to reset session.");
      }
    },

    async closeSession() {
      if (!this.currentSessionId || this.isSending) {
        return;
      }

      this.chatError = "";
      const closingSessionId = this.currentSessionId;

      try {
        await apiCloseSession(closingSessionId);

        const remainingSessions = this.sessions.filter((s) => s.session_id !== closingSessionId);
        this.sessions = remainingSessions;
        this.messages = [];
        this.currentSessionId = null;

        if (remainingSessions.length > 0) {
          await this.openSession(remainingSessions[0].session_id);
          return;
        }

        const createdSession = await apiCreateSession({});
        this.sessions = [createdSession];
        await this.openSession(createdSession.session_id);
      } catch (err) {
        this.setChatError(err instanceof Error ? err.message : "Unable to close session.");
      }
    },

    async scrollMessagesToBottom() {
      await this.$nextTick();
      const container = this.$refs.messagesContainer;
      if (!container || typeof container.scrollHeight !== "number") {
        return;
      }

      container.scrollTop = container.scrollHeight;
    },

    isNearMessagesBottom() {
      const container = this.$refs.messagesContainer;
      if (!container) {
        return true;
      }

      return container.scrollTop + container.clientHeight >= container.scrollHeight - 40;
    },

    async openSession(sessionId) {
      this.chatError = "";
      this.currentSessionId = sessionId;
      this.messages = [];

      try {
        const context = await apiGetContext(sessionId);
        const history = context.history;
        this.messages = history
          .filter((entry) => typeof entry?.content === "string" && typeof entry?.role === "string")
          .map((entry, index) => this.createMessage(entry.role, entry.content, Date.now() + index));
        await this.decorateCodeBlocks();
        await this.scrollMessagesToBottom();
        this.closeSidebarOnMobile();
      } catch (err) {
        this.setChatError(err instanceof Error ? err.message : "Unable to open session.");
        this.messages = [];
      }
    },

    async sendMessage() {
      const message = this.draft.trim();
      if (!message || this.isSending) {
        return;
      }

      if (!this.currentSessionId) {
        this.setChatError("No active session selected.");
        return;
      }

      this.chatError = "";
      this.isSending = true;

      this.messages = [...this.messages, this.createMessage("user", message)];
      this.draft = "";
      await this.decorateCodeBlocks();

      try {
        const response = await apiSendMessage(this.currentSessionId, message);
        const shouldAutoScroll = this.isNearMessagesBottom();
        this.messages = [...this.messages, this.createMessage("assistant", response.response)];
        await this.decorateCodeBlocks();

        if (shouldAutoScroll) {
          await this.scrollMessagesToBottom();
        }
      } catch (err) {
        this.setChatError(err instanceof Error ? err.message : "Unable to send message.");
      } finally {
        this.isSending = false;
      }
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
        await this.loadSessions();
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
        this.resetChatState();
        this.viewState = "unauthenticated";
      }
    },
  },

  /**
   * Vue lifecycle hook: runs once after initial render.
   * Used to bootstrap auth state before user interaction.
   */
  async mounted() {
    window.addEventListener("keydown", this.onGlobalKeydown);
    await this.checkSession();
  },

  unmounted() {
    window.removeEventListener("keydown", this.onGlobalKeydown);
  },
}).mount("#app");