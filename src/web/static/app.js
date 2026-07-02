import { initDailiesRoom, attemptAsyncGeneration } from "./modules/dailiesRoom.js";
import { initCameraCards, renderCameraCards, syncCameraCards } from "./modules/cameraCards.js";
import {
  initMovementVocabulary,
  renderMovementVocabulary,
  syncMovementVocabulary,
} from "./modules/movementVocabulary.js";
import {
  initLightTable,
  openLightTable,
  closeLightTable,
  maybeAutoOpenLightTable,
} from "./modules/lightTable.js";

const DEFAULT_SETTINGS = {
  accessibility: {
    reducedMotion: false,
    highContrastFocus: true,
    announceStatusChanges: true,
  },
  preferences: {
    autoFavoriteWinner: false,
    autoOpenCompare: true,
    defaultPreset: "cinematic-balanced",
    defaultAspectRatio: "16:9",
    defaultDuration: 6,
    defaultVariants: 3,
  },
  behavior: {
    autoSave: true,
    autoSaveDelayMs: 700,
    renderQuality: "balanced",
    parallelPreviews: 2,
    confirmBeforeClear: true,
  },
  theme: {
    mode: "darkroom",
    accent: "amber",
    grain: 0.35,
    contrast: 1,
    density: "comfortable",
  },
  developer: {
    showRawPayload: false,
    enableDebugOverlay: false,
    enableKeyboardTimeline: true,
    gestureNavigation: true,
  },
};

const GENERATION_TIMEOUT_MS = 180000;

const PROVIDER_META = {
  sora: { label: "Sora", costPerSecond: 0.3, estSeconds: 90, audio: true, maxDuration: 20, deprecated: true },
  veo: { label: "Veo", costPerSecond: 0.35, estSeconds: 40, audio: true, maxDuration: 8 },
  runway: { label: "Runway", costPerSecond: 0.25, estSeconds: 50, audio: false, maxDuration: 10 },
  kling: { label: "Kling", costPerSecond: 0.15, estSeconds: 60, audio: true, maxDuration: 10 },
  luma: { label: "Luma", costPerSecond: 0.32, estSeconds: 55, audio: false, maxDuration: 10 },
  pika: { label: "Pika", costPerSecond: 0.2, estSeconds: 45, audio: false, maxDuration: 10 },
  wan: { label: "Wan", costPerSecond: 0.1, estSeconds: 70, audio: false, maxDuration: 10 },
  flux: { label: "Flux", costPerSecond: 0.05, estSeconds: 20, audio: false, maxDuration: 6 },
};

const state = {
  auth: {
    googleEnabled: false,
    googleClientId: null,
    authenticated: false,
    user: null,
  },
  sessionReady: false,
  currentImageFile: null,
  currentImageUrl: null,
  currentImageName: null,
  currentRunId: null,
  selectedForCompare: new Set(),
  pendingRun: null,
  activeGeneration: null,
  runs: [],
  providerOptions: [],
  presets: [],
  settings: structuredClone(DEFAULT_SETTINGS),
  settingsVersion: 1,
  settingsUpdatedAt: null,
  settingsSaveTimer: null,
  swipe: {
    startX: 0,
    startY: 0,
  },
  contextMenu: null,
};

const refs = {
  authView: document.getElementById("authView"),
  authStatus: document.getElementById("authStatus"),
  googleButtonHost: document.getElementById("googleButtonHost"),
  continueGuestButton: document.getElementById("continueGuestButton"),
  appHeader: document.getElementById("appHeader"),
  appMain: document.getElementById("appMain"),
  userIdentity: document.getElementById("userIdentity"),
  logoutButton: document.getElementById("logoutButton"),

  navButtons: document.querySelectorAll(".nav-btn"),
  views: document.querySelectorAll(".view"),

  dropZone: document.getElementById("dropZone"),
  fileInput: document.getElementById("fileInput"),
  sourcePreview: document.getElementById("sourcePreview"),
  dropZoneText: document.getElementById("dropZoneText"),
  intentInput: document.getElementById("intentInput"),
  intentChips: document.querySelectorAll(".chip"),
  generateButton: document.getElementById("generateButton"),
  costPreview: document.getElementById("costPreview"),
  sampleFrameButton: document.getElementById("sampleFrameButton"),

  providerSelect: document.getElementById("providerSelect"),
  providerCards: document.getElementById("providerCards"),
  presetSelect: document.getElementById("presetSelect"),
  durationInput: document.getElementById("durationInput"),
  variantCountInput: document.getElementById("variantCountInput"),
  aspectSelect: document.getElementById("aspectSelect"),
  motionInput: document.getElementById("motionInput"),
  movementSegments: document.getElementById("movementSegments"),
  qualitySelect: document.getElementById("qualitySelect"),
  negativeIntentInput: document.getElementById("negativeIntentInput"),
  toggleAdvancedButton: document.getElementById("toggleAdvancedButton"),
  advancedPanel: document.getElementById("advancedPanel"),

  resultGrid: document.getElementById("resultGrid"),
  openCompareButton: document.getElementById("openCompareButton"),
  comparePanel: document.getElementById("comparePanel"),
  closeCompareButton: document.getElementById("closeCompareButton"),
  compareGrid: document.getElementById("compareGrid"),
  lightTableTransport: document.getElementById("lightTableTransport"),
  runSummary: document.getElementById("runSummary"),

  timelineList: document.getElementById("timelineList"),
  clearTimelineButton: document.getElementById("clearTimelineButton"),
  historyList: document.getElementById("historyList"),
  favoritesList: document.getElementById("favoritesList"),

  presetCards: document.getElementById("presetCards"),

  syncState: document.getElementById("syncState"),
  settingsVersion: document.getElementById("settingsVersion"),
  settingsHistoryList: document.getElementById("settingsHistoryList"),

  apiKeyRows: document.getElementById("apiKeyRows"),

  reducedMotionToggle: document.getElementById("reducedMotionToggle"),
  autoFavoriteToggle: document.getElementById("autoFavoriteToggle"),
  autoOpenCompareToggle: document.getElementById("autoOpenCompareToggle"),
  announceStatusToggle: document.getElementById("announceStatusToggle"),

  autoSaveDelayInput: document.getElementById("autoSaveDelayInput"),
  parallelPreviewInput: document.getElementById("parallelPreviewInput"),
  confirmClearToggle: document.getElementById("confirmClearToggle"),

  accentSelect: document.getElementById("accentSelect"),
  grainInput: document.getElementById("grainInput"),
  contrastInput: document.getElementById("contrastInput"),
  themePreview: document.getElementById("themePreview"),

  debugOverlayToggle: document.getElementById("debugOverlayToggle"),
  rawPayloadToggle: document.getElementById("rawPayloadToggle"),
  gestureNavToggle: document.getElementById("gestureNavToggle"),

  exportDataButton: document.getElementById("exportDataButton"),
  importDataInput: document.getElementById("importDataInput"),

  toast: document.getElementById("toast"),
  statusLive: document.getElementById("statusLive"),

  settingsToggles: document.querySelectorAll(".settings-toggle"),
};

