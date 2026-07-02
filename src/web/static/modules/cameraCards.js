// Camera Cards (P4) — the provider picker rendered as camera spec cards.
// The hidden <select id="providerSelect"> stays in the DOM as the source of
// truth: cards set its value and dispatch `change` so existing listeners
// (cost preview, params collection) keep working untouched.

let ctx = null;
let groupNode = null;

export function initCameraCards(context) {
  ctx = context;
}

export function renderCameraCards(providers) {
  const { refs } = ctx;
  const host = refs.providerCards;
  if (!host) return;

  refs.providerSelect.hidden = true;

  host.className = "camera-cards";
  host.setAttribute("role", "radiogroup");
  host.setAttribute("aria-label", "Provider camera cards");
  host.innerHTML = "";

  host.appendChild(buildAutoCard());
  (providers || []).forEach((provider) => {
    host.appendChild(buildProviderCard(provider));
  });

  groupNode = host;
  if (!host.dataset.ccBound) {
    host.dataset.ccBound = "true";
    host.addEventListener("keydown", onGroupKeydown);
  }
  syncCameraCards();
}

export function syncCameraCards(options = {}) {
  if (!groupNode) return;
  const current = ctx.refs.providerSelect.value || "auto";
  let selectedCard = null;

  groupNode.querySelectorAll("[role='radio']").forEach((card) => {
    const isSelected = card.dataset.providerId === current;
    card.setAttribute("aria-checked", String(isSelected));
    card.classList.toggle("is-selected", isSelected);
    card.tabIndex = isSelected && !card.disabled ? 0 : -1;
    if (isSelected) selectedCard = card;
  });

  if (!selectedCard) {
    const first = groupNode.querySelector("[role='radio']:not(:disabled)");
    if (first) first.tabIndex = 0;
  }
  if (options.focus && selectedCard) {
    selectedCard.focus();
  }
}

function buildCardShell(providerId) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "camera-card";
  card.setAttribute("role", "radio");
  card.setAttribute("aria-checked", "false");
  card.dataset.providerId = providerId;
  card.tabIndex = -1;
  card.addEventListener("click", () => selectProvider(providerId));
  return card;
}

function buildAutoCard() {
  const card = buildCardShell("auto");
  card.innerHTML = `
    <strong class="camera-card-name">Auto</strong>
    <div class="camera-card-specs"><span>Best available lens</span></div>
    <div class="camera-card-tags"><span class="badge">Routes per preset</span></div>
  `;
  return card;
}

function buildProviderCard(provider) {
  const { sanitize } = ctx;
  const lifecycle = provider.lifecycle || {};
  const supported = provider.supported !== false;
  const configured = Boolean(provider.configured);

  const card = buildCardShell(provider.id);

  if (!supported) {
    card.classList.add("is-disabled");
    card.setAttribute("aria-disabled", "true");
    card.disabled = true;
  } else if (!configured) {
    card.classList.add("is-unconfigured");
  }

  let ribbon = "";
  if (lifecycle.status === "deprecated") {
    ribbon = `<span class="camera-card-ribbon is-eol">⚠️ ${sanitize(lifecycle.note || "Deprecated")}</span>`;
  } else if (lifecycle.status === "migration_recommended") {
    ribbon = `<span class="camera-card-ribbon is-migrate">Migrate soon</span>`;
  }

  const cost = Number(provider.est_cost_per_second);
  const wait = Number(provider.est_wait_seconds);
  const maxDuration = Number(provider.max_duration);

  card.innerHTML = `
    ${ribbon}
    <strong class="camera-card-name">${sanitize(provider.label || provider.id)}</strong>
    <div class="camera-card-specs">
      ${Number.isFinite(cost) ? `<span>~$${cost.toFixed(2)}/s</span>` : ""}
      ${Number.isFinite(wait) ? `<span>⏱ ~${wait}s</span>` : ""}
      ${Number.isFinite(maxDuration) && maxDuration > 0 ? `<span>max ${sanitize(maxDuration)}s</span>` : ""}
    </div>
    <div class="camera-card-tags">
      <span class="badge">${provider.supports_audio ? "Audio" : "Silent"}</span>
      ${!supported ? '<span class="badge">Coming soon</span>' : ""}
      ${supported && !configured ? '<span class="badge not_configured">Not configured</span>' : ""}
    </div>
  `;
  return card;
}

function selectProvider(providerId) {
  const select = ctx.refs.providerSelect;
  const hasOption = Array.from(select.options).some((option) => option.value === providerId);
  if (!hasOption) return;
  select.value = providerId;
  select.dispatchEvent(new Event("change", { bubbles: true }));
  syncCameraCards({ focus: true });
}

function onGroupKeydown(event) {
  const keys = ["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"];
  if (!keys.includes(event.key)) return;
  event.preventDefault();

  const cards = Array.from(groupNode.querySelectorAll("[role='radio']:not(:disabled)"));
  if (!cards.length) return;

  const active = document.activeElement?.closest?.("[role='radio']");
  let index = cards.indexOf(active);
  if (index < 0) {
    index = cards.findIndex((card) => card.getAttribute("aria-checked") === "true");
  }
  if (index < 0) index = 0;

  let next = index;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") {
    next = (index + 1) % cards.length;
  } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
    next = (index - 1 + cards.length) % cards.length;
  } else if (event.key === "Home") {
    next = 0;
  } else {
    next = cards.length - 1;
  }

  selectProvider(cards[next].dataset.providerId);
}
