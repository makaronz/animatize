// Dailies Room (P1/U1) — live pipeline screening while a take renders.
// Attempts async SSE generation first; reports back so app.js can fall back
// to the classic synchronous flow transparently when the backend is older
// or the dailies feed never comes up.

let ctx = null;

const STAGE_STEPS = [
  { key: "scene_analysis", label: "Scene Analysis" },
  { key: "prompt_compile", label: "Prompt Compile" },
  { key: "render", label: "Rendering" },
  { key: "qc", label: "QC" },
];

const STATE_GLYPHS = {
  pending: "○",
  active: "◐",
  done: "●",
  failed: "✕",
};

export function initDailiesRoom(context) {
  ctx = context;
}

/**
 * Try the async generation contract.
 * Resolves with one of:
 *   { mode: "async-complete", run }           — SSE `done` delivered the run payload
 *   { mode: "sync-response", response, payload } — POST answered non-202 (older backend / sync result)
 *   { mode: "retry-sync" }                    — 202 received but the stream died before any stage event
 * Rejects with an Error (AbortError name for cut/timeout, `code` preserved from server errors).
 */
export async function attemptAsyncGeneration({ formData, params, sourceImageDataUrl, signal }) {
  formData.append("async_mode", "1");
  let response;
  try {
    response = await fetch("/api/sequences", {
      method: "POST",
      credentials: "same-origin",
      body: formData,
      signal,
    });
  } finally {
    // Keep the FormData reusable for the synchronous fallback.
    formData.delete("async_mode");
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (response.status !== 202) {
    return { mode: "sync-response", response, payload };
  }

  if (!payload?.run_id) {
    return { mode: "retry-sync" };
  }

  const runId = payload.run_id;
  const streamUrl = payload.stream_url || `/api/sequences/${encodeURIComponent(runId)}/events`;
  return watchDailies({ runId, streamUrl, params, sourceImageDataUrl, signal });
}

function requestCancel(runId) {
  fetch(`/api/sequences/${encodeURIComponent(runId)}/cancel`, {
    method: "POST",
    credentials: "same-origin",
  }).catch(() => {});
}

function parseEventData(event) {
  if (typeof event.data !== "string") return null;
  try {
    return JSON.parse(event.data);
  } catch {
    return null;
  }
}

function watchDailies({ runId, streamUrl, params, sourceImageDataUrl, signal }) {
  return new Promise((resolve, reject) => {
    const room = renderRoom({ params, sourceImageDataUrl });
    const source = new EventSource(streamUrl);
    let settled = false;
    let sawStage = false;

    const cleanup = () => {
      source.close();
      signal.removeEventListener("abort", onAbort);
      room.element.remove();
    };

    const settle = (finish, value) => {
      if (settled) return;
      settled = true;
      cleanup();
      finish(value);
    };

    const onAbort = () => {
      requestCancel(runId);
      const error = new Error("Take cut.");
      error.name = "AbortError";
      error.code = "cancelled";
      settle(reject, error);
    };

    if (signal.aborted) {
      onAbort();
      return;
    }
    signal.addEventListener("abort", onAbort);

    source.addEventListener("stage", (event) => {
      const data = parseEventData(event);
      if (!data) return;
      sawStage = true;
      room.applyStage(data);
    });

    source.addEventListener("done", (event) => {
      const run = parseEventData(event);
      if (!run) {
        settle(reject, new Error("Dailies stream finished without a printable take."));
        return;
      }
      settle(resolve, { mode: "async-complete", run });
    });

    source.addEventListener("error", (event) => {
      // Named `event: error` frames carry data; raw connection failures do not.
      if (typeof event.data === "string") {
        const info = parseEventData(event) || {};
        const error = new Error(info.message || "Generation failed.");
        if (info.code) error.code = info.code;
        settle(reject, error);
        return;
      }
      if (!sawStage) {
        // Feed never came up — let app.js replay the synchronous flow.
        settle(resolve, { mode: "retry-sync" });
        return;
      }
      if (source.readyState === EventSource.CLOSED) {
        settle(reject, new Error("Dailies feed went dark mid-take. The projector lost signal."));
        return;
      }
      // EventSource is retrying on its own; keep the room open.
      room.setDetail("Signal dropped — re-syncing the dailies feed...");
    });
  });
}

function renderRoom({ params, sourceImageDataUrl }) {
  const { refs, PROVIDER_META, sanitize, cutActiveGeneration } = ctx;

  const meta = PROVIDER_META[params.provider];
  const providerLabel = meta
    ? meta.label
    : params.provider === "auto"
      ? "Auto (best available)"
      : params.provider;
  const waitText = meta ? ` • Est. ~${meta.estSeconds}s` : "";

  const element = document.createElement("section");
  element.className = "dailies-room";
  element.setAttribute("aria-label", "Dailies room — live take progress");

  const trackerMarkup = STAGE_STEPS.map(
    (step) => `
      <div class="dailies-step" data-step="${step.key}" data-state="pending">
        <span class="dailies-step-glyph" aria-hidden="true">${STATE_GLYPHS.pending}</span>
        <span class="dailies-step-label">${sanitize(step.label)}</span>
      </div>
    `,
  ).join('<span class="dailies-step-link" aria-hidden="true"></span>');

  element.innerHTML = `
    <div class="dailies-tracker" aria-label="Pipeline stages">${trackerMarkup}</div>
    <div class="dailies-progress" aria-hidden="true"><span class="dailies-progress-fill" data-progress></span></div>
    <div class="dailies-body">
      ${
        sourceImageDataUrl
          ? `<img class="dailies-thumb" src="${sanitize(sourceImageDataUrl)}" alt="Source frame" />`
          : ""
      }
      <p class="dailies-detail" data-detail>Queued in the screening room...</p>
    </div>
    <div class="dailies-footer">
      <span class="dailies-provider">Provider: ${sanitize(providerLabel)}${sanitize(waitText)}</span>
      <button class="btn btn-danger dailies-cut" type="button" aria-label="Cut the current take">Cut</button>
    </div>
  `;

  element.querySelector(".dailies-cut").addEventListener("click", () => cutActiveGeneration());

  refs.resultGrid.innerHTML = "";
  refs.resultGrid.appendChild(element);
  refs.runSummary.textContent = "Dailies rolling...";

  const detailNode = element.querySelector("[data-detail]");
  const progressNode = element.querySelector("[data-progress]");

  // textContent assignment keeps arbitrary backend detail strings inert.
  const setDetail = (text) => {
    detailNode.textContent = String(text ?? "");
  };

  const applyStage = (data) => {
    if (data.detail) {
      setDetail(data.detail);
    }
    if (typeof data.progress === "number" && Number.isFinite(data.progress)) {
      const clamped = Math.max(0, Math.min(1, data.progress));
      progressNode.style.width = `${(clamped * 100).toFixed(1)}%`;
    }

    const stageKey = String(data.stage || "");
    const step = element.querySelector(`[data-step="${CSS.escape(stageKey)}"]`);
    if (!step) return; // e.g. "queued" has no tracker slot

    if (data.status === "failed") {
      setStepState(step, "failed");
      return;
    }
    setStepState(step, data.status === "completed" ? "done" : "active");

    // Any earlier step that never reported completion is done once a later stage runs.
    for (const node of element.querySelectorAll(".dailies-step")) {
      if (node === step) break;
      if (node.dataset.state !== "done") setStepState(node, "done");
    }
  };

  return { element, setDetail, applyStage };
}

function setStepState(node, stepState) {
  node.dataset.state = stepState;
  const glyph = node.querySelector(".dailies-step-glyph");
  if (glyph) glyph.textContent = STATE_GLYPHS[stepState] || STATE_GLYPHS.pending;
}
