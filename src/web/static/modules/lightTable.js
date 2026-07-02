// Light Table (P6/U5) — upgraded compare panel: synchronized playback,
// reviewer keys (1/2/3, F, Space, Esc) and auto-open after multi-variant runs.
// Selection still lives in state.selectedForCompare; result-card checkboxes
// stay the visible entry point.

let ctx = null;
let cards = []; // [{ run, variant, card, video }]
let selectedIndex = 0;
let transportToggle = null;

const LETTERS = ["A", "B", "C"];

export function initLightTable(context) {
  ctx = context;
  window.addEventListener("keydown", onReviewerKeys);
}

export function isLightTableOpen() {
  return Boolean(ctx && !ctx.refs.comparePanel.hidden);
}

export function openLightTable(options = {}) {
  const { refs } = ctx;
  const selection = collectSelection();
  if (!selection.length) return;

  buildPanel(selection);
  refs.comparePanel.hidden = false;
  if (options.focus) {
    refs.comparePanel.focus();
  }
}

export function closeLightTable() {
  const { refs } = ctx;
  if (refs.comparePanel.hidden) return;
  cards.forEach((entry) => entry.video?.pause());
  transportToggle = null;
  refs.comparePanel.hidden = true;
  refs.openCompareButton?.focus();
}

export function maybeAutoOpenLightTable(run) {
  const { state, refs } = ctx;
  if (state.settings.preferences.autoOpenCompare === false) return;
  const variants = run?.variants || [];
  if (variants.length < 2) return;

  state.selectedForCompare.clear();
  variants.slice(0, 3).forEach((variant) => state.selectedForCompare.add(variant.id));

  // Result cards were just rendered for this run; tick their compare boxes in order.
  refs.resultGrid.querySelectorAll("[data-compare]").forEach((checkbox, index) => {
    checkbox.checked = index < 3;
  });
  refs.openCompareButton.disabled = state.selectedForCompare.size < 2;

  openLightTable();
  ctx.announce("Light table opened — press 1, 2 or 3 to pick a take.");
}

function collectSelection() {
  const { state } = ctx;
  const picked = [];
  state.runs.forEach((run) => {
    (run.variants || []).forEach((variant) => {
      if (state.selectedForCompare.has(variant.id)) {
        picked.push({ run, variant });
      }
    });
  });
  return picked.slice(0, 3);
}

function buildPanel(selection) {
  const { refs } = ctx;
  refs.compareGrid.innerHTML = "";
  cards = selection.map((entry, index) => {
    const card = buildCard(entry, index);
    refs.compareGrid.appendChild(card);
    return { ...entry, card, video: card.querySelector("[data-lt-video]") };
  });
  buildTransport();
  selectCard(0);
}

function buildCard(entry, index) {
  const { sanitize, executionUrl } = ctx;
  const { run, variant } = entry;
  const url = executionUrl(variant);
  const isVideo = Boolean(url) && !/\.(png|jpe?g|gif|webp)(\?|$)/i.test(url);
  const letter = LETTERS[index] || String(index + 1);

  const card = document.createElement("article");
  card.className = "compare-card light-table-card";
  card.dataset.index = String(index);
  card.innerHTML = `
    <div class="light-table-head">
      <span class="light-table-letter" aria-hidden="true">${letter}</span>
      <strong>${sanitize(variant.label)}</strong>
      <span class="badge light-table-fav ${variant.favorite ? "is-on" : ""}" data-lt-fav aria-hidden="true">★</span>
    </div>
    <div class="light-table-media">
      ${
        isVideo
          ? `<video data-lt-video preload="metadata" muted playsinline src="${sanitize(url)}" aria-label="Take ${letter} output"></video>`
          : url
            ? `<img src="${sanitize(url)}" alt="Output for ${sanitize(variant.label)}" />`
            : run.source_image_data_url
              ? `<img src="${sanitize(run.source_image_data_url)}" alt="Source preview for ${sanitize(variant.label)}" />`
              : "<span>No output</span>"
      }
    </div>
    <p>Status: ${sanitize(variant.status)} • Provider: ${sanitize(variant.provider || "n/a")}</p>
    <p>Temporal weight: ${sanitize(variant.compiled_prompt?.temporal_config?.temporal_weight ?? "n/a")}</p>
    <div class="action-row">
      <button class="btn-small" type="button" data-lt-winner>Select as winner</button>
      <button class="btn-small ${variant.favorite ? "is-favorited" : ""}" type="button" data-lt-favorite>
        ${variant.favorite ? "Unfavorite" : "Favorite"}
      </button>
      ${url ? `<a class="btn-small" href="${sanitize(url)}" target="_blank" rel="noreferrer noopener">Open output</a>` : ""}
    </div>
  `;

  card.addEventListener("click", () => selectCard(index));

  card.querySelector("[data-lt-winner]").addEventListener("click", async (event) => {
    event.stopPropagation();
    if (ctx.state.settings.preferences.autoFavoriteWinner && !variant.favorite) {
      await toggleEntryFavorite(index, { silent: true });
    }
    ctx.announce(`${variant.label} marked as winner.`);
  });

  card.querySelector("[data-lt-favorite]").addEventListener("click", (event) => {
    event.stopPropagation();
    toggleEntryFavorite(index);
  });

  return card;
}

