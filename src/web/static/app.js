const STORAGE_KEY = "animatize_ui_runs_v2";
const SETTINGS_KEY = "animatize_ui_settings_v2";

const state = {
  currentImageFile: null,
  currentImageUrl: null,
  currentImageName: null,
  currentRunId: null,
  selectedForCompare: new Set(),
  pendingRun: null,
  runs: [],
  providerOptions: [],
  settings: {
    reducedMotion: false,
    autoFavoriteWinner: false,
  },
};

const refs = {
  navButtons: document.querySelectorAll(".nav-btn"),
  views: document.querySelectorAll(".view"),
  dropZone: document.getElementById("dropZone"),
  fileInput: document.getElementById("fileInput"),
  sourcePreview: document.getElementById("sourcePreview"),
  dropZoneText: document.getElementById("dropZoneText"),
  intentInput: document.getElementById("intentInput"),
  intentChips: document.querySelectorAll(".chip"),
  generateButton: document.getElementById("generateButton"),
  resultGrid: document.getElementById("resultGrid"),
  openCompareButton: document.getElementById("openCompareButton"),
  comparePanel: document.getElementById("comparePanel"),
  closeCompareButton: document.getElementById("closeCompareButton"),
  compareGrid: document.getElementById("compareGrid"),
  timelineList: document.getElementById("timelineList"),
  historyList: document.getElementById("historyList"),
  favoritesList: document.getElementById("favoritesList"),
  emptyStateCard: document.getElementById("emptyStateCard"),
  runSummary: document.getElementById("runSummary"),
  statusLive: document.getElementById("statusLive"),
  clearTimelineButton: document.getElementById("clearTimelineButton"),
  providerSelect: document.getElementById("providerSelect"),
  presetSelect: document.getElementById("presetSelect"),
  durationInput: document.getElementById("durationInput"),
  variantCountInput: document.getElementById("variantCountInput"),
  aspectSelect: document.getElementById("aspectSelect"),
  motionInput: document.getElementById("motionInput"),
  qualitySelect: document.getElementById("qualitySelect"),
  negativeIntentInput: document.getElementById("negativeIntentInput"),
  toggleAdvancedButton: document.getElementById("toggleAdvancedButton"),
  advancedPanel: document.getElementById("advancedPanel"),
  reducedMotionToggle: document.getElementById("reducedMotionToggle"),
  autoFavoriteToggle: document.getElementById("autoFavoriteToggle"),
};

function saveRuns() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.runs));
}

function loadRuns() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    state.runs = JSON.parse(raw);
  } catch {
    state.runs = [];
  }
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(state.settings));
}

function loadSettings() {
  const raw = localStorage.getItem(SETTINGS_KEY);
  if (!raw) return;
  try {
    const parsed = JSON.parse(raw);
    state.settings = { ...state.settings, ...parsed };
  } catch {
    // ignore malformed values
  }
}

function announce(message) {
  refs.statusLive.textContent = message;
}

function switchView(nextView) {
  refs.views.forEach((view) => view.classList.remove("is-active"));
  refs.navButtons.forEach((button) => button.classList.remove("is-active"));
  document.getElementById(nextView)?.classList.add("is-active");
  document.querySelector(`[data-view="${nextView}"]`)?.classList.add("is-active");
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
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
    provider: refs.providerSelect.value,
    preset: refs.presetSelect.value,
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
  refs.presetSelect.value = params.preset || "cinematic-balanced";
  refs.durationInput.value = params.duration || 6;
  refs.variantCountInput.value = params.variants || 3;
  refs.aspectSelect.value = params.aspect_ratio || "16:9";
  refs.motionInput.value = params.motion_intensity || 6;
  refs.qualitySelect.value = params.quality_mode || "balanced";
  refs.negativeIntentInput.value = params.negative_intent || "";
}

