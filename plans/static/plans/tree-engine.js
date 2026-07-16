/**
 * tree-engine.js — Living Progress Tree
 *
 * A deterministic, procedurally-grown fractal tree that represents personal growth.
 *
 * Model: a stochastic L-system (F → F[+F]F[-F]F with randomized parameters) is
 * "compiled" once into an explicit branch skeleton, seeded by the user's id.
 * Progress (completedActions) maps to a maturity scalar M ∈ [0,1]; every branch,
 * leaf and blossom owns a window in maturity-space [growStart, growStart+growDur]
 * and animates from its base as M passes through that window. The rendered M
 * eases toward the target M in real time, so each new action produces a slow,
 * visible unfurling rather than a jump.
 *
 * Framework-agnostic: give it a 2D canvas context and call tick()/render().
 */

// ---------------------------------------------------------------------------
// Deterministic randomness
// ---------------------------------------------------------------------------

export function hashString(str) {
  // FNV-1a 32-bit
  let h = 0x811c9dc5;
  const s = String(str);
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------------------------------------------------------------------------
// Progress → maturity mapping
// ---------------------------------------------------------------------------

const FULL_MATURITY_ACTIONS = 365;

/** Logarithmic maturity: fast early feedback, months to reach magnificence. */
export function maturityFromActions(actions) {
  const a = Math.max(0, actions);
  return Math.min(1, Math.log(1 + a) / Math.log(1 + FULL_MATURITY_ACTIONS));
}

export const GROWTH_STAGES = [
  { minActions: 0,   label: 'A seed rests underground' },
  { minActions: 1,   label: 'Roots are reaching down' },
  { minActions: 3,   label: 'A tiny stem has emerged' },
  { minActions: 7,   label: 'The trunk is rising' },
  { minActions: 14,  label: 'First branches are spreading' },
  { minActions: 30,  label: 'A young tree, branching freely' },
  { minActions: 60,  label: 'Fine twigs are filling the crown' },
  { minActions: 100, label: 'The crown is full of leaves' },
  { minActions: 200, label: 'An old tree — blossoming' },
];

export function growthStage(actions) {
  let level = 0;
  for (let i = 0; i < GROWTH_STAGES.length; i++) {
    if (actions >= GROWTH_STAGES[i].minActions) level = i;
  }
  return { level, label: GROWTH_STAGES[level].label };
}

// ---------------------------------------------------------------------------
// Palettes (calm, warm, botanical-watercolor)
// ---------------------------------------------------------------------------

const SEASONS = {
  spring: { leaves: ['#9fbf6b', '#b5cf7e', '#8ab35e', '#c8dc95'], newLeaf: '#d3e4a4', blossom: '#f2d7dc' },
  summer: { leaves: ['#6f9a52', '#83a95f', '#5d8a48', '#96b573'], newLeaf: '#b6cf8e', blossom: '#f0e3c8' },
  autumn: { leaves: ['#c98f3d', '#b9772f', '#d4a755', '#a86a2e'], newLeaf: '#ddb968', blossom: '#e8c9a0' },
};

const TRUNK_DARK = { r: 0x6b, g: 0x4f, b: 0x3a };  // warm brown
const TRUNK_LIGHT = { r: 0x9a, g: 0x7b, b: 0x5f }; // lighter twigs

function trunkColor(depth, maxDepth, alpha = 1) {
  const t = Math.min(1, depth / maxDepth);
  const r = Math.round(TRUNK_DARK.r + (TRUNK_LIGHT.r - TRUNK_DARK.r) * t);
  const g = Math.round(TRUNK_DARK.g + (TRUNK_LIGHT.g - TRUNK_DARK.g) * t);
  const b = Math.round(TRUNK_DARK.b + (TRUNK_LIGHT.b - TRUNK_DARK.b) * t);
  return `rgba(${r},${g},${b},${alpha})`;
}

// ---------------------------------------------------------------------------
// Personality → generation parameters
// ---------------------------------------------------------------------------

const PERSONALITIES = {
  balanced:  { heightScale: 1.00, spreadScale: 1.00, angleNoise: 1.00, curvature: 1.0 },
  calm:      { heightScale: 0.88, spreadScale: 1.25, angleNoise: 0.75, curvature: 0.8 },
  energetic: { heightScale: 1.18, spreadScale: 0.85, angleNoise: 1.10, curvature: 1.0 },
  creative:  { heightScale: 1.00, spreadScale: 1.10, angleNoise: 1.60, curvature: 1.6 },
};

// Maturity-space schedule per branch depth: [earliest start, start jitter, grow duration]
const DEPTH_SCHEDULE = [
  [0.10, 0.00, 0.22], // trunk
  [0.30, 0.08, 0.15], // primary branches
  [0.44, 0.10, 0.14], // secondary
  [0.56, 0.10, 0.13], // tertiary
  [0.66, 0.12, 0.12], // twigs
  [0.76, 0.12, 0.10], // fine twigs
];
const MAX_DEPTH = DEPTH_SCHEDULE.length - 1;

// ---------------------------------------------------------------------------
// Geometry helpers — every branch is a quadratic Bézier
// ---------------------------------------------------------------------------

function bezierPoint(p0x, p0y, cx, cy, p2x, p2y, u) {
  const v = 1 - u;
  return [
    v * v * p0x + 2 * v * u * cx + u * u * p2x,
    v * v * p0y + 2 * v * u * cy + u * u * p2y,
  ];
}

function bezierTangent(p0x, p0y, cx, cy, p2x, p2y, u) {
  const dx = 2 * (1 - u) * (cx - p0x) + 2 * u * (p2x - cx);
  const dy = 2 * (1 - u) * (cy - p0y) + 2 * u * (p2y - cy);
  return Math.atan2(dy, dx);
}

const clamp01 = (x) => (x < 0 ? 0 : x > 1 ? 1 : x);
const easeOut = (x) => 1 - Math.pow(1 - x, 3);

// ---------------------------------------------------------------------------
// The tree
// ---------------------------------------------------------------------------

export class ProgressTree {
  /**
   * @param {object} opts
   * @param {string} opts.userId        deterministic seed — same user, same tree
   * @param {string} [opts.personality] balanced | calm | energetic | creative
   * @param {string} [opts.season]      spring | summer | autumn
   * @param {number} [opts.completedActions]
   */
  constructor({ userId, personality = 'balanced', season = 'summer', completedActions = 0 }) {
    this.userId = userId;
    this.personality = PERSONALITIES[personality] ? personality : 'balanced';
    this.season = SEASONS[season] ? season : 'summer';

    this.targetM = maturityFromActions(completedActions);
    this.displayedM = this.targetM; // first paint shows the persisted tree instantly
    this.completedActions = completedActions;

    this.time = 0;          // seconds, drives wind
    this.windStrength = 1;  // baseline sway
    this.gust = 0;          // decaying boost when an action completes

    this.generate();
  }

  // -- Structure generation (runs once; topology never changes) --------------

  generate() {
    const rng = mulberry32(hashString(this.userId));
    const P = PERSONALITIES[this.personality];

    this.trunk = this.growBranch(rng, P, {
      depth: 0,
      angle: -Math.PI / 2 + (rng() - 0.5) * 0.10, // slight natural lean
      length: 1.0,                                 // normalized; scaled at render
      width: 1.0,
      attachT: 0,
      growStart: DEPTH_SCHEDULE[0][0],
      side: rng() < 0.5 ? -1 : 1,
    });

    // Root system: small mirrored branches below ground, revealed first
    this.rootBranches = [];
    const rootCount = 3 + Math.floor(rng() * 2);
    for (let i = 0; i < rootCount; i++) {
      const spread = (i / (rootCount - 1)) * 2 - 1; // -1..1
      this.rootBranches.push({
        angle: Math.PI / 2 + spread * (0.9 + rng() * 0.3),
        length: 0.16 + rng() * 0.12,
        curve: (rng() - 0.5) * 0.8,
        growStart: 0.02 + rng() * 0.04,
        growDur: 0.08,
      });
    }

    // Count nodes for perf budget awareness
    let count = 0;
    const walk = (b) => { count++; b.children.forEach(walk); };
    walk(this.trunk);
    this.branchCount = count;
  }

  growBranch(rng, P, cfg) {
    const { depth } = cfg;
    const [stageStart, jitter, dur] = DEPTH_SCHEDULE[depth];
    // A branch may not start growing before its parent has reached its attach point.
    const growStart = Math.max(cfg.growStart, stageStart + rng() * jitter);

    const branch = {
      depth,
      angle: cfg.angle,           // relative to parent tangent at attach point
      length: cfg.length,
      width: cfg.width,
      attachT: cfg.attachT,
      curve: (rng() - 0.5) * 0.5 * P.curvature, // built-in bend, per-branch
      growStart,
      growDur: dur,
      swayPhase: rng() * Math.PI * 2,
      swayFreq: 0.7 + rng() * 0.7,
      side: cfg.side,
      children: [],
      leaves: [],
      blossom: null,
    };

    if (depth < MAX_DEPTH) {
      const childStartFor = (t) => growStart + dur * t;

      // Tip split: 2 (sometimes 3) continuations — deliberately asymmetric
      const splitLeft = 0.25 + rng() * 0.35;   // left magnitude
      const splitRight = 0.25 + rng() * 0.35;  // right magnitude, drawn independently
      const tipAngles = [-splitLeft, splitRight];
      if (rng() < 0.35 && depth < 3) tipAngles.push((rng() - 0.5) * 0.2); // middle shoot
      for (const a of tipAngles) {
        branch.children.push(this.growBranch(rng, P, {
          depth: depth + 1,
          angle: a * P.spreadScale + (rng() - 0.5) * 0.25 * P.angleNoise,
          length: cfg.length * (0.62 + rng() * 0.18), // 62–80% of parent
          width: cfg.width * 0.65,                     // thickness decay
          attachT: 1.0,
          growStart: childStartFor(1.0),
          side: a < 0 ? -1 : 1,
        }));
      }

      // Side branches along the limb (30–60% length): alternate sides w/ jitter
      const sideCount = depth === 0 ? 2 + Math.floor(rng() * 2) : (rng() < 0.6 ? 1 : 0);
      let side = rng() < 0.5 ? -1 : 1;
      for (let i = 0; i < sideCount; i++) {
        const t = 0.35 + rng() * 0.55;
        branch.children.push(this.growBranch(rng, P, {
          depth: depth + 1,
          angle: side * (0.55 + rng() * 0.45) * P.spreadScale + (rng() - 0.5) * 0.3 * P.angleNoise,
          length: cfg.length * (0.30 + rng() * 0.30), // 30–60%
          width: cfg.width * 0.55,
          attachT: t,
          growStart: childStartFor(t),
          side,
        }));
        side = -side;
      }
    }

    // Leaves live on the outer twigs
    if (depth >= 3) {
      const leafCount = depth >= 4 ? 2 + Math.floor(rng() * 3) : 1 + Math.floor(rng() * 2);
      for (let i = 0; i < leafCount; i++) {
        branch.leaves.push({
          t: 0.35 + rng() * 0.65,
          side: rng() < 0.5 ? -1 : 1,
          size: 0.7 + rng() * 0.6,
          angleOffset: 0.5 + rng() * 0.7,
          shade: Math.floor(rng() * 4),
          revealAt: 0.50 + rng() * 0.45, // leaves keep arriving for months
          flutterPhase: rng() * Math.PI * 2,
        });
      }
      // Some twig tips earn a blossom in late maturity
      if (depth >= 4 && rng() < 0.30) {
        branch.blossom = { revealAt: 0.85 + rng() * 0.13, size: 0.8 + rng() * 0.5, phase: rng() * Math.PI * 2 };
      }
    }

    return branch;
  }

  // -- Progress API -----------------------------------------------------------

  /** Set absolute progress (e.g. after loading persisted state). */
  setActions(n, { animate = true } = {}) {
    this.completedActions = Math.max(0, n);
    this.targetM = maturityFromActions(this.completedActions);
    if (!animate) this.displayedM = this.targetM;
  }

  /** The daily moment: one healthy action completed. */
  completeAction() {
    this.setActions(this.completedActions + 1);
    this.gust = 1; // gentle stir of the branches — the tree acknowledges you
  }

  // -- Per-frame update ---------------------------------------------------------

  tick(dtSeconds) {
    this.time += dtSeconds;
    // Ease displayed maturity toward target: new growth unfurls over ~3–4s
    const d = this.targetM - this.displayedM;
    if (Math.abs(d) > 1e-5) this.displayedM += d * Math.min(1, dtSeconds * 0.9);
    else this.displayedM = this.targetM;
    this.gust *= Math.pow(0.35, dtSeconds); // gust decays over ~2s
  }

  // -- Rendering ----------------------------------------------------------------

  render(ctx, w, h) {
    const M = this.displayedM;
    const groundY = h * 0.82;
    const baseX = w / 2;
    const unit = Math.min(h * 0.30, w * 0.34); // trunk full length in px
    const wind = (this.windStrength + this.gust * 2.5) * 0.012;

    ctx.clearRect(0, 0, w, h);

    this.drawGround(ctx, w, groundY);
    this.drawRoots(ctx, baseX, groundY, unit, M);
    this.drawSeed(ctx, baseX, groundY, M);

    const trunkP = this.progressOf(this.trunk, M);
    if (trunkP > 0) {
      this.drawBranch(ctx, this.trunk, baseX, groundY + 2, -Math.PI / 2, unit, h * 0.016, M, wind);
    }
  }

  progressOf(node, M) {
    return easeOut(clamp01((M - node.growStart) / node.growDur));
  }

  drawBranch(ctx, b, x0, y0, parentTangent, unitLen, unitWidth, M, wind) {
    const p = this.progressOf(b, M);
    if (p <= 0) return;

    // Wind: deeper (thinner) branches sway more; motion accumulates down the hierarchy
    const flex = Math.pow((b.depth + 1) / (MAX_DEPTH + 1), 2);
    const sway = wind * flex * (
      Math.sin(this.time * b.swayFreq + b.swayPhase) * 0.7 +
      Math.sin(this.time * b.swayFreq * 2.3 + b.swayPhase * 1.7) * 0.3
    ) * 40;

    const theta = (b.depth === 0 ? b.angle : parentTangent + b.angle) + sway;

    // Gravity: bend the branch tip toward the ground, more for thin outer limbs
    const droop = 0.22 * flex * Math.sin(theta + Math.PI / 2);
    const bend = b.curve + droop;

    const len = b.length * unitLen;
    const p0x = x0, p0y = y0;
    const cx = p0x + Math.cos(theta) * len * 0.5;
    const cy = p0y + Math.sin(theta) * len * 0.5;
    const p2x = cx + Math.cos(theta + bend) * len * 0.5;
    const p2y = cy + Math.sin(theta + bend) * len * 0.5;

    // Draw the grown portion [0, p] as tapered polyline segments
    const w0 = Math.max(0.6, b.width * unitWidth * (0.35 + 0.65 * p));
    const wTip = Math.max(0.4, w0 * 0.45);
    const SEGS = b.depth <= 1 ? 10 : 6;
    ctx.strokeStyle = trunkColor(b.depth, MAX_DEPTH);
    ctx.lineCap = 'round';
    let [px, py] = [p0x, p0y];
    for (let i = 1; i <= SEGS; i++) {
      const u = (i / SEGS) * p;
      const [qx, qy] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, u);
      ctx.lineWidth = w0 + (wTip - w0) * (i / SEGS);
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(qx, qy);
      ctx.stroke();
      px = qx; py = qy;
    }

    // Leaves (only where the branch has already grown past the leaf's node)
    for (const leaf of b.leaves) {
      if (leaf.t > p) continue;
      const lp = clamp01((M - leaf.revealAt) / 0.02);
      if (lp <= 0) continue;
      const [lx, ly] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, leaf.t);
      const tan = bezierTangent(p0x, p0y, cx, cy, p2x, p2y, leaf.t);
      this.drawLeaf(ctx, lx, ly, tan, leaf, easeOut(lp), M, unitLen);
    }

    // Blossom at twig tip, late maturity
    if (b.blossom && p >= 1) {
      const bp = clamp01((M - b.blossom.revealAt) / 0.03);
      if (bp > 0) this.drawBlossom(ctx, p2x, p2y, b.blossom, easeOut(bp), unitLen);
    }

    // Children — recurse from their attach point with the local tangent
    for (const child of b.children) {
      if (child.attachT > p) continue;
      const [ax, ay] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, child.attachT);
      const tan = bezierTangent(p0x, p0y, cx, cy, p2x, p2y, child.attachT);
      this.drawBranch(ctx, child, ax, ay, tan, unitLen, unitWidth, M, wind);
    }
  }

  drawLeaf(ctx, x, y, tangent, leaf, unfold, M, unitLen) {
    const pal = SEASONS[this.season];
    const age = M - leaf.revealAt; // young leaves are lighter
    const color = age < 0.06 ? pal.newLeaf : pal.leaves[leaf.shade];
    const flutter = Math.sin(this.time * 2.1 + leaf.flutterPhase) * 0.12 * (1 + this.gust * 2);
    const size = leaf.size * unitLen * 0.035 * unfold;
    const ang = tangent + leaf.side * leaf.angleOffset + flutter;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(ang);
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.88;
    ctx.beginPath();
    ctx.ellipse(size * 1.1, 0, size * 1.25, size * 0.55, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    ctx.globalAlpha = 1;
  }

  drawBlossom(ctx, x, y, blossom, open, unitLen) {
    const pal = SEASONS[this.season];
    const r = blossom.size * unitLen * 0.022 * open;
    const bob = Math.sin(this.time * 1.6 + blossom.phase) * r * 0.15;
    ctx.fillStyle = pal.blossom;
    ctx.globalAlpha = 0.9;
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + blossom.phase;
      ctx.beginPath();
      ctx.arc(x + Math.cos(a) * r * 0.7, y + bob + Math.sin(a) * r * 0.7, r * 0.55, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = '#e8b84b';
    ctx.beginPath();
    ctx.arc(x, y + bob, r * 0.3, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  drawRoots(ctx, baseX, groundY, unit, M) {
    ctx.strokeStyle = 'rgba(107,79,58,0.45)';
    ctx.lineCap = 'round';
    for (const r of this.rootBranches) {
      const p = easeOut(clamp01((M - r.growStart) / r.growDur));
      if (p <= 0) continue;
      const len = r.length * unit * p;
      const cx = baseX + Math.cos(r.angle) * len * 0.5;
      const cy = groundY + Math.sin(r.angle) * len * 0.5;
      const ex = cx + Math.cos(r.angle + r.curve) * len * 0.5;
      const ey = cy + Math.sin(r.angle + r.curve) * len * 0.5;
      ctx.lineWidth = Math.max(0.8, unit * 0.012 * p);
      ctx.beginPath();
      ctx.moveTo(baseX, groundY);
      ctx.quadraticCurveTo(cx, cy, ex, ey);
      ctx.stroke();
    }
  }

  drawSeed(ctx, baseX, groundY, M) {
    const alpha = clamp01(1 - M / 0.14); // the seed dissolves as the sprout takes over
    if (alpha <= 0) return;
    ctx.fillStyle = `rgba(94,70,50,${alpha})`;
    ctx.beginPath();
    ctx.ellipse(baseX, groundY + 9, 4.5, 6.5, 0.3, 0, Math.PI * 2);
    ctx.fill();
  }

  drawGround(ctx, w, groundY) {
    // Soft watercolor soil band
    const g = ctx.createLinearGradient(0, groundY - 4, 0, groundY + 46);
    g.addColorStop(0, 'rgba(139,116,88,0.16)');
    g.addColorStop(1, 'rgba(139,116,88,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, groundY, w, 46);
    // Ink ground line
    ctx.strokeStyle = 'rgba(90,74,58,0.5)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(w * 0.08, groundY);
    ctx.lineTo(w * 0.92, groundY);
    ctx.stroke();
  }
}

// ---------------------------------------------------------------------------
// Convenience runner: wires a tree to a canvas with rAF + DPR handling.
// Pauses when the tab is hidden. Returns a handle with the tree and stop().
// ---------------------------------------------------------------------------

export function mountTree(canvas, options) {
  const tree = new ProgressTree(options);
  const ctx = canvas.getContext('2d');
  let raf = 0;
  let last = performance.now();

  function resize() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  const ro = new ResizeObserver(resize);
  ro.observe(canvas);

  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    tree.tick(dt);
    const rect = canvas.getBoundingClientRect();
    tree.render(ctx, rect.width, rect.height);
    raf = requestAnimationFrame(frame);
  }
  raf = requestAnimationFrame(frame);

  const onVis = () => {
    if (document.hidden) cancelAnimationFrame(raf);
    else { last = performance.now(); raf = requestAnimationFrame(frame); }
  };
  document.addEventListener('visibilitychange', onVis);

  return {
    tree,
    stop() {
      cancelAnimationFrame(raf);
      ro.disconnect();
      document.removeEventListener('visibilitychange', onVis);
    },
  };
}
