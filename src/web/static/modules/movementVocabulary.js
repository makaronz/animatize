// Movement Vocabulary (P5) — motion intensity as a six-segment film-grammar
// control. The hidden numeric <input id="motionInput"> remains the source of
// truth; segments write to it and dispatch input/change events.

let ctx = null;
let groupNode = null;
let descNode = null;
let previewTimer = null;

const SEGMENTS = [
  {
    key: "locked",
    label: "LOCKED",
    value: 1,
    description: "Locked off — tripod-still, zero drift",
    previewClass: null,
  },
  {
    key: "drift",
    label: "DRIFT",
    value: 3,
    description: "Drift — breathing camera, near-still",
    previewClass: "mv-preview-drift",
  },
  {
    key: "glide",
    label: "GLIDE",
    value: 5,
    description: "Steadicam glide — smooth, intentional",
    previewClass: "mv-preview-glide",
  },
  {
    key: "track",
    label: "TRACK",
    value: 6,
    description: "Tracking move — lateral travel with the subject",
    previewClass: "mv-preview-track",
  },
  {
    key: "push",
    label: "PUSH",
    value: 8,
    description: "Push-in — deliberate dolly toward the subject",
    previewClass: "mv-preview-push",
  },
  {
    key: "kinetic",
    label: "KINETIC",
    value: 10,
    description: "Kinetic — handheld energy, whip and surge",
    previewClass: "mv-preview-kinetic",
  },
];

const ALL_PREVIEW_CLASSES = SEGMENTS.map((segment) => segment.previewClass).filter(Boolean);

export function initMovementVocabulary(context) {
  ctx = context;
}

export function renderMovementVocabulary() {
  const { refs } = ctx;
  const host = refs.movementSegments;
  if (!host) return;

  refs.motionInput.hidden = true;

  host.className = "movement-vocab";
  host.innerHTML = "";

  const group = document.createElement("div");
  group.className = "movement-segments";
  group.setAttribute("role", "radiogroup");
  group.setAttribute("aria-label", "Movement vocabulary");

  SEGMENTS.forEach((segment) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "movement-segment";
    button.setAttribute("role", "radio");
    button.setAttribute("aria-checked", "false");
    button.dataset.segment = segment.key;
    button.tabIndex = -1;
    button.textContent = segment.label;
    button.addEventListener("click", () => selectSegment(segment));
    button.addEventListener("mouseenter", () => playPreview(segment));
    button.addEventListener("focus", () => playPreview(segment));
    group.appendChild(button);
  });

  group.addEventListener("keydown", onGroupKeydown);

  const description = document.createElement("p");
  description.className = "movement-desc";
  description.setAttribute("aria-live", "polite");

  host.appendChild(group);
  host.appendChild(description);

  groupNode = group;
  descNode = description;
  syncMovementVocabulary();
}

export function syncMovementVocabulary() {
  if (!groupNode) return;
  const value = Number(ctx.refs.motionInput.value || 6);
  const activeIndex = nearestSegmentIndex(value);

  groupNode.querySelectorAll(".movement-segment").forEach((button, index) => {
    const isActive = index === activeIndex;
    button.setAttribute("aria-checked", String(isActive));
    button.classList.toggle("is-selected", isActive);
    button.tabIndex = isActive ? 0 : -1;
  });

  if (descNode) {
    const segment = SEGMENTS[activeIndex];
    descNode.textContent = `${segment.label}: ${segment.description}`;
  }
}

function nearestSegmentIndex(value) {
  let best = 0;
  let bestDelta = Infinity;
  SEGMENTS.forEach((segment, index) => {
    const delta = Math.abs(segment.value - value);
    if (delta < bestDelta) {
      bestDelta = delta;
      best = index;
    }
  });
  return best;
}

function selectSegment(segment) {
  const input = ctx.refs.motionInput;
  input.value = String(segment.value);
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new Event("change", { bubbles: true }));
  syncMovementVocabulary();
  playPreview(segment);
}

function playPreview(segment) {
  const { refs, hasSourceImage, isReducedMotion } = ctx;
  if (!segment.previewClass || !hasSourceImage() || isReducedMotion()) return;

  const target = refs.sourcePreview;
  clearTimeout(previewTimer);
  target.classList.remove(...ALL_PREVIEW_CLASSES);
  // Force a reflow so re-hovering the same segment restarts the animation.
  void target.offsetWidth;
  target.classList.add(segment.previewClass);
  previewTimer = setTimeout(() => {
    target.classList.remove(segment.previewClass);
  }, 1200);
}

function onGroupKeydown(event) {
  const keys = ["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"];
  if (!keys.includes(event.key)) return;
  event.preventDefault();

  const current = nearestSegmentIndex(Number(ctx.refs.motionInput.value || 6));
  let next = current;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") {
    next = (current + 1) % SEGMENTS.length;
  } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
    next = (current - 1 + SEGMENTS.length) % SEGMENTS.length;
  } else if (event.key === "Home") {
    next = 0;
  } else {
    next = SEGMENTS.length - 1;
  }

  selectSegment(SEGMENTS[next]);
  groupNode.querySelectorAll(".movement-segment")[next]?.focus();
}