function setGenerateEnabled() {
  const hasImage = Boolean(state.currentImageFile || state.currentImageUrl);
  const hasIntent = refs.intentInput.value.trim().length > 0;
  refs.generateButton.disabled = !(hasImage && hasIntent);
  refs.emptyStateCard.hidden = hasImage || hasIntent || state.runs.length > 0;
}

function setCurrentImage(file, dataUrl) {
  state.currentImageFile = file;
  state.currentImageName = file.name;
  state.currentImageUrl = dataUrl;
  refs.sourcePreview.src = dataUrl;
  refs.dropZone.classList.add("has-image");
  refs.dropZoneText.innerHTML = `<strong>${file.name}</strong><span>Ready for generation</span>`;
  setGenerateEnabled();
  announce("Source image uploaded.");
}

function attachUploadEvents() {
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

function currentRun() {
  return state.runs.find((run) => run.run_id === state.currentRunId) || null;
}

function toggleFavorite(runId, variantId) {
  const run = state.runs.find((entry) => entry.run_id === runId);
  if (!run) return;
  const variant = run.variants.find((entry) => entry.id === variantId);
  if (!variant) return;
  variant.favorite = !variant.favorite;
  saveRuns();
  if (state.currentRunId === runId) renderResults(run);
  renderHistory();
  renderFavorites();
}

function executionUrl(variant) {
  return (
    variant.execution?.result?.video_url ||
    variant.execution?.result?.output_url ||
    variant.execution?.result?.url ||
    null
  );
}

function metricValue(label, value) {
  if (value === null || value === undefined || value === "") return "";
  return `<span class="metric-badge">${label} ${value}</span>`;
}

function buildResultCard(run, variant) {
  const card = document.createElement("article");
  card.className = "result-card";
  const videoUrl = executionUrl(variant);
  const rulesApplied = variant.compiled_prompt?.cinematic_rules?.total_rules_applied;
  const temporalWeight = variant.compiled_prompt?.temporal_config?.temporal_weight;
  const seed = variant.model_parameters?.seed;
  const provider = variant.provider || "not configured";
  const status = variant.status || "unknown";

  card.innerHTML = `
    <div class="result-media">
      ${
        videoUrl
          ? `<video controls preload="metadata" src="${videoUrl}" aria-label="Generated video output for ${variant.label}"></video>`
          : run.source_image_data_url
            ? `<img src="${run.source_image_data_url}" alt="Source image preview for ${variant.label}" />`
            : `<span>No media URL</span>`
      }
    </div>
    <div class="result-body">
      <strong>${variant.label}</strong>
      <p>Provider: ${provider}</p>
      <div class="metric-row">
        ${metricValue("Status", status)}
        ${metricValue("Rules", rulesApplied)}
        ${metricValue("Temporal", temporalWeight)}
        ${metricValue("Seed", seed)}
      </div>
      <div class="result-actions-inline">
        <button class="btn-small ${variant.favorite ? "is-favorited" : ""}" data-favorite>
          ${variant.favorite ? "Favorited" : "Favorite"}
        </button>
        <button class="btn-small" data-rerun>Regenerate</button>
        ${
          videoUrl
            ? `<a class="btn-small" href="${videoUrl}" target="_blank" rel="noreferrer noopener">Open output</a>`
            : ""
        }
      </div>
      <label class="result-check">
        <input type="checkbox" data-compare ${state.selectedForCompare.has(variant.id) ? "checked" : ""} />
        Compare
      </label>
      ${
        variant.error
          ? `<p class="status failed">Error: ${variant.error}</p>`
          : ""
      }
    </div>
  `;

  card.querySelector("[data-favorite]").addEventListener("click", () => {
    toggleFavorite(run.run_id, variant.id);
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

  return card;
}

function renderResults(run) {
  refs.resultGrid.innerHTML = "";
  refs.comparePanel.hidden = true;
  state.selectedForCompare.clear();
  refs.openCompareButton.disabled = true;
  if (!run || !run.variants?.length) {
    refs.resultGrid.innerHTML = '<p class="list-card">No results yet.</p>';
    return;
  }
  run.variants.forEach((variant) => refs.resultGrid.appendChild(buildResultCard(run, variant)));
}

function renderComparePanel() {
  const selected = [];
  state.runs.forEach((run) => {
    run.variants.forEach((variant) => {
      if (state.selectedForCompare.has(variant.id)) {
        selected.push({ run, variant });
      }
    });
  });
  refs.compareGrid.innerHTML = "";
  selected.forEach(({ variant }) => {
    const panel = document.createElement("article");
    panel.className = "compare-card";
    panel.innerHTML = `
      <h4>${variant.label}</h4>
      <p>Status: ${variant.status}</p>
      <p>Provider: ${variant.provider || "not configured"}</p>
      <p>Rules applied: ${variant.compiled_prompt?.cinematic_rules?.total_rules_applied ?? "n/a"}</p>
      <p>Temporal weight: ${variant.compiled_prompt?.temporal_config?.temporal_weight ?? "n/a"}</p>
      ${
        executionUrl(variant)
          ? `<a href="${executionUrl(variant)}" target="_blank" rel="noreferrer noopener">Open generated output</a>`
          : "<p>No output URL returned.</p>"
      }
    `;
    refs.compareGrid.appendChild(panel);
  });
}

function renderTimeline() {
  refs.timelineList.innerHTML = "";
  if (state.pendingRun) {
    const row = document.createElement("article");
    row.className = "timeline-item";
    row.innerHTML = `
      <div>
        <strong>${state.pendingRun.intent.slice(0, 62)}${state.pendingRun.intent.length > 62 ? "..." : ""}</strong>
        <p>${formatDate(state.pendingRun.createdAt)} • ${state.pendingRun.params.preset}</p>
      </div>
      <div class="status running">running</div>
    `;
    refs.timelineList.appendChild(row);
  }

  if (!state.runs.length) {
    const empty = document.createElement("p");
    empty.className = "list-card";
    empty.textContent = "No generation runs yet.";
    refs.timelineList.appendChild(empty);
    return;
  }

  state.runs
    .slice()
    .reverse()
    .slice(0, 8)
    .forEach((run) => {
      const row = document.createElement("article");
      row.className = "timeline-item";
      row.innerHTML = `
        <div>
          <strong>${run.intent.slice(0, 62)}${run.intent.length > 62 ? "..." : ""}</strong>
          <p>${formatDate(run.created_at)} • ${run.params.preset}</p>
        </div>
        <div class="status ${run.status}">${run.status}</div>
      `;
      refs.timelineList.appendChild(row);
    });
}

function buildRunListCard(run) {
  const card = document.createElement("article");
  card.className = "list-card";
  card.innerHTML = `
    <strong>${run.intent.slice(0, 94)}${run.intent.length > 94 ? "..." : ""}</strong>
    <p>${formatDate(run.created_at)} • ${run.params.preset} • ${run.params.aspect_ratio}</p>
    <div class="metric-row">
      <span class="status ${run.status}">${run.status}</span>
      <span class="metric-badge">${run.variants.length} variants</span>
      <span class="metric-badge">Objects ${run.analysis?.object_count ?? 0}</span>
    </div>
    <div class="result-actions-inline">
      <button class="btn-small" data-open>Open</button>
      <button class="btn-small" data-rerun>One-click regenerate</button>
    </div>
  `;

  card.querySelector("[data-open]").addEventListener("click", () => {
    switchView("createView");
    state.currentRunId = run.run_id;
    refs.intentInput.value = run.intent;
    setCurrentParams(run.params);
    if (run.source_image_data_url) {
      state.currentImageUrl = run.source_image_data_url;
      state.currentImageFile = null;
      state.currentImageName = run.source_image?.filename || "history-image";
      refs.sourcePreview.src = run.source_image_data_url;
      refs.dropZone.classList.add("has-image");
      refs.dropZoneText.innerHTML = `<strong>${state.currentImageName}</strong><span>Loaded from history</span>`;
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
    refs.historyList.innerHTML = '<p class="list-card">No runs yet. Start in Create.</p>';
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
    run.variants.forEach((variant) => {
      if (variant.favorite) favorites.push({ run, variant });
    });
  });
  if (!favorites.length) {
    refs.favoritesList.innerHTML =
      '<p class="list-card">No favorites yet. Mark strong variants while reviewing results.</p>';
    return;
  }

  favorites
    .slice()
    .reverse()
    .forEach(({ run, variant }) => {
      const card = document.createElement("article");
      card.className = "list-card";
      card.innerHTML = `
        <strong>${variant.label}</strong>
        <p>${run.intent.slice(0, 84)}${run.intent.length > 84 ? "..." : ""}</p>
        <div class="metric-row">
          <span class="status ${variant.status}">${variant.status}</span>
          <span class="metric-badge">${variant.provider || "no provider"}</span>
        </div>
        <div class="result-actions-inline">
          <button class="btn-small" data-open>Open run</button>
          <button class="btn-small" data-rerun>Regenerate</button>
          <button class="btn-small is-favorited" data-unfav>Unfavorite</button>
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

async function loadProviders() {
  try {
    const response = await fetch("/api/providers");
    if (!response.ok) throw new Error("Provider endpoint unavailable.");
    const payload = await response.json();
    state.providerOptions = payload.available_providers || [];

    refs.providerSelect.innerHTML = '<option value="auto">Auto (best available)</option>';
    state.providerOptions.forEach((provider) => {
      const option = document.createElement("option");
      option.value = provider;
      option.textContent = provider;
      refs.providerSelect.appendChild(option);
    });
  } catch (error) {
    announce("Could not load provider capabilities.");
  }
}

function normalizeRun(payload, sourceImageDataUrl) {
  const run = {
    ...payload,
    source_image_data_url: sourceImageDataUrl,
    variants: (payload.variants || []).map((variant) => ({
      ...variant,
      favorite: variant.favorite || false,
    })),
  };
  return run;
}

async function executeGeneration({ imageFile, sourceImageDataUrl, intent, params }) {
  state.pendingRun = {
    createdAt: Date.now(),
    intent,
    params,
  };
  renderTimeline();
  createLoadingCards(params.variants);
  refs.runSummary.textContent = "Running backend sequence...";
  announce("Generation request sent to backend.");

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
    const response = await fetch("/api/sequences", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Backend generation failed.");
    }
    const run = normalizeRun(payload, sourceImageDataUrl);
    state.runs.push(run);
    state.currentRunId = run.run_id;
    saveRuns();
    renderResults(run);
    refs.runSummary.textContent = `Run ${run.run_id} • ${run.status} • provider ${run.params.provider || "none"}`;
    announce(`Generation finished with status: ${run.status}.`);
  } catch (error) {
    refs.resultGrid.innerHTML = `<p class="list-card">Generation failed: ${error.message}</p>`;
    refs.runSummary.textContent = "Generation failed";
    announce(`Generation failed: ${error.message}`);
  } finally {
    state.pendingRun = null;
    renderTimeline();
    renderHistory();
    renderFavorites();
  }
}

async function generateSequence() {
  const intent = refs.intentInput.value.trim();
  if (!intent) {
    announce("Intent is required.");
    return;
  }

  let imageFile = state.currentImageFile;
  if (!imageFile && state.currentImageUrl) {
    imageFile = dataUrlToFile(state.currentImageUrl, state.currentImageName || "source-image.jpg");
  }
  if (!imageFile) {
    announce("Upload an image before generation.");
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
  const imageDataUrl = run.source_image_data_url || state.currentImageUrl;
  if (!imageDataUrl) {
    announce("Cannot regenerate. Source image is unavailable.");
    return;
  }
  const imageFile = dataUrlToFile(imageDataUrl, run.source_image?.filename || "source-image.jpg");
  refs.intentInput.value = run.intent;
  setCurrentParams(run.params);
  switchView("createView");
  state.currentImageUrl = imageDataUrl;
  state.currentImageFile = imageFile;
  state.currentImageName = imageFile.name;
  refs.sourcePreview.src = imageDataUrl;
  refs.dropZone.classList.add("has-image");
  refs.dropZoneText.innerHTML = `<strong>${imageFile.name}</strong><span>Loaded for regeneration</span>`;
  setGenerateEnabled();

  await executeGeneration({
    imageFile,
    sourceImageDataUrl: imageDataUrl,
    intent: run.intent,
    params: run.params,
  });
}

function clearAllRuns() {
  state.runs = [];
  state.currentRunId = null;
  state.selectedForCompare.clear();
  state.pendingRun = null;
  refs.resultGrid.innerHTML = "";
  refs.compareGrid.innerHTML = "";
  refs.comparePanel.hidden = true;
  refs.runSummary.textContent = "No runs yet";
  saveRuns();
  renderTimeline();
  renderHistory();
  renderFavorites();
  announce("Timeline cleared.");
}

function attachEvents() {
  refs.navButtons.forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  refs.intentInput.addEventListener("input", setGenerateEnabled);
  refs.intentChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      refs.intentInput.value = chip.dataset.intent;
      setGenerateEnabled();
    });
  });

  refs.generateButton.addEventListener("click", () => {
    generateSequence();
  });

  refs.openCompareButton.addEventListener("click", () => {
    refs.comparePanel.hidden = false;
    renderComparePanel();
  });

  refs.closeCompareButton.addEventListener("click", () => {
    refs.comparePanel.hidden = true;
  });

  refs.clearTimelineButton.addEventListener("click", clearAllRuns);

  refs.toggleAdvancedButton.addEventListener("click", () => {
    const willExpand = refs.advancedPanel.hidden;
    refs.advancedPanel.hidden = !willExpand;
    refs.toggleAdvancedButton.textContent = willExpand ? "Hide advanced" : "Show advanced";
    refs.toggleAdvancedButton.setAttribute("aria-expanded", String(willExpand));
  });

  refs.reducedMotionToggle.addEventListener("change", () => {
    state.settings.reducedMotion = refs.reducedMotionToggle.checked;
    saveSettings();
  });

  refs.autoFavoriteToggle.addEventListener("change", () => {
    state.settings.autoFavoriteWinner = refs.autoFavoriteToggle.checked;
    saveSettings();
  });

  window.addEventListener("keydown", (event) => {
    const tag = document.activeElement?.tagName?.toLowerCase();
    const isTyping = tag === "textarea" || tag === "input";
    if (isTyping) return;
    if (event.key.toLowerCase() === "g" && !refs.generateButton.disabled) {
      generateSequence();
    }
    if (event.key.toLowerCase() === "c" && !refs.openCompareButton.disabled) {
      refs.comparePanel.hidden = false;
      renderComparePanel();
    }
    if (event.key.toLowerCase() === "r" && state.currentRunId) {
      rerunFromRun(state.currentRunId);
    }
  });
}

async function initialize() {
  loadRuns();
  loadSettings();
  refs.reducedMotionToggle.checked = state.settings.reducedMotion;
  refs.autoFavoriteToggle.checked = state.settings.autoFavoriteWinner;

  attachUploadEvents();
  attachEvents();
  await loadProviders();

  renderTimeline();
  renderHistory();
  renderFavorites();
  setGenerateEnabled();

  if (state.runs.length) {
    const latest = state.runs[state.runs.length - 1];
    state.currentRunId = latest.run_id;
    refs.runSummary.textContent = `Run ${latest.run_id} • ${latest.status}`;
  }
}

initialize();