const VIEW_ORDER = ["createView", "libraryView", "presetsView", "settingsView"];

function announce(message) {
  if (refs.statusLive) {
    refs.statusLive.textContent = message;
  }
  if (state.settings.accessibility.announceStatusChanges) {
    showToast(message);
  }
}

function showToast(message) {
  refs.toast.textContent = message;
  refs.toast.classList.add("is-visible");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    refs.toast.classList.remove("is-visible");
  }, 2200);
}

async function requestJSON(url, options = {}) {
  const { timeoutMs = 12000, ...fetchOptions } = options;
  const controller = fetchOptions.signal ? null : new AbortController();
  const timeoutId = controller
    ? setTimeout(() => {
        controller.abort();
      }, timeoutMs)
    : null;

  let response;
  try {
    response = await fetch(url, {
      credentials: "same-origin",
      ...fetchOptions,
      signal: fetchOptions.signal || controller?.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(`Request timed out after ${timeoutMs}ms`);
    }
    throw new Error(`Network request failed: ${error.message}`);
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || `Request failed (${response.status})`;
    throw new Error(detail);
  }

  return payload;
}

async function bootstrapSession() {
  await requestJSON("/api/session/bootstrap");
  state.sessionReady = true;
}

async function loadAuthConfig() {
  const payload = await requestJSON("/api/auth/config");
  state.auth.googleEnabled = Boolean(payload.google_enabled);
  state.auth.googleClientId = payload.google_client_id;
}

async function loadCurrentUser() {
  const payload = await requestJSON("/api/auth/me");
  state.auth.authenticated = Boolean(payload.authenticated);
  state.auth.user = payload.user || null;
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.defer = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function initializeGoogleButton() {
  if (!state.auth.googleEnabled || !state.auth.googleClientId) {
    refs.authStatus.textContent = "Google Sign-In is unavailable in this environment.";
    return;
  }

  try {
    await loadScript("https://accounts.google.com/gsi/client");
    window.google.accounts.id.initialize({
      client_id: state.auth.googleClientId,
      callback: async (response) => {
        try {
          refs.authStatus.textContent = "Verifying film slate...";
          await requestJSON("/api/auth/google", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ credential: response.credential }),
          });
          await loadCurrentUser();
          refs.authStatus.textContent = "Authenticated. Initializing console...";
          enterAppExperience();
          await initializeRuntimeData();
        } catch (error) {
          refs.authStatus.textContent = `Authentication failed: ${error.message}`;
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
      ux_mode: "popup",
    });

    window.google.accounts.id.renderButton(refs.googleButtonHost, {
      theme: "filled_black",
      size: "large",
      shape: "pill",
      text: "signin_with",
      width: 280,
      logo_alignment: "left",
    });

    refs.authStatus.textContent = "Ready for Google authentication.";
  } catch (error) {
    refs.authStatus.textContent = `Unable to initialize Google Sign-In: ${error.message}`;
  }
}

function enterAppExperience() {
  refs.authView.hidden = true;
  refs.appHeader.hidden = false;
  refs.appMain.hidden = false;
  if (state.auth.authenticated && state.auth.user) {
    refs.userIdentity.textContent = state.auth.user.email || state.auth.user.name || "Authenticated";
    refs.logoutButton.hidden = false;
  } else {
    refs.userIdentity.textContent = "Guest Session";
    refs.logoutButton.hidden = true;
  }
}

async function continueAsGuest() {
  refs.authStatus.textContent = "Entering guest projector mode...";
  refs.continueGuestButton.disabled = true;
  enterAppExperience();
  try {
    await initializeRuntimeData();
    refs.authStatus.textContent = "Guest mode ready.";
  } catch (error) {
    refs.authStatus.textContent = `Guest mode started with limited data: ${error.message}`;
    announce("Some sync endpoints are unavailable. Retrying in background is safe.");
  } finally {
    refs.continueGuestButton.disabled = false;
  }
}

function switchView(nextView) {
  refs.views.forEach((view) => view.classList.remove("is-active"));
  refs.navButtons.forEach((button) => button.classList.remove("is-active"));

  document.getElementById(nextView)?.classList.add("is-active");
  document.querySelector(`.nav-btn[data-view="${nextView}"]`)?.classList.add("is-active");
}

function formatDate(timestamp) {
  if (!timestamp) return "Unknown";
  return new Date(timestamp).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function sanitize(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function dataUrlToFile(dataUrl, name = "source-image.jpg") {
  const [header, data] = dataUrl.split(",");
  const mime = header.match(/:(.*?);/)?.[1] || "image/jpeg";
  const binary = atob(data);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return new File([bytes], name, { type: mime });
}

function getCurrentParams() {
  return {
    provider: refs.providerSelect.value || "auto",
    preset: refs.presetSelect.value || "cinematic-balanced",
    duration: Number(refs.durationInput.value || 6),
    variants: Number(refs.variantCountInput.value || 3),
    aspect_ratio: refs.aspectSelect.value,
    motion_intensity: Number(refs.motionInput.value || 6),
    quality_mode: refs.qualitySelect.value,
    negative_intent: refs.negativeIntentInput.value.trim(),
  };
}

function setCurrentParams(params = {}) {
  refs.providerSelect.value = params.provider || "auto";
  refs.presetSelect.value = params.preset || state.settings.preferences.defaultPreset || "cinematic-balanced";
  refs.durationInput.value = params.duration || state.settings.preferences.defaultDuration || 6;
  refs.variantCountInput.value = params.variants || state.settings.preferences.defaultVariants || 3;
  refs.aspectSelect.value = params.aspect_ratio || state.settings.preferences.defaultAspectRatio || "16:9";
  refs.motionInput.value = params.motion_intensity || 6;
  refs.qualitySelect.value = params.quality_mode || state.settings.behavior.renderQuality || "balanced";
  refs.negativeIntentInput.value = params.negative_intent || "";
  syncCameraCards();
  syncMovementVocabulary();
  updateCostPreview();
}

function hasSourceImage() {
  return Boolean(state.currentImageFile || state.currentImageUrl);
}

function isReducedMotion() {
  return (
    Boolean(state.settings.accessibility.reducedMotion) ||
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true
  );
}

function setGenerateEnabled() {
  if (state.activeGeneration) return;
  const hasImage = hasSourceImage();
  const hasIntent = refs.intentInput.value.trim().length > 0;
  refs.generateButton.disabled = !(hasImage && hasIntent);
}

function setRunPending(isPending) {
  const button = refs.generateButton;
  if (isPending) {
    button.textContent = "Cut";
    button.classList.remove("btn-primary");
    button.classList.add("btn-danger");
    button.setAttribute("aria-label", "Cut the current take");
    button.disabled = false;
  } else {
    button.textContent = "Roll Camera";
    button.classList.add("btn-primary");
    button.classList.remove("btn-danger");
    button.removeAttribute("aria-label");
    setGenerateEnabled();
  }
}

function cutActiveGeneration() {
  state.activeGeneration?.controller.abort();
}

function updateCostPreview() {
  if (!refs.costPreview) return;
  const meta = PROVIDER_META[refs.providerSelect.value];
  if (!meta) {
    refs.costPreview.hidden = true;
    return;
  }
  const duration = Number(refs.durationInput.value || 6);
  const variants = Number(refs.variantCountInput.value || 3);
  const cost = (variants * duration * meta.costPerSecond).toFixed(2);
  refs.costPreview.hidden = false;
  refs.costPreview.textContent = `${variants} variants × ${duration}s ≈ $${cost} • ~${meta.estSeconds}s wait`;
}

function setCurrentImage(file, dataUrl) {
  state.currentImageFile = file;
  state.currentImageName = file.name;
  state.currentImageUrl = dataUrl;
  refs.sourcePreview.src = dataUrl;
  refs.dropZone.classList.add("has-image");
  refs.dropZoneText.innerHTML = `<strong>${sanitize(file.name)}</strong><span>Key frame loaded</span>`;
  setGenerateEnabled();
  announce("Source frame loaded.");
}

function createSampleFrameDataUrl() {
  const canvas = document.createElement("canvas");
  canvas.width = 960;
  canvas.height = 540;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = "#0b0a08";
  ctx.fillRect(0, 0, 960, 540);

  const glow = ctx.createRadialGradient(620, 210, 40, 620, 210, 430);
  glow.addColorStop(0, "rgba(255, 179, 71, 0.85)");
  glow.addColorStop(0.45, "rgba(255, 143, 31, 0.28)");
  glow.addColorStop(1, "rgba(255, 143, 31, 0)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, 960, 540);

  ctx.fillStyle = "#08070a";
  ctx.fillRect(150, 250, 130, 290);

  ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
  ctx.fillRect(0, 470, 960, 70);

  return canvas.toDataURL("image/jpeg", 0.92);
}

function attachSampleFrameEvents() {
  const button = refs.sampleFrameButton;
  if (!button) return;
  button.addEventListener("keydown", (event) => event.stopPropagation());
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const dataUrl = createSampleFrameDataUrl();
    setCurrentImage(dataUrlToFile(dataUrl, "sample-frame.jpg"), dataUrl);
    if (!refs.intentInput.value.trim()) {
      refs.intentInput.value =
        "Slow push-in on the silhouette, warm amber practicals, soft haze, stable identity.";
      announce("Sample intent loaded. Ready to roll camera.");
    }
    setGenerateEnabled();
  });
}

function attachUploadEvents() {
  attachSampleFrameEvents();
  refs.dropZone.addEventListener("click", () => refs.fileInput.click());
  refs.dropZone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      refs.fileInput.click();
    }
  });

  refs.fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setCurrentImage(file, reader.result);
    reader.readAsDataURL(file);
  });

  refs.dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    refs.dropZone.classList.add("is-dragover");
  });

  refs.dropZone.addEventListener("dragleave", () => {
    refs.dropZone.classList.remove("is-dragover");
  });

  refs.dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    refs.dropZone.classList.remove("is-dragover");
    const file = event.dataTransfer?.files?.[0];
    if (!file || !file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = () => setCurrentImage(file, reader.result);
    reader.readAsDataURL(file);
  });
}