async function toggleEntryFavorite(index, options = {}) {
  const entry = cards[index];
  if (!entry) return;
  // toggleFavorite mutates the same variant object held in state.runs and
  // re-renders the result grid while app.js preserves the open panel.
  await ctx.toggleFavorite(entry.run.run_id, entry.variant.id);

  const isFavorite = Boolean(entry.variant.favorite);
  entry.card.querySelector("[data-lt-fav]")?.classList.toggle("is-on", isFavorite);
  const button = entry.card.querySelector("[data-lt-favorite]");
  if (button) {
    button.textContent = isFavorite ? "Unfavorite" : "Favorite";
    button.classList.toggle("is-favorited", isFavorite);
  }
  if (!options.silent) {
    ctx.announce(isFavorite ? `${entry.variant.label} favorited.` : `${entry.variant.label} unfavorited.`);
  }
}

function selectCard(index) {
  const entry = cards[index];
  if (!entry) return;
  selectedIndex = index;
  cards.forEach((item, i) => {
    item.card.classList.toggle("is-selected", i === index);
    // Only the selected take carries audio during synced playback.
    if (item.video) item.video.muted = i !== index;
  });
}

function buildTransport() {
  const host = ctx.refs.lightTableTransport;
  transportToggle = null;
  if (!host) return;

  const videos = cards.map((entry) => entry.video).filter(Boolean);
  host.innerHTML = "";
  if (!videos.length) {
    host.hidden = true;
    return;
  }
  host.hidden = false;
  host.innerHTML = `
    <button class="btn-small" type="button" data-lt-play aria-label="Play or pause all takes">▶ Roll</button>
    <input type="range" data-lt-scrub min="0" max="1000" value="0" step="1" aria-label="Scrub all takes" />
    <span class="light-table-time" data-lt-time>0.0s</span>
  `;

  const playButton = host.querySelector("[data-lt-play]");
  const scrub = host.querySelector("[data-lt-scrub]");
  const timeNode = host.querySelector("[data-lt-time]");
  const master = videos[0];
  let scrubbing = false;
  let playing = false;

  const maxDuration = () =>
    videos.reduce((max, video) => (Number.isFinite(video.duration) ? Math.max(max, video.duration) : max), 0);

  const setPlaying = (next) => {
    playing = next;
    playButton.textContent = playing ? "❚❚ Hold" : "▶ Roll";
    videos.forEach((video) => {
      if (playing) video.play().catch(() => {});
      else video.pause();
    });
  };
  transportToggle = () => setPlaying(!playing);

  playButton.addEventListener("click", () => setPlaying(!playing));

  const seekTo = (fraction) => {
    const duration = maxDuration();
    if (!duration) return;
    const target = fraction * duration;
    videos.forEach((video) => {
      const limit = Number.isFinite(video.duration) ? video.duration : duration;
      video.currentTime = Math.min(target, Math.max(0, limit - 0.05));
    });
    timeNode.textContent = `${target.toFixed(1)}s`;
  };

  scrub.addEventListener("input", () => {
    scrubbing = true;
    seekTo(Number(scrub.value) / 1000);
  });
  scrub.addEventListener("change", () => {
    scrubbing = false;
  });

  master.addEventListener("timeupdate", () => {
    const duration = maxDuration();
    if (!duration) return;
    if (!scrubbing) {
      scrub.value = String(Math.round((master.currentTime / duration) * 1000));
      timeNode.textContent = `${master.currentTime.toFixed(1)}s`;
    }
    if (playing) {
      videos.forEach((video) => {
        if (video === master) return;
        if (Math.abs(video.currentTime - master.currentTime) > 0.3) {
          video.currentTime = master.currentTime;
        }
      });
    }
  });

  master.addEventListener("ended", () => setPlaying(false));
}

function onReviewerKeys(event) {
  if (!isLightTableOpen()) return;
  const tag = document.activeElement?.tagName?.toLowerCase();
  if (tag === "input" || tag === "textarea" || tag === "select") return;

  if (event.key === "1" || event.key === "2" || event.key === "3") {
    const index = Number(event.key) - 1;
    if (cards[index]) {
      selectCard(index);
      ctx.announce(`Take ${LETTERS[index]} selected.`);
    }
    return;
  }

  if (event.key === "f" || event.key === "F") {
    toggleEntryFavorite(selectedIndex);
    return;
  }

  if (event.key === " " || event.code === "Space") {
    event.preventDefault();
    transportToggle?.();
    return;
  }

  if (event.key === "Escape") {
    closeLightTable();
  }
}
