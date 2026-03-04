const LEVELS = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
  silent: 99,
};

function normalizeLevel(level) {
  if (!level) return "info";
  const value = String(level).toLowerCase();
  return Object.prototype.hasOwnProperty.call(LEVELS, value) ? value : "info";
}

function resolveLevel() {
  const fromStorage = globalThis.localStorage?.getItem("lc:log-level");
  const fromWindow = globalThis.LC_LOG_LEVEL;
  const fromQuery = new URLSearchParams(globalThis.location?.search ?? "").get("log");
  return normalizeLevel(fromQuery || fromStorage || fromWindow || "info");
}

function shouldLog(targetLevel, currentLevel) {
  return LEVELS[targetLevel] >= LEVELS[currentLevel];
}

function makeMethod(targetLevel, scope, getLevel) {
  return (...args) => {
    const currentLevel = getLevel();
    if (!shouldLog(targetLevel, currentLevel)) {
      return;
    }

    const prefix = `[${scope}]`;
    if (targetLevel === "debug") {
      console.debug(prefix, ...args);
      return;
    }
    if (targetLevel === "info") {
      console.info(prefix, ...args);
      return;
    }
    if (targetLevel === "warn") {
      console.warn(prefix, ...args);
      return;
    }
    console.error(prefix, ...args);
  };
}

export function createLogger(scope) {
  let level = resolveLevel();

  const getLevel = () => level;

  return {
    debug: makeMethod("debug", scope, getLevel),
    info: makeMethod("info", scope, getLevel),
    warn: makeMethod("warn", scope, getLevel),
    error: makeMethod("error", scope, getLevel),
    setLevel(nextLevel) {
      level = normalizeLevel(nextLevel);
      try {
        globalThis.localStorage?.setItem("lc:log-level", level);
      } catch {
        // ignore localStorage failures
      }
    },
    getLevel,
  };
}