function createLoadingCards(count) {
  refs.resultGrid.innerHTML = "";
  for (let index = 0; index < count; index += 1) {
    const skeleton = document.createElement("div");
    skeleton.className = "skeleton";
    refs.resultGrid.appendChild(skeleton);
  }
}

function executionUrl(variant) {
  return (
    variant.execution?.result?.video_url ||
    variant.execution?.result?.output_url ||
    variant.execution?.result?.url ||
    null
  );
}

function currentRun() {
  return state.runs.find((run) => run.run_id === state.currentRunId) || null;
}

async function persistRun(run) {
  if (!run?.run_id) return;
  try {
    await requestJSON(`/api/runs/${encodeURIComponent(run.run_id)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(run),
    });
  } catch (error) {
    console.warn("Could not persist run", error);
  }
}

async function toggleFavorite(runId, variantId) {
  const run = state.runs.find((entry) => entry.run_id === runId);
  if (!run) return;
  const variant = run.variants.find((entry) => entry.id === variantId);
  if (!variant) return;
  variant.favorite = !variant.favorite;
  await persistRun(run);
  if (state.currentRunId === runId) {
    renderResults(run, { preserveCompare: !refs.comparePanel.hidden });
  }
  renderHistory();
  renderFavorites();
}

function openContextMenu(event, items) {
  closeContextMenu();
  const menu = document.createElement("div");
  menu.className = "context-menu";
  items.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item.label;
    button.addEventListener("click", () => {
      closeContextMenu();
      item.action();
    });
    menu.appendChild(button);
  });

  menu.style.left = `${Math.min(window.innerWidth - 190, event.clientX)}px`;
  menu.style.top = `${Math.min(window.innerHeight - 180, event.clientY)}px`;
  document.body.appendChild(menu);
  state.contextMenu = menu;

  setTimeout(() => {
    document.addEventListener("click", onContextDismiss, { once: true });
  }, 0);
}

function onContextDismiss() {
  closeContextMenu();
}

function closeContextMenu() {
  if (state.contextMenu) {
    state.contextMenu.remove();
    state.contextMenu = null;
  }
}

function buildResultCard(run, variant) {
  const card = document.createElement("article");
  card.className = "result-card";

  const videoUrl = executionUrl(variant);
  const statusClass = sanitize(variant.status || "unknown");

  card.innerHTML = `
    <button class="context-btn" type="button" aria-label="Open contextual menu">⋯</button>
    <div class="result-media">
      ${
        videoUrl
          ? `<video controls preload="metadata" src="${sanitize(videoUrl)}" aria-label="Generated output for ${sanitize(variant.label)}"></video>`
          : run.source_image_data_url
            ? `<img src="${sanitize(run.source_image_data_url)}" alt="Source preview for ${sanitize(variant.label)}" />`
            : `<span>No output URL</span>`
      }
    </div>
    <div class="result-body">
      <div class="result-meta">
        <strong>${sanitize(variant.label)}</strong>
        <span class="badge ${statusClass}">${statusClass}</span>
      </div>
      <div class="badge-row">
        <span class="badge">${sanitize(variant.provider || "provider: n/a")}</span>
        <span class="badge">Rules ${sanitize(variant.compiled_prompt?.cinematic_rules?.total_rules_applied ?? "n/a")}</span>
        <span class="badge">Seed ${sanitize(variant.model_parameters?.seed ?? "-")}</span>
      </div>
      <div class="action-row">
        <button class="btn-small ${variant.favorite ? "is-favorited" : ""}" type="button" data-favorite>
          ${variant.favorite ? "Favorited" : "Favorite"}
        </button>
        <button class="btn-small" type="button" data-rerun>Regenerate</button>
        ${videoUrl ? `<a class="btn-small" href="${sanitize(videoUrl)}" target="_blank" rel="noreferrer noopener">Open output</a>` : ""}
      </div>
      <label class="result-check">
        <input type="checkbox" data-compare ${state.selectedForCompare.has(variant.id) ? "checked" : ""} />
        Compare
      </label>
      ${variant.error ? `<p class="alert">${sanitize(variant.error)}</p>` : ""}
      ${state.settings.developer.showRawPayload ? `<pre>${sanitize(JSON.stringify(variant.execution || {}, null, 2))}</pre>` : ""}
    </div>
  `;

  card.querySelector("[data-favorite]").addEventListener("click", async () => {
    await toggleFavorite(run.run_id, variant.id);
  });

  card.querySelector("[data-rerun]").addEventListener("click", () => {
    rerunFromRun(run.run_id);
  });

  card.querySelector("[data-compare]").addEventListener("change", (event) => {
    if (event.target.checked) {
      if (state.selectedForCompare.size >= 3) {
        event.target.checked = false;
        announce("Compare supports up to 3 variants.");
        return;
      }
      state.selectedForCompare.add(variant.id);
    } else {
      state.selectedForCompare.delete(variant.id);
    }
    refs.openCompareButton.disabled = state.selectedForCompare.size < 2;
  });

  card.querySelector(".context-btn").addEventListener("click", (event) => {
    openContextMenu(event, [
      {
        label: variant.favorite ? "Unfavorite" : "Favorite",
        action: () => toggleFavorite(run.run_id, variant.id),
      },
      {
        label: "Regenerate from this run",
        action: () => rerunFromRun(run.run_id),
      },
      {
        label: "Open output",
        action: () => {
          if (videoUrl) window.open(videoUrl, "_blank", "noopener,noreferrer");
        },
      },
    ]);
  });

  return card;
}

function renderResults(run, options = {}) {
  refs.resultGrid.innerHTML = "";
  if (!options.preserveCompare) {
    refs.comparePanel.hidden = true;
    state.selectedForCompare.clear();
    refs.openCompareButton.disabled = true;
  }

  if (!run || !Array.isArray(run.variants) || run.variants.length === 0) {
    refs.resultGrid.innerHTML = '<p class="list-card">No takes yet.</p>';
    return;
  }

  run.variants.forEach((variant) => {
    refs.resultGrid.appendChild(buildResultCard(run, variant));
  });
}

function renderTimeline() {
  refs.timelineList.innerHTML = "";

  if (state.pendingRun) {
    const pending = document.createElement("article");
    pending.className = "timeline-item";
    pending.innerHTML = `
      <div>
        <strong>${sanitize(state.pendingRun.intent.slice(0, 70))}</strong>
        <p>${formatDate(state.pendingRun.createdAt)} • ${sanitize(state.pendingRun.params.preset)}</p>
      </div>
      <span class="badge not_executed">running</span>
    `;
    refs.timelineList.appendChild(pending);
  }

  if (!state.runs.length) {
    refs.timelineList.innerHTML += '<p class="list-card">No timeline events yet.</p>';
    return;
  }

  state.runs
    .slice()
    .reverse()
    .slice(0, 10)
    .forEach((run) => {
      const row = document.createElement("article");
      row.className = "timeline-item";
      row.innerHTML = `
        <div>
          <strong>${sanitize(run.intent.slice(0, 68))}${run.intent.length > 68 ? "..." : ""}</strong>
          <p>${formatDate(run.created_at)} • ${sanitize(run.params?.preset || "custom")}</p>
        </div>
        <span class="badge ${sanitize(run.status)}">${sanitize(run.status)}</span>
      `;
      refs.timelineList.appendChild(row);
    });
}

function buildRunListCard(run) {
  const card = document.createElement("article");
  card.className = "list-card";
  card.innerHTML = `
    <strong>${sanitize(run.intent.slice(0, 96))}${run.intent.length > 96 ? "..." : ""}</strong>
    <p>${formatDate(run.created_at)} • ${sanitize(run.params?.preset || "custom")} • ${sanitize(run.params?.aspect_ratio || "16:9")}</p>
    <div class="badge-row">
      <span class="badge ${sanitize(run.status)}">${sanitize(run.status)}</span>
      <span class="badge">${sanitize((run.variants || []).length)} variants</span>
      <span class="badge">Objects ${sanitize(run.analysis?.object_count ?? 0)}</span>
    </div>
    <div class="action-row">
      <button class="btn-small" type="button" data-open>Open</button>
      <button class="btn-small" type="button" data-rerun>Regenerate</button>
    </div>
  `;

  card.querySelector("[data-open]").addEventListener("click", () => {
    switchView("createView");
    state.currentRunId = run.run_id;
    refs.intentInput.value = run.intent;
    setCurrentParams(run.params || {});
    if (run.source_image_data_url) {
      state.currentImageUrl = run.source_image_data_url;
      state.currentImageName = run.source_image?.filename || "history-source.jpg";
      refs.sourcePreview.src = run.source_image_data_url;
      refs.dropZone.classList.add("has-image");
      refs.dropZoneText.innerHTML = `<strong>${sanitize(state.currentImageName)}</strong><span>Loaded from history</span>`;
    }
    refs.runSummary.textContent = `Run ${run.run_id} • ${run.status}`;
    renderResults(run);
    setGenerateEnabled();
  });

  card.querySelector("[data-rerun]").addEventListener("click", () => rerunFromRun(run.run_id));

  return card;
}

function renderHistory() {
  refs.historyList.innerHTML = "";
  if (!state.runs.length) {
    refs.historyList.innerHTML = '<p class="list-card">No runs yet.</p>';
    return;
  }

  state.runs
    .slice()
    .reverse()
    .forEach((run) => refs.historyList.appendChild(buildRunListCard(run)));
}

function renderFavorites() {
  refs.favoritesList.innerHTML = "";
  const favorites = [];

  state.runs.forEach((run) => {
    (run.variants || []).forEach((variant) => {
      if (variant.favorite) favorites.push({ run, variant });
    });
  });

  if (!favorites.length) {
    refs.favoritesList.innerHTML = '<p class="list-card">No favorites yet.</p>';
    return;
  }

  favorites
    .slice()
    .reverse()
    .forEach(({ run, variant }) => {
      const card = document.createElement("article");
      card.className = "list-card";
      card.innerHTML = `
        <strong>${sanitize(variant.label)}</strong>
        <p>${sanitize(run.intent.slice(0, 96))}${run.intent.length > 96 ? "..." : ""}</p>
        <div class="badge-row">
          <span class="badge ${sanitize(variant.status)}">${sanitize(variant.status)}</span>
          <span class="badge">${sanitize(variant.provider || "no provider")}</span>
        </div>
        <div class="action-row">
          <button class="btn-small" type="button" data-open>Open run</button>
          <button class="btn-small" type="button" data-rerun>Regenerate</button>
          <button class="btn-small is-favorited" type="button" data-unfav>Unfavorite</button>
        </div>
      `;

      card.querySelector("[data-open]").addEventListener("click", () => {
        switchView("createView");
        state.currentRunId = run.run_id;
        renderResults(run);
      });
      card.querySelector("[data-rerun]").addEventListener("click", () => rerunFromRun(run.run_id));
      card.querySelector("[data-unfav]").addEventListener("click", () => toggleFavorite(run.run_id, variant.id));
      refs.favoritesList.appendChild(card);
    });
}

async function loadRuns() {
  const payload = await requestJSON("/api/runs?limit=200");
  state.runs = Array.isArray(payload.runs) ? payload.runs : [];

  if (state.runs.length) {
    const latest = state.runs[state.runs.length - 1];
    state.currentRunId = latest.run_id;
    refs.runSummary.textContent = `Run ${latest.run_id} • ${latest.status}`;
  } else {
    refs.runSummary.textContent = "No takes yet";
  }
}

async function clearAllRuns() {
  if (state.settings.behavior.confirmBeforeClear) {
    const confirmed = window.confirm("Clear all timeline runs for this profile?");
    if (!confirmed) return;
  }

  await requestJSON("/api/runs", { method: "DELETE" });
  state.runs = [];
  state.currentRunId = null;
  state.selectedForCompare.clear();
  refs.resultGrid.innerHTML = "";
  refs.compareGrid.innerHTML = "";
  refs.comparePanel.hidden = true;
  refs.runSummary.textContent = "No takes yet";
  renderTimeline();
  renderHistory();
  renderFavorites();
  announce("Timeline cleared.");
}

async function loadProviders() {
  const payload = await requestJSON("/api/providers");
  state.providerOptions = payload.available_providers || [];

  refs.providerSelect.innerHTML = '<option value="auto">Auto (best available)</option>';
  (payload.supported_providers || []).forEach((provider) => {
    const option = document.createElement("option");
    option.value = provider;
    const configured = state.providerOptions.includes(provider);
    option.textContent = providerOptionLabel(provider, configured);
    option.title = providerOptionTooltip(provider, configured);
    if (PROVIDER_META[provider]?.deprecated) {
      option.classList.add("is-deprecated");
    }
    refs.providerSelect.appendChild(option);
  });
  renderCameraCards(payload.providers || []);
  updateCostPreview();
}

function providerOptionLabel(provider, configured) {
  const meta = PROVIDER_META[provider];
  if (!meta) {
    return configured ? `${provider} (configured)` : `${provider} (not configured)`;
  }
  let label = `${meta.label} — ${meta.audio ? "audio" : "no audio"} • ~$${meta.costPerSecond.toFixed(2)}/s`;
  if (meta.deprecated) label += " (deprecated)";
  if (!configured) label += " (not configured)";
  return label;
}

function providerOptionTooltip(provider, configured) {
  const meta = PROVIDER_META[provider];
  if (!meta) {
    return configured ? `${provider}: configured` : `${provider}: API key not configured`;
  }
  const parts = [
    `${meta.label}: ~${meta.estSeconds}s per take`,
    `max ${meta.maxDuration}s clip`,
    meta.audio ? "native audio" : "no audio",
  ];
  if (meta.deprecated) parts.push("deprecated");
  if (!configured) parts.push("API key not configured");
  return parts.join(" • ");
}

async function loadPresets() {
  const payload = await requestJSON("/api/presets");
  state.presets = payload.presets || [];

  refs.presetSelect.innerHTML = "";
  refs.presetCards.innerHTML = "";

  state.presets.forEach((preset) => {
    const option = document.createElement("option");
    option.value = preset.id;
    option.textContent = preset.name;
    refs.presetSelect.appendChild(option);

    const card = document.createElement("article");
    card.innerHTML = `
      <h4>${sanitize(preset.name)}</h4>
      <p>${sanitize(preset.description)}</p>
      <span class="badge">Temporal ${sanitize(preset.temporal_priority)}</span>
    `;
    refs.presetCards.appendChild(card);
  });
}

function classifyGenerationError(error) {
  const status = Number(error?.status || 0);
  const lower = String(error?.message || "").toLowerCase();

  if (status === 429 || lower.includes("429") || lower.includes("rate limit") || lower.includes("overload")) {
    return { headline: "Provider overloaded", actions: ["retry", "switch-provider"] };
  }
  if (
    status === 401 ||
    status === 403 ||
    lower.includes("401") ||
    lower.includes("403") ||
    lower.includes("api key") ||
    lower.includes("unauthorized") ||
    lower.includes("forbidden") ||
    lower.includes("authentication")
  ) {
    return { headline: "API key rejected", actions: ["open-settings"] };
  }
  if (
    lower.includes("content policy") ||
    lower.includes("policy violation") ||
    lower.includes("safety") ||
    lower.includes("moderation")
  ) {
    return { headline: "Prompt rejected by safety filter", actions: ["edit-intent"] };
  }
  return { headline: "Generation failed", actions: ["retry"] };
}

function renderRecoveryCard(error, retryArgs) {
  const info = classifyGenerationError(error);
  const RECOVERY_ACTIONS = {
    retry: { label: "Retry", run: () => executeGeneration(retryArgs) },
    "switch-provider": { label: "Switch provider", run: () => refs.providerSelect.focus() },
    "open-settings": { label: "Open Settings", run: () => switchView("settingsView") },
    "edit-intent": { label: "Edit intent", run: () => refs.intentInput.focus() },
  };

  const card = document.createElement("article");
  card.className = "recovery-card";
  card.setAttribute("role", "alert");
  card.innerHTML = `
    <strong>${sanitize(info.headline)}</strong>
    <p>${sanitize(error?.message || "Unknown error.")}</p>
    <div class="action-row"></div>
  `;

  const actionRow = card.querySelector(".action-row");
  info.actions.forEach((key) => {
    const action = RECOVERY_ACTIONS[key];
    if (!action) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn-small";
    button.textContent = action.label;
    button.addEventListener("click", action.run);
    actionRow.appendChild(button);
  });

  refs.resultGrid.innerHTML = "";
  refs.resultGrid.appendChild(card);
  actionRow.querySelector("button")?.focus();
}

async function executeGeneration({ imageFile, sourceImageDataUrl, intent, params }) {
  if (state.activeGeneration) {
    announce("A take is already rolling. Cut it before starting another.");
    return;
  }

  const controller = new AbortController();
  const generation = { controller, timedOut: false };
  const timeoutId = setTimeout(() => {
    generation.timedOut = true;
    controller.abort();
  }, GENERATION_TIMEOUT_MS);
  state.activeGeneration = generation;
  setRunPending(true);

  state.pendingRun = {
    createdAt: Date.now(),
    intent,
    params,
  };
  renderTimeline();
  createLoadingCards(params.variants);
  refs.runSummary.textContent = "Projector spinning...";
  announce("Generation request sent.");

  const formData = new FormData();
  formData.append("image", imageFile, imageFile.name || "source.jpg");
  formData.append("intent", intent);
  formData.append("provider", params.provider);
  formData.append("preset", params.preset);
  formData.append("duration", String(params.duration));
  formData.append("variants", String(params.variants));
  formData.append("aspect_ratio", params.aspect_ratio);
  formData.append("motion_intensity", String(params.motion_intensity));
  formData.append("quality_mode", params.quality_mode);
  formData.append("negative_intent", params.negative_intent || "");

  try {
    // Dailies Room first: async SSE mode with transparent synchronous fallback.
    const asyncOutcome = await attemptAsyncGeneration({
      formData,
      params,
      sourceImageDataUrl,
      signal: controller.signal,
    });

    let resultPayload = null;
    if (asyncOutcome.mode === "async-complete") {
      resultPayload = asyncOutcome.run;
    } else {
      let { response, payload } = asyncOutcome;
      if (asyncOutcome.mode === "retry-sync") {
        // The dailies feed never came up — replay the classic synchronous take.
        createLoadingCards(params.variants);
        refs.runSummary.textContent = "Projector spinning...";
        response = await fetch("/api/sequences", {
          method: "POST",
          credentials: "same-origin",
          body: formData,
          signal: controller.signal,
        });
        try {
          payload = await response.json();
        } catch {
          payload = null;
        }
      }
      if (!response.ok) {
        const detail = payload?.detail;
        const failure = new Error(
          typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : "Generation failed.",
        );
        failure.status = response.status;
        throw failure;
      }
      resultPayload = payload;
    }

    const run = {
      ...resultPayload,
      source_image_data_url: sourceImageDataUrl,
      variants: (resultPayload.variants || []).map((variant) => ({
        ...variant,
        favorite: Boolean(variant.favorite),
      })),
    };

    state.runs.push(run);
    state.currentRunId = run.run_id;
    await persistRun(run);

    renderResults(run);
    refs.runSummary.textContent = `Run ${run.run_id} • ${run.status}`;
    announce(`Generation finished with status: ${run.status}`);
    maybeAutoOpenLightTable(run);
  } catch (error) {
    const retryArgs = { imageFile, sourceImageDataUrl, intent, params };
    if (error?.name === "AbortError" || error?.code === "cancelled") {
      refs.resultGrid.innerHTML = "";
      if (generation.timedOut) {
        refs.runSummary.textContent = "Take timed out";
        renderRecoveryCard(new Error(`Generation timed out after ${GENERATION_TIMEOUT_MS / 1000} seconds.`), retryArgs);
        announce("Generation timed out.");
      } else {
        refs.runSummary.textContent = "Take cut";
        showToast("Take cut.");
        announce("Take cut.");
      }
    } else {
      renderRecoveryCard(error, retryArgs);
      refs.runSummary.textContent = "Generation failed";
      announce(`Generation failed: ${error.message}`);
    }
  } finally {
    clearTimeout(timeoutId);
    state.activeGeneration = null;
    setRunPending(false);
    state.pendingRun = null;
    renderTimeline();
    renderHistory();
    renderFavorites();
  }
}

async function generateSequence() {
  if (state.activeGeneration) return;
  const intent = refs.intentInput.value.trim();
  if (!intent) {
    announce("Director intent is required.");
    return;
  }

  let imageFile = state.currentImageFile;
  if (!imageFile && state.currentImageUrl) {
    imageFile = dataUrlToFile(state.currentImageUrl, state.currentImageName || "source-image.jpg");
  }

  if (!imageFile) {
    announce("Upload a source frame before generation.");
    return;
  }

  const params = getCurrentParams();
  await executeGeneration({
    imageFile,
    sourceImageDataUrl: state.currentImageUrl,
    intent,
    params,
  });
}

async function rerunFromRun(runId) {
  const run = state.runs.find((entry) => entry.run_id === runId);
  if (!run) return;

  const sourceDataUrl = run.source_image_data_url || state.currentImageUrl;
  if (!sourceDataUrl) {
    announce("Source frame is unavailable for rerun.");
    return;
  }

  const imageFile = dataUrlToFile(sourceDataUrl, run.source_image?.filename || "source-image.jpg");
  refs.intentInput.value = run.intent;
  setCurrentParams(run.params || {});
  switchView("createView");

  state.currentImageUrl = sourceDataUrl;
  state.currentImageFile = imageFile;
  state.currentImageName = imageFile.name;
  refs.sourcePreview.src = sourceDataUrl;
  refs.dropZone.classList.add("has-image");
  refs.dropZoneText.innerHTML = `<strong>${sanitize(imageFile.name)}</strong><span>Loaded for rerun</span>`;
  setGenerateEnabled();

  await executeGeneration({
    imageFile,
    sourceImageDataUrl: sourceDataUrl,
    intent: run.intent,
    params: run.params,
  });
}

function mergeSettings(settings) {
  state.settings = {
    ...structuredClone(DEFAULT_SETTINGS),
    ...state.settings,
    ...settings,
    accessibility: {
      ...DEFAULT_SETTINGS.accessibility,
      ...(state.settings.accessibility || {}),
      ...(settings.accessibility || {}),
    },
    preferences: {
      ...DEFAULT_SETTINGS.preferences,
      ...(state.settings.preferences || {}),
      ...(settings.preferences || {}),
    },
    behavior: {
      ...DEFAULT_SETTINGS.behavior,
      ...(state.settings.behavior || {}),
      ...(settings.behavior || {}),
    },
    theme: {
      ...DEFAULT_SETTINGS.theme,
      ...(state.settings.theme || {}),
      ...(settings.theme || {}),
    },
    developer: {
      ...DEFAULT_SETTINGS.developer,
      ...(state.settings.developer || {}),
      ...(settings.developer || {}),
    },
  };
}

async function loadSettings() {
  const payload = await requestJSON("/api/settings");
  mergeSettings(payload.settings || {});
  state.settingsVersion = payload.version || 1;
  state.settingsUpdatedAt = payload.updated_at;
  renderSettingsState();
}

function renderSettingsState() {
  refs.reducedMotionToggle.checked = Boolean(state.settings.accessibility.reducedMotion);
  refs.autoFavoriteToggle.checked = Boolean(state.settings.preferences.autoFavoriteWinner);
  refs.autoOpenCompareToggle.checked = state.settings.preferences.autoOpenCompare !== false;
  refs.announceStatusToggle.checked = Boolean(state.settings.accessibility.announceStatusChanges);

  refs.autoSaveDelayInput.value = Number(state.settings.behavior.autoSaveDelayMs || 700);
  refs.parallelPreviewInput.value = Number(state.settings.behavior.parallelPreviews || 2);
  refs.confirmClearToggle.checked = Boolean(state.settings.behavior.confirmBeforeClear);

  refs.accentSelect.value = state.settings.theme.accent || "amber";
  refs.grainInput.value = Number(state.settings.theme.grain ?? 0.35);
  refs.contrastInput.value = Number(state.settings.theme.contrast ?? 1);

  refs.debugOverlayToggle.checked = Boolean(state.settings.developer.enableDebugOverlay);
  refs.rawPayloadToggle.checked = Boolean(state.settings.developer.showRawPayload);
  refs.gestureNavToggle.checked = Boolean(state.settings.developer.gestureNavigation);

  refs.settingsVersion.textContent = `v${state.settingsVersion}`;
  refs.syncState.textContent = state.settingsUpdatedAt ? `Synced ${formatDate(state.settingsUpdatedAt)}` : "Idle";

  applyThemePreview();
}

function collectSettingsFromUI() {
  return {
    ...state.settings,
    accessibility: {
      ...state.settings.accessibility,
      reducedMotion: refs.reducedMotionToggle.checked,
      announceStatusChanges: refs.announceStatusToggle.checked,
    },
    preferences: {
      ...state.settings.preferences,
      autoFavoriteWinner: refs.autoFavoriteToggle.checked,
      autoOpenCompare: refs.autoOpenCompareToggle.checked,
    },
    behavior: {
      ...state.settings.behavior,
      autoSaveDelayMs: Number(refs.autoSaveDelayInput.value || 700),
      parallelPreviews: Number(refs.parallelPreviewInput.value || 2),
      confirmBeforeClear: refs.confirmClearToggle.checked,
    },
    theme: {
      ...state.settings.theme,
      accent: refs.accentSelect.value,
      grain: Number(refs.grainInput.value || 0.35),
      contrast: Number(refs.contrastInput.value || 1),
    },
    developer: {
      ...state.settings.developer,
      enableDebugOverlay: refs.debugOverlayToggle.checked,
      showRawPayload: refs.rawPayloadToggle.checked,
      gestureNavigation: refs.gestureNavToggle.checked,
    },
  };
}

async function saveSettings(changeNote = "autosave") {
  const nextSettings = collectSettingsFromUI();
  mergeSettings(nextSettings);
  refs.syncState.textContent = "Saving...";

  const payload = await requestJSON("/api/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      settings: state.settings,
      change_note: changeNote,
    }),
  });

  state.settingsVersion = payload.version || state.settingsVersion;
  state.settingsUpdatedAt = payload.updated_at;
  refs.settingsVersion.textContent = `v${state.settingsVersion}`;
  refs.syncState.textContent = `Synced ${formatDate(state.settingsUpdatedAt)}`;

  applyThemePreview();
  await loadSettingsHistory();
}

function scheduleSettingsSave(changeNote = "autosave") {
  if (!state.settings.behavior.autoSave) {
    return;
  }

  const delay = Number(refs.autoSaveDelayInput.value || state.settings.behavior.autoSaveDelayMs || 700);
  clearTimeout(state.settingsSaveTimer);
  state.settingsSaveTimer = setTimeout(() => {
    saveSettings(changeNote).catch((error) => {
      refs.syncState.textContent = `Save failed: ${error.message}`;
    });
  }, Math.max(250, delay));
}

function applyThemePreview() {
  document.body.dataset.accent = refs.accentSelect.value || "amber";
  document.documentElement.style.setProperty("--grain-opacity", String(refs.grainInput.value || 0.35));
  document.documentElement.style.setProperty("--global-contrast", String(refs.contrastInput.value || 1));

  refs.themePreview.innerHTML = `
    <p>Live Preview</p>
    <h4>Accent: ${sanitize(refs.accentSelect.value)}</h4>
    <p>Grain ${sanitize(refs.grainInput.value)} • Contrast ${sanitize(refs.contrastInput.value)}</p>
  `;
}

async function loadSettingsHistory() {
  const payload = await requestJSON("/api/settings/history?limit=20");
  const history = payload.history || [];
  refs.settingsHistoryList.innerHTML = "";

  if (!history.length) {
    refs.settingsHistoryList.innerHTML = '<p class="list-card">No versions yet.</p>';
    return;
  }

  history.forEach((entry) => {
    const row = document.createElement("article");
    row.className = "history-row";
    row.innerHTML = `
      <div class="history-row-meta">
        <strong>v${sanitize(entry.version)}</strong>
        <p>${sanitize(entry.change_note || "update")} • ${formatDate(entry.created_at)}</p>
      </div>
      <button class="btn-small" type="button" data-restore>Restore</button>
    `;

    row.querySelector("[data-restore]").addEventListener("click", async () => {
      await requestJSON(`/api/settings/history/${entry.id}/restore`, { method: "POST" });
      await loadSettings();
      await loadSettingsHistory();
      announce(`Restored settings version v${entry.version}.`);
    });

    refs.settingsHistoryList.appendChild(row);
  });
}

async function loadApiKeyStatuses() {
  const payload = await requestJSON("/api/settings/api-keys");
  const rows = payload.api_keys || [];
  refs.apiKeyRows.innerHTML = "";

  rows.forEach((row) => {
    const container = document.createElement("article");
    container.className = "api-key-row";
    container.innerHTML = `
      <div class="api-key-row-head">
        <strong>${sanitize(row.provider)}</strong>
        <span class="key-state">${row.configured ? `Configured (${sanitize(row.masked || "masked")})` : "Not configured"}</span>
      </div>
      <input type="password" placeholder="Enter ${sanitize(row.provider)} API key" data-key-input />
      <div class="key-actions">
        <button class="btn-small" type="button" data-save-key>Save</button>
        <button class="btn-small" type="button" data-clear-key>Clear</button>
      </div>
    `;

    container.querySelector("[data-save-key]").addEventListener("click", async () => {
      const input = container.querySelector("[data-key-input]");
      const apiKey = input.value.trim();
      if (!apiKey) {
        announce(`Enter a key before saving ${row.provider}.`);
        return;
      }
      await requestJSON(`/api/settings/api-keys/${encodeURIComponent(row.provider)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey }),
      });
      input.value = "";
      announce(`${row.provider} key stored securely.`);
      await Promise.all([loadApiKeyStatuses(), loadProviders()]);
    });

    container.querySelector("[data-clear-key]").addEventListener("click", async () => {
      await requestJSON(`/api/settings/api-keys/${encodeURIComponent(row.provider)}`, {
        method: "DELETE",
      });
      announce(`${row.provider} key removed.`);
      await Promise.all([loadApiKeyStatuses(), loadProviders()]);
    });

    refs.apiKeyRows.appendChild(container);
  });
}

async function exportBackup() {
  const payload = await requestJSON("/api/settings/backup");
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `animatize-backup-${new Date().toISOString().slice(0, 10)}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
  announce("Backup exported.");
}

async function importBackup(file) {
  const text = await file.text();
  const payload = JSON.parse(text);
  await requestJSON("/api/settings/restore", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  await Promise.all([loadSettings(), loadSettingsHistory(), loadRuns()]);
  renderTimeline();
  renderHistory();
  renderFavorites();
  announce("Backup restored.");
}

function attachSettingsEvents() {
  refs.settingsToggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const panel = document.getElementById(toggle.dataset.target);
      const isOpen = panel.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });
  });

  [
    refs.reducedMotionToggle,
    refs.autoFavoriteToggle,
    refs.autoOpenCompareToggle,
    refs.announceStatusToggle,
    refs.autoSaveDelayInput,
    refs.parallelPreviewInput,
    refs.confirmClearToggle,
    refs.debugOverlayToggle,
    refs.rawPayloadToggle,
    refs.gestureNavToggle,
  ].forEach((element) => {
    element.addEventListener("change", () => {
      scheduleSettingsSave("settings_change");
    });
  });

  [refs.accentSelect, refs.grainInput, refs.contrastInput].forEach((element) => {
    element.addEventListener("input", () => {
      applyThemePreview();
      scheduleSettingsSave("theme_adjustment");
    });
  });

  refs.exportDataButton.addEventListener("click", () => {
    exportBackup().catch((error) => announce(`Export failed: ${error.message}`));
  });

  refs.importDataInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    importBackup(file).catch((error) => announce(`Restore failed: ${error.message}`));
    event.target.value = "";
  });
}

function attachGestureNavigation() {
  refs.appMain.addEventListener("touchstart", (event) => {
    const touch = event.changedTouches?.[0];
    if (!touch) return;
    state.swipe.startX = touch.clientX;
    state.swipe.startY = touch.clientY;
  });

  refs.appMain.addEventListener("touchend", (event) => {
    if (!state.settings.developer.gestureNavigation) return;

    const touch = event.changedTouches?.[0];
    if (!touch) return;

    const deltaX = touch.clientX - state.swipe.startX;
    const deltaY = touch.clientY - state.swipe.startY;
    if (Math.abs(deltaX) < 60 || Math.abs(deltaY) > 45) return;

    const activeView = document.querySelector(".view.is-active")?.id || VIEW_ORDER[0];
    const index = VIEW_ORDER.indexOf(activeView);
    if (index < 0) return;

    const nextIndex = deltaX < 0 ? Math.min(VIEW_ORDER.length - 1, index + 1) : Math.max(0, index - 1);
    if (nextIndex !== index) {
      switchView(VIEW_ORDER[nextIndex]);
      announce(`Switched to ${VIEW_ORDER[nextIndex].replace("View", "")}.`);
    }
  });
}

function attachKeyboardShortcuts() {
  window.addEventListener("keydown", (event) => {
    const tag = document.activeElement?.tagName?.toLowerCase();
    if (tag === "textarea" || tag === "input") return;

    if (event.key.toLowerCase() === "g" && !refs.generateButton.disabled) {
      generateSequence();
    }
    if (event.key.toLowerCase() === "c" && !refs.openCompareButton.disabled) {
      openLightTable({ focus: true });
    }
    if (event.key.toLowerCase() === "r" && state.currentRunId) {
      rerunFromRun(state.currentRunId);
    }
  });
}

function attachCoreEvents() {
  refs.navButtons.forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  refs.continueGuestButton.addEventListener("click", () => {
    continueAsGuest().catch((error) => {
      refs.authStatus.textContent = `Unable to start guest mode: ${error.message}`;
    });
  });

  refs.logoutButton.addEventListener("click", async () => {
    await requestJSON("/api/auth/logout", { method: "POST" });
    state.auth.authenticated = false;
    state.auth.user = null;
    refs.authView.hidden = false;
    refs.appHeader.hidden = true;
    refs.appMain.hidden = true;
    refs.authStatus.textContent = "Signed out. Continue as guest or sign in again.";
  });

  refs.intentInput.addEventListener("input", setGenerateEnabled);
  refs.intentChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      refs.intentInput.value = chip.dataset.intent;
      setGenerateEnabled();
    });
  });

  refs.generateButton.addEventListener("click", () => {
    if (state.activeGeneration) {
      cutActiveGeneration();
      return;
    }
    generateSequence();
  });

  [refs.providerSelect, refs.durationInput, refs.variantCountInput].forEach((element) => {
    element.addEventListener("input", updateCostPreview);
    element.addEventListener("change", updateCostPreview);
  });

  refs.openCompareButton.addEventListener("click", () => {
    openLightTable({ focus: true });
  });

  refs.closeCompareButton.addEventListener("click", () => {
    closeLightTable();
  });

  refs.clearTimelineButton.addEventListener("click", () => {
    clearAllRuns().catch((error) => announce(`Could not clear timeline: ${error.message}`));
  });

  refs.toggleAdvancedButton.addEventListener("click", () => {
    const willExpand = refs.advancedPanel.hidden;
    refs.advancedPanel.hidden = !willExpand;
    refs.toggleAdvancedButton.textContent = willExpand ? "Hide advanced controls" : "Pull focus (advanced)";
    refs.toggleAdvancedButton.setAttribute("aria-expanded", String(willExpand));
  });

  attachUploadEvents();
  attachSettingsEvents();
  attachGestureNavigation();
  attachKeyboardShortcuts();
}

async function initializeRuntimeData() {
  await Promise.all([loadProviders(), loadPresets(), loadSettings(), loadRuns()]);
  await Promise.all([loadSettingsHistory(), loadApiKeyStatuses()]);

  setCurrentParams();
  renderTimeline();
  renderHistory();
  renderFavorites();
  setGenerateEnabled();
}

async function initialize() {
  const moduleContext = {
    state,
    refs,
    PROVIDER_META,
    announce,
    showToast,
    sanitize,
    switchView,
    toggleFavorite,
    executionUrl,
    cutActiveGeneration,
    hasSourceImage,
    isReducedMotion,
  };
  initDailiesRoom(moduleContext);
  initCameraCards(moduleContext);
  initMovementVocabulary(moduleContext);
  initLightTable(moduleContext);
  renderMovementVocabulary();

  attachCoreEvents();

  try {
    await bootstrapSession();
    await Promise.all([loadAuthConfig(), loadCurrentUser()]);

    if (state.auth.authenticated) {
      enterAppExperience();
      await initializeRuntimeData();
      return;
    }

    refs.authView.hidden = false;
    refs.appHeader.hidden = true;
    refs.appMain.hidden = true;
    await initializeGoogleButton();
  } catch (error) {
    refs.authStatus.textContent = `Startup failed: ${error.message}`;
  }
}

initialize();
