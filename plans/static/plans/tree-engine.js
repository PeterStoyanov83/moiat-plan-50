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
 * Girth is secondary growth: a limb keeps thickening from the day it appears
 * until full maturity, so the trunk of an old tree is much stouter than the
 * same trunk on the sapling.
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
  { minActions: 0,   label: 'Семе почива в земята' },
  { minActions: 1,   label: 'Корените се спускат надолу' },
  { minActions: 3,   label: 'Покълна крехко стъбло' },
  { minActions: 7,   label: 'Стволът се издига' },
  { minActions: 14,  label: 'Първите клони се разклоняват' },
  { minActions: 30,  label: 'Младо дърво, което расте свободно' },
  { minActions: 60,  label: 'Тънки клонки изпълват короната' },
  { minActions: 100, label: 'Короната е пълна с листа' },
  { minActions: 200, label: 'Старо дърво — в цъфтеж' },
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
  spring: { leaves: ['#9fbf6b', '#b5cf7e', '#8ab35e', '#c8dc95'], newLeaf: '#d3e4a4', blossom: '#f4cdd6', blossomRate: 0.80 },
  summer: { leaves: ['#6f9a52', '#83a95f', '#5d8a48', '#96b573'], newLeaf: '#b6cf8e', blossom: '#f0e3c8', blossomRate: 0.28 },
  autumn: { leaves: ['#c98f3d', '#b9772f', '#d4a755', '#a86a2e'], newLeaf: '#ddb968', blossom: '#e8c9a0', blossomRate: 0.10 },
  winter: { leaves: [], newLeaf: '#ffffff', blossom: '#ffffff', blossomRate: 0 },
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
// Species archetypes — each user grows a recognizably different tree
// ---------------------------------------------------------------------------
//
// heightScale   fraction of available sky the tree may fill vertically
// widthScale    trunk girth multiplier (oak ≫ birch)
// tipAngle      [min,max] radians for the asymmetric tip split
// sideAngle     [min,max] radians for side branches off a limb
// contRatio     continuation branch length as fraction of parent
// sideRatio     side branch length as fraction of parent
// widthDecay    child thickness as fraction of parent
// trunkSides    [min,max] count of side branches along the trunk
// taperByHeight side branches shorten toward the top (1 = strongly conical)
// droop         gravity multiplier (willow weeps, oak barely bends)
// maxDepth      recursion depth
// leaf*         foliage density / proportions, blossomAffinity scales bloom count

const SPECIES = {
  ash: {
    heightScale: 0.92, widthScale: 1.0,
    tipAngle: [0.25, 0.60], sideAngle: [0.55, 1.00], angleNoise: 1.0, curvature: 1.0,
    contRatio: [0.62, 0.80], sideRatio: [0.30, 0.60], widthDecay: 0.65,
    trunkSides: [2, 3], taperByHeight: 0.25, droop: 0.7, maxDepth: 5,
    leafDensity: 1.0, leafAspect: 0.55, leafSize: 1.0, trunkTaper: 0.45, blossomAffinity: 1.0,
  },
  oak: {
    heightScale: 0.80, widthScale: 1.55,
    tipAngle: [0.35, 0.75], sideAngle: [0.60, 1.10], angleNoise: 1.4, curvature: 1.6,
    contRatio: [0.58, 0.76], sideRatio: [0.35, 0.60], widthDecay: 0.70,
    trunkSides: [2, 4], taperByHeight: 0.30, droop: 0.8, maxDepth: 5,
    leafDensity: 1.15, leafAspect: 0.60, leafSize: 1.0, trunkTaper: 0.42, blossomAffinity: 0.7,
  },
  birch: {
    heightScale: 1.0, widthScale: 0.85,
    tipAngle: [0.15, 0.45], sideAngle: [0.50, 0.90], angleNoise: 0.9, curvature: 0.9,
    contRatio: [0.62, 0.78], sideRatio: [0.35, 0.60], widthDecay: 0.60,
    trunkSides: [2, 3], taperByHeight: 0.45, droop: 1.3, maxDepth: 5,
    leafDensity: 1.2, leafAspect: 0.55, leafSize: 1.0, trunkTaper: 0.40, blossomAffinity: 0.6,
  },
  willow: {
    heightScale: 0.85, widthScale: 1.1,
    tipAngle: [0.20, 0.50], sideAngle: [0.50, 0.95], angleNoise: 1.1, curvature: 1.2,
    contRatio: [0.66, 0.86], sideRatio: [0.40, 0.70], widthDecay: 0.62,
    trunkSides: [2, 3], taperByHeight: 0.20, droop: 3.4, maxDepth: 5,
    leafDensity: 1.4, leafAspect: 0.35, leafSize: 0.85, trunkTaper: 0.45, blossomAffinity: 0.5,
  },
};

// Legacy personality names → species, so old saved state keeps working.
// Retired species (sequoia, baobab) map to their nearest living relatives.
const PERSONALITY_ALIASES = {
  balanced: 'ash', calm: 'oak', energetic: 'birch', creative: 'willow',
  sequoia: 'birch', baobab: 'oak',
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
const rangeRnd = (rng, [lo, hi]) => lo + rng() * (hi - lo);

/** Mix a #rrggbb color toward another by k ∈ [0,1]. */
function fadeToward(hexA, hexB, k) {
  const a = parseInt(hexA.slice(1), 16), b = parseInt(hexB.slice(1), 16);
  const mix = (sa, sb) => Math.round(sa + (sb - sa) * k);
  const r = mix((a >> 16) & 255, (b >> 16) & 255);
  const g = mix((a >> 8) & 255, (b >> 8) & 255);
  const bl = mix(a & 255, b & 255);
  return `rgb(${r},${g},${bl})`;
}

// ---------------------------------------------------------------------------
// The tree
// ---------------------------------------------------------------------------

export class ProgressTree {
  /**
   * @param {object} opts
   * @param {string} opts.userId       deterministic seed — same user, same tree
   * @param {string} [opts.species]    ash | oak | birch | willow
   * @param {string} [opts.personality] legacy alias for species
   * @param {string} [opts.season]     spring | summer | autumn | winter
   * @param {number} [opts.completedActions]
   */
  constructor({ userId, species, personality, season = 'summer', completedActions = 0, level = 1 }) {
    this.userId = userId;
    const requested = species || personality;
    this.species = SPECIES[requested] ? requested
      : (SPECIES[PERSONALITY_ALIASES[requested]] ? PERSONALITY_ALIASES[requested] : 'ash');
    this.season = SEASONS[season] ? season : 'summer';

    // Program level (1–20): each mastered level thickens the trunk and every
    // limb — the wood of the tree is the user's accumulated discipline
    this.level = Math.min(20, Math.max(1, level));
    this.displayedLevel = this.level;

    // Care state (inactivity system): health fades leaves, dormancy bares
    // the crown — the wood never suffers, roots never regress
    this.health = 100;
    this.displayedHealth = 100;
    this.dormant = false;

    this.targetM = maturityFromActions(completedActions);
    this.displayedM = this.targetM; // first paint shows the persisted tree instantly
    this.completedActions = completedActions;

    this.time = 0;          // seconds, drives wind
    this.windStrength = 1;  // baseline sway
    this.gust = 0;          // decaying boost when an action completes
    this.snow = this.season === 'winter' ? 1 : 0; // snow cover 0..1, piles up over time
    this.glimmers = [];     // ephemeral golden pops marking exactly where new growth appeared
    this._glimmerOps = [];  // per-frame draw queue so glimmers render on top of everything
    this.camera = { zoom: 1, x: 0, y: 0 }; // pan/zoom; screen = world·zoom + (x,y)

    // Deferred progress: steps done on other screens queue here and are only
    // spent — with the zoom-into-the-leaf reveal — once the tree is visible
    this.pendingActions = null;
    this.reveal = null;      // active cinematic: { phase: in|hold|out, t, from, to }
    this.onReveal = null;     // hook: fires once, when the first queued growth lands
    this.onRevealStop = null; // hook: fires at EVERY recap stop (keep counters live)
    this._layout = null;     // last render layout, needed to aim the camera

    this.generate();
  }

  // -- Structure generation (runs once; topology never changes) --------------

  generate() {
    const rng = mulberry32(hashString(this.userId));
    const S = SPECIES[this.species];

    // Normalize trunk length so the tallest possible leader chain still fits
    // the sky above the ground line, whatever the species' contRatio is.
    const meanCont = (S.contRatio[0] + S.contRatio[1]) / 2;
    let extent = 0;
    for (let d = 0, l = 1; d <= S.maxDepth; d++) { extent += l; l *= meanCont; }
    this.trunkUnit = S.heightScale / extent; // fraction of available sky per trunk-length

    this.trunk = this.growBranch(rng, S, {
      depth: 0,
      angle: -Math.PI / 2 + (rng() - 0.5) * 0.10, // slight natural lean
      length: 1.0,                                 // trunk-lengths; scaled at render
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

    // The environment: rolling hills and a distant forest — company for the
    // user's tree, deliberately soft and simple so their own tree is always
    // the detailed one. Seeded separately so tree topology stays untouched.
    const erng = mulberry32(hashString(this.userId + '::env'));
    this.env = {
      hills: [
        { lift: 0.30 + erng() * 0.04, amp: 0.014 + erng() * 0.010, freq: 1.1 + erng() * 0.5, phase: erng() * 6.28, fade: 0.80 },
        { lift: 0.18 + erng() * 0.03, amp: 0.018 + erng() * 0.012, freq: 0.9 + erng() * 0.5, phase: erng() * 6.28, fade: 0.66 },
        { lift: 0.07 + erng() * 0.03, amp: 0.020 + erng() * 0.014, freq: 0.8 + erng() * 0.4, phase: erng() * 6.28, fade: 0.58 },
      ],
      trees: [],
    };
    const perLayer = [6, 5, 3];
    const clearance = [0, 0.12, 0.24]; // keep the middle open for the user's tree
    for (let li = 0; li < 3; li++) {
      for (let i = 0; i < perLayer[li]; i++) {
        let x;
        do { x = 0.03 + erng() * 0.94; } while (Math.abs(x - 0.5) < clearance[li]);
        this.env.trees.push({
          layer: li,
          x,
          scale: 0.7 + erng() * 0.6,
          lean: (erng() - 0.5) * 0.3,
          shade: Math.floor(erng() * 4),
          phase: erng() * 6.28,
          blobs: [0, 1, 2].map((k) => ({
            dx: (k - 1) * (0.40 + erng() * 0.15) + (erng() - 0.5) * 0.2,
            dy: -0.72 - (k === 1 ? 0.25 : 0) + (erng() - 0.5) * 0.15,
            r: 0.42 + erng() * 0.22,
          })),
        });
      }
    }

    // Count nodes for perf budget awareness; cache leaf spots so a fully
    // grown tree can still shimmer somewhere specific on each action
    let count = 0;
    this.leafSpots = [];
    const walk = (b) => {
      count++;
      for (const leaf of b.leaves) {
        this.leafSpots.push({
          branch: b,
          leaf,
          // The maturity at which this leaf actually becomes visible:
          // inverse of the eased branch growth reaching the leaf's node
          availAt: b.growStart + b.growDur * (1 - Math.pow(1 - leaf.t, 1 / 3)),
        });
      }
      b.children.forEach((c) => { c.parent = b; walk(c); });
    };
    walk(this.trunk);
    this.branchCount = count;

    // Leaves ARE the progress counter: rank them by when their spot appears
    // (seedling stem first, outer twigs last) — leaf N unfolds on action N+1,
    // so the user can literally count their actions in the crown.
    // Sort strictly by visibility maturity: rank 0 is the seedling's lowest
    // stem leaf, which is always showable by the first action
    this.leafSpots.sort((a, b) => a.availAt - b.availAt);
    this.leafSpots.forEach((s, i) => { s.leaf.rank = i; });
    this.leafCapacity = this.leafSpots.length;

    // Leaves already earned before this session appear instantly, not as a
    // 700-leaf unfolding fireworks show on load
    for (const s of this.leafSpots) {
      if (s.leaf.rank < this.completedActions) s.leaf._born = -10;
    }
  }

  growBranch(rng, S, cfg) {
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
      curve: (rng() - 0.5) * 0.5 * S.curvature, // built-in bend, per-branch
      growStart,
      growDur: dur,
      swayPhase: rng() * Math.PI * 2,
      swayFreq: 0.7 + rng() * 0.7,
      side: cfg.side,
      children: [],
      leaves: [],
      blossom: null,
    };

    if (depth < S.maxDepth) {
      const childStartFor = (t) => growStart + dur * t;

      // Tip split: 2 (sometimes 3) continuations — deliberately asymmetric
      const splitLeft = rangeRnd(rng, S.tipAngle);   // left magnitude
      const splitRight = rangeRnd(rng, S.tipAngle);  // right magnitude, drawn independently
      const tipAngles = [-splitLeft, splitRight];
      if (rng() < 0.35 && depth < 3) tipAngles.push((rng() - 0.5) * 0.2); // middle shoot
      for (const a of tipAngles) {
        branch.children.push(this.growBranch(rng, S, {
          depth: depth + 1,
          angle: a + (rng() - 0.5) * 0.25 * S.angleNoise,
          length: cfg.length * rangeRnd(rng, S.contRatio),
          width: cfg.width * S.widthDecay,             // thickness decay
          attachT: 1.0,
          growStart: childStartFor(1.0),
          side: a < 0 ? -1 : 1,
        }));
      }

      // Side branches along the limb: alternate sides w/ jitter.
      // taperByHeight makes higher attachments shorter → tapered birch crown.
      const [sLo, sHi] = S.trunkSides;
      const sideCount = depth === 0
        ? sLo + Math.floor(rng() * (sHi - sLo + 1))
        : (rng() < 0.6 ? 1 : 0);
      let side = rng() < 0.5 ? -1 : 1;
      for (let i = 0; i < sideCount; i++) {
        const t = 0.35 + rng() * 0.55;
        const heightTaper = 1 - S.taperByHeight * t;
        branch.children.push(this.growBranch(rng, S, {
          depth: depth + 1,
          angle: side * rangeRnd(rng, S.sideAngle) + (rng() - 0.5) * 0.3 * S.angleNoise,
          length: cfg.length * rangeRnd(rng, S.sideRatio) * heightTaper,
          width: cfg.width * S.widthDecay * 0.85,
          attachT: t,
          growStart: childStartFor(t),
          side,
        }));
        side = -side;
      }
    }

    // Leaves are the progress counter — one action, one leaf — so every level
    // carries some: the seedling stem gets its first small leaves (a sprout
    // is never bare), inner limbs a few shoots, outer twigs the full crown.
    {
      let leafCount, tLo, tHi, sizeMul;
      if (depth === 0) {
        // A seedling wears its first week of leaves right on the stem
        leafCount = 4 + Math.floor(rng() * 2); tLo = 0.10; tHi = 0.65; sizeMul = 0.55;
      } else if (depth < Math.min(3, S.maxDepth - 1)) {
        leafCount = 2 + Math.floor(rng() * 2); tLo = 0.20; tHi = 0.90; sizeMul = 0.7;
      } else {
        // Capacity is tuned to ~1 leaf per action for a year-plus of use:
        // a 365-action crown should look full, not like 20% of a reserve
        leafCount = 1 + (rng() < 0.35 * S.leafDensity ? 1 : 0);
        tLo = 0.35; tHi = 1.0; sizeMul = 1;
      }
      for (let i = 0; i < leafCount; i++) {
        // The seedling stem gets an evenly-laddered run of leaves so the very
        // first action always has a leaf low enough on the young sprout
        const t = depth === 0
          ? tLo + (i / leafCount) * (tHi - tLo) + rng() * 0.04
          : tLo + rng() * (tHi - tLo);
        branch.leaves.push({
          t,
          side: rng() < 0.5 ? -1 : 1,
          size: (0.7 + rng() * 0.6) * S.leafSize * sizeMul,
          angleOffset: 0.5 + rng() * 0.7,
          shade: Math.floor(rng() * 4),
          rankJitter: rng(),  // breaks ties when ordering leaves by arrival
          rank: 0,            // assigned after generation: leaf N = action N+1
          flutterPhase: rng() * Math.PI * 2,
        });
      }
    }

    if (depth >= Math.min(3, S.maxDepth - 1)) {
      // Every outer twig tip is a blossom *candidate*; the season decides
      // how many actually open (spring ≫ summer > autumn, none in winter).
      if (depth >= S.maxDepth - 1) {
        branch.blossom = {
          chance: rng(),
          revealAt: 0.82 + rng() * 0.16,
          size: 0.8 + rng() * 0.5,
          phase: rng() * Math.PI * 2,
        };
      }
    }

    return branch;
  }

  // -- Progress API -----------------------------------------------------------

  /** Set absolute progress (e.g. after loading persisted state). Authoritative:
   *  clears any queued-but-unrevealed steps. */
  setActions(n, { animate = true } = {}) {
    const prevActions = this.completedActions;
    const prevTarget = this.targetM;
    this.completedActions = Math.max(0, n);
    this.targetM = maturityFromActions(this.completedActions);
    this.pendingActions = null;
    if (!animate) {
      this.displayedM = this.targetM;
      this.reveal = null; // a hard state change cancels any running cinematic
      for (const s of this.leafSpots) {
        if (s.leaf.rank < this.completedActions) s.leaf._born = -10;
        else s.leaf._born = undefined; // allows moving progress backwards (reset)
      }
      return;
    }
    // Keyed to the action count, not maturity: a fully grown tree (M capped
    // at 1) still glimmers somewhere on every action.
    if (this.completedActions > prevActions) {
      this.spawnGlimmers(prevTarget, this.targetM, prevActions, this.completedActions);
    }
  }

  /** How many leaves the user has earned and the tree can currently hold. */
  visibleLeafCount() {
    let n = 0;
    for (const s of this.leafSpots) {
      // availAt is the eased-growth visibility threshold, so this mirrors
      // exactly what the render pass shows
      if (s.leaf.rank < this.completedActions && s.availAt <= this.targetM) n++;
    }
    return n;
  }

  /**
   * Queue glimmer pops on everything that will newly appear in (m0, m1] —
   * the user sees exactly where their action landed. A fully grown tree has
   * nothing new left, so one deterministic leaf shimmers instead: the tree
   * always acknowledges the action somewhere specific.
   */
  spawnGlimmers(m0, m1, a0 = 0, a1 = 0) {
    const S = SPECIES[this.species];
    const pal = SEASONS[this.season];
    const found = [];

    // New leaves come straight from the rank ledger: actions (a0, a1] earn
    // leaves a0..a1-1
    for (let r = a0; r < Math.min(a1, this.leafCapacity); r++) {
      const spot = this.leafSpots[r];
      found.push({ branch: spot.branch, kind: 'leaf', leaf: spot.leaf, at: spot.availAt });
    }

    const walk = (b) => {
      if (b.growStart > m0 && b.growStart <= m1) {
        found.push({ branch: b, kind: 'branch', at: b.growStart });
      }
      if (b.blossom && b.blossom.revealAt > m0 && b.blossom.revealAt <= m1 &&
          b.blossom.chance < pal.blossomRate * S.blossomAffinity) {
        found.push({ branch: b, kind: 'blossom', at: b.blossom.revealAt });
      }
      b.children.forEach(walk);
    };
    walk(this.trunk);

    found.sort((a, b) => a.at - b.at);
    let picked = found.slice(0, 8); // a ripple of pops, not a firework show

    if (picked.length === 0 && this.leafSpots.length > 0) {
      // Fully grown: shimmer one deterministic existing leaf
      const rng = mulberry32((hashString(this.userId) ^ this.completedActions) >>> 0);
      const spot = this.leafSpots[Math.floor(rng() * this.leafSpots.length)];
      picked = [{ branch: spot.branch, kind: 'leaf', leaf: spot.leaf, at: m1 }];
    }

    picked.forEach((g, i) => {
      this.glimmers.push({
        ...g,
        delay: i * 0.30,     // staggered ripple through the crown
        created: this.time,
        started: null,
        done: false,
      });
    });
  }

  /**
   * The daily moment: one healthy action completed — possibly on another
   * screen. Nothing changes yet; the step is queued and spent by playReveal()
   * once the tree is actually in front of the user (mountTree watches for
   * that automatically).
   */
  completeAction() {
    this.queueActions((this.pendingActions ?? this.completedActions) + 1);
  }

  /** Queue an absolute action count for the next on-screen reveal. */
  queueActions(n) {
    if (n > this.completedActions) this.pendingActions = n;
  }

  hasPendingReveal() {
    return this.pendingActions !== null && this.pendingActions > this.completedActions;
  }

  /**
   * Play the queued progress. One banked step: dive to its leaf, let it
   * unfold under the spotlight, pull back. Several banked steps: a RECAP —
   * the camera hops leaf to leaf (up to 4 stops, days split between them),
   * each stop landing its share of growth up close, then one pull-back to
   * the whole tree. If the tree has never rendered, growth applies plainly.
   */
  playReveal() {
    if (!this.hasPendingReveal() || this.reveal) return;
    const total = this.pendingActions;
    const committed = this.completedActions;
    const delta = total - committed;

    if (!this._layout || this.leafCapacity === 0) {
      this.setActions(total);
      this.gust = 1;
      if (this.onReveal) this.onReveal(delta);
      return;
    }

    const { w, h } = this._layout;
    const Z = 3.4;
    // A full tree has no fresh leaves left — one stop at the vitality leaf
    // (the same one spawnGlimmers will shimmer, by the same seeded pick)
    const room = Math.max(1, this.leafCapacity - committed);
    const stopsCount = Math.max(1, Math.min(delta, 4, room));

    const stops = [];
    let base = committed;
    for (let i = 0; i < stopsCount; i++) {
      const actions = committed + Math.round((delta * (i + 1)) / stopsCount);
      let idx;
      if (committed >= this.leafCapacity) {
        const rng = mulberry32((hashString(this.userId) ^ total) >>> 0);
        idx = Math.floor(rng() * this.leafCapacity);
      } else {
        idx = Math.min(base, this.leafCapacity - 1); // first leaf of this segment
      }
      const [tx, ty] = this.computeSpotPosition(this.leafSpots[idx]);
      // Frame the leaf slightly above center, like leaning in to look at it
      stops.push({ actions, target: { zoom: Z, x: w / 2 - tx * Z, y: h * 0.42 - ty * Z } });
      base = actions;
    }

    this.reveal = {
      stops,
      stopIdx: 0,
      totalDelta: delta,
      phase: 'in',
      t: 0,
      from: { ...this.camera },
      to: stops[0].target,
    };
  }

  /**
   * Rest-pose world position of a leaf spot (no wind), by replaying the
   * branch geometry down the parent chain — works before the leaf exists.
   */
  computeSpotPosition(spot) {
    const L = this._layout;
    const S = SPECIES[this.species];
    const chain = [];
    for (let b = spot.branch; b; b = b.parent) chain.unshift(b);

    let x0 = L.baseX, y0 = L.groundY + 2, tanIn = -Math.PI / 2;
    let geom = null;
    for (let i = 0; i < chain.length; i++) {
      const b = chain[i];
      const flex = Math.pow((b.depth + 1) / (S.maxDepth + 1), 2);
      const theta = b.depth === 0 ? b.angle : tanIn + b.angle;
      const droop = 0.22 * S.droop * flex * Math.sin(theta + Math.PI / 2);
      const bend = b.curve + droop;
      const len = b.length * L.unit;
      const cx = x0 + Math.cos(theta) * len * 0.5;
      const cy = y0 + Math.sin(theta) * len * 0.5;
      const p2x = cx + Math.cos(theta + bend) * len * 0.5;
      const p2y = cy + Math.sin(theta + bend) * len * 0.5;
      geom = [x0, y0, cx, cy, p2x, p2y];
      const next = chain[i + 1];
      if (next) {
        [x0, y0] = bezierPoint(...geom, next.attachT);
        tanIn = bezierTangent(...geom, next.attachT);
      }
    }
    return bezierPoint(...geom, spot.leaf.t);
  }

  /** Change season in place (leaves, blossoms and snow adjust gradually). */
  setSeason(season) {
    if (SEASONS[season]) this.season = season;
  }

  /**
   * Level mastery (1–20): each advance is a MAJOR growth event — the trunk
   * and every limb visibly thicken (animated swell over ~2 s) and a golden
   * ripple runs up the main structure. Never regresses visually on its own;
   * pass animate:false for silent state restores.
   */
  setLevel(n, { animate = true } = {}) {
    const next = Math.min(20, Math.max(1, Math.round(n)));
    const wasLevel = this.level;
    this.level = next;
    if (!animate) {
      this.displayedLevel = next;
      return;
    }
    if (next > wasLevel) {
      this.gust = 1.2;
      // Ripple up the trunk and primary limbs to mark the thickening
      const targets = [this.trunk, ...this.trunk.children].slice(0, 5);
      targets.forEach((b, i) => {
        this.glimmers.push({
          branch: b, kind: 'branch', at: 0,
          delay: i * 0.25, created: this.time, started: null, done: false,
        });
      });
    }
  }

  /**
   * Care state, for the inactivity system: health 0–100 fades leaf vibrancy
   * and lets some leaves quietly drop (never below ~40 % of the crown);
   * dormant bares the tree entirely — the wood and roots stay, unharmed.
   */
  setHealth(h) {
    this.health = Math.min(100, Math.max(0, h));
  }

  setDormant(d) {
    this.dormant = !!d;
  }

  // -- Per-frame update ---------------------------------------------------------

  tick(dtSeconds) {
    this.time += dtSeconds;
    // Ease displayed maturity toward target: new growth unfurls over ~3–4s.
    // Under the reveal spotlight, grow faster so the leaf lands while framed.
    const rate = this.reveal ? 2.2 : 0.9;
    const d = this.targetM - this.displayedM;
    if (Math.abs(d) > 1e-5) this.displayedM += d * Math.min(1, dtSeconds * rate);
    else this.displayedM = this.targetM;

    // The reveal cinematic: dive in → growth lands under the spotlight → pull back
    if (this.reveal) {
      const r = this.reveal;
      const cam = this.camera;
      const easeInOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
      const lerpCam = (a, b, k) => {
        cam.zoom = a.zoom + (b.zoom - a.zoom) * k;
        cam.x = a.x + (b.x - a.x) * k;
        cam.y = a.y + (b.y - a.y) * k;
      };
      r.t += dtSeconds;
      if (r.phase === 'in') {
        // First dive is slower; hops between recap stops are brisker
        const dur = r.stopIdx === 0 ? 1.2 : 0.9;
        lerpCam(r.from, r.to, easeInOut(Math.min(1, r.t / dur)));
        if (r.t >= dur) {
          r.phase = 'hold';
          r.t = 0;
          // This stop's share of growth lands, framed up close
          this.setActions(r.stops[r.stopIdx].actions);
          this.gust = 1;
          if (r.stopIdx === 0 && this.onReveal) this.onReveal(r.totalDelta);
          if (this.onRevealStop) this.onRevealStop(this.completedActions);
        }
      } else if (r.phase === 'hold') {
        const lastStop = r.stopIdx === r.stops.length - 1;
        const dur = lastStop ? 2.2 : 1.4;
        // A slow breath outward while the leaf unfolds
        cam.zoom = r.to.zoom * (1 - 0.03 * easeInOut(Math.min(1, r.t / dur)));
        if (r.t >= dur) {
          r.t = 0;
          r.from = { ...cam };
          if (!lastStop) {
            r.stopIdx += 1;
            r.phase = 'in';
            r.to = r.stops[r.stopIdx].target;
          } else {
            r.phase = 'out';
            r.to = { zoom: 1, x: 0, y: 0 };
          }
        }
      } else {
        lerpCam(r.from, r.to, easeInOut(Math.min(1, r.t / 1.6)));
        if (r.t >= 1.6) this.reveal = null;
      }
    }
    this.gust *= Math.pow(0.35, dtSeconds); // gust decays over ~2s

    // Snow piles up slowly through winter (~10s to settle) and melts away after
    const snowTarget = this.season === 'winter' ? 1 : 0;
    this.snow += (snowTarget - this.snow) * Math.min(1, dtSeconds * 0.25);
    if (this.snow < 0.005) this.snow = 0;

    // Level girth swells over ~2s; health fades gently, recovers gently
    this.displayedLevel += (this.level - this.displayedLevel) * Math.min(1, dtSeconds * 1.2);
    this.displayedHealth += (this.health - this.displayedHealth) * Math.min(1, dtSeconds * 0.8);
  }

  // -- Rendering ----------------------------------------------------------------

  render(ctx, w, h) {
    const M = this.displayedM;
    const S = SPECIES[this.species];
    const groundY = h * 0.82;
    const baseX = w / 2;
    // Trunk length in px: the species' leader chain fits the sky above ground
    const sky = groundY - h * 0.05;
    const unit = Math.min(sky * this.trunkUnit, w * 0.34);
    const unitWidth = h * 0.016 * S.widthScale;
    const wind = (this.windStrength + this.gust * 2.5) * 0.012;
    this._layout = { w, h, baseX, groundY, unit, unitWidth };
    // Level 1 → 0.75×, level 20 → 1.6×: every mastered level adds visible wood
    this._levelGirth = 0.75 + 0.85 * ((this.displayedLevel - 1) / 19);

    ctx.clearRect(0, 0, w, h);

    // Winter cools the whole scene so the white snow can read against
    // the warm paper background (screen-space, unaffected by the camera)
    if (this.snow > 0) {
      ctx.fillStyle = `rgba(214,224,236,${0.42 * this.snow})`;
      ctx.fillRect(0, 0, w, h);
    }

    // Camera: everything that belongs to the scene pans and zooms together
    const cam = this.camera;
    ctx.save();
    ctx.translate(cam.x, cam.y);
    ctx.scale(cam.zoom, cam.zoom);

    this.drawEnvironment(ctx, w, h, groundY);
    this.drawGround(ctx, w, groundY);
    this.drawRoots(ctx, baseX, groundY, unit, M);
    this.drawSeed(ctx, baseX, groundY, M);

    const trunkP = this.progressOf(this.trunk, M);
    this._glimmerOps.length = 0;
    if (trunkP > 0) {
      this.drawBranch(ctx, this.trunk, baseX, groundY + 2, -Math.PI / 2, unit, unitWidth, M, wind, S);
    }

    // Glimmer pops draw above the whole tree so the spot is unmistakable
    if (this._glimmerOps.length) {
      for (const [gx, gy, t] of this._glimmerOps) this.drawGlimmer(ctx, gx, gy, t, unit);
    }
    if (this.glimmers.length) this.glimmers = this.glimmers.filter((g) => !g.done);

    ctx.restore();

    // Snowfall drifts in front of the scene, in screen space
    if (this.snow > 0) this.drawSnowfall(ctx, w, h);
  }

  progressOf(node, M) {
    return easeOut(clamp01((M - node.growStart) / node.growDur));
  }

  drawBranch(ctx, b, x0, y0, parentTangent, unitLen, unitWidth, M, wind, S) {
    const p = this.progressOf(b, M);
    if (p <= 0) return;

    // Wind: deeper (thinner) branches sway more; motion accumulates down the hierarchy
    const flex = Math.pow((b.depth + 1) / (S.maxDepth + 1), 2);
    const sway = wind * flex * (
      Math.sin(this.time * b.swayFreq + b.swayPhase) * 0.7 +
      Math.sin(this.time * b.swayFreq * 2.3 + b.swayPhase * 1.7) * 0.3
    ) * 40;

    const theta = (b.depth === 0 ? b.angle : parentTangent + b.angle) + sway;

    // Gravity: bend the branch tip toward the ground — a willow weeps,
    // an oak barely notices
    const droop = 0.22 * S.droop * flex * Math.sin(theta + Math.PI / 2);
    const bend = b.curve + droop;

    const len = b.length * unitLen;
    const p0x = x0, p0y = y0;
    const cx = p0x + Math.cos(theta) * len * 0.5;
    const cy = p0y + Math.sin(theta) * len * 0.5;
    const p2x = cx + Math.cos(theta + bend) * len * 0.5;
    const p2y = cy + Math.sin(theta + bend) * len * 0.5;

    // Secondary growth: a limb keeps thickening from the moment it appears
    // until the tree reaches full maturity — old trunks are stout trunks.
    const girth = 0.45 + 0.55 * clamp01((M - b.growStart) / Math.max(0.25, 1 - b.growStart));
    const w0 = Math.max(0.6, b.width * unitWidth * (0.35 + 0.65 * p) * girth * this._levelGirth);
    const wTip = Math.max(0.4, w0 * (b.depth === 0 ? S.trunkTaper : 0.45));

    // Draw the grown portion [0, p] as tapered polyline segments
    const SEGS = b.depth <= 1 ? 10 : 6;
    ctx.strokeStyle = trunkColor(b.depth, S.maxDepth);
    ctx.lineCap = 'round';
    const pts = [[p0x, p0y]];
    let [px, py] = [p0x, p0y];
    for (let i = 1; i <= SEGS; i++) {
      const u = (i / SEGS) * p;
      const [qx, qy] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, u);
      ctx.lineWidth = w0 + (wTip - w0) * (i / SEGS);
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(qx, qy);
      ctx.stroke();
      pts.push([qx, qy]);
      px = qx; py = qy;
    }

    // Snow settles on the upper side of near-horizontal limbs
    if (this.snow > 0.02) {
      for (let i = 1; i < pts.length; i++) {
        const dx = pts[i][0] - pts[i - 1][0];
        const dy = pts[i][1] - pts[i - 1][1];
        const segLen = Math.hypot(dx, dy) || 1;
        const horiz = Math.abs(dx) / segLen; // flat limbs collect most
        if (horiz < 0.08) continue;
        const segW = w0 + (wTip - w0) * (i / SEGS);
        // Perpendicular offset pointing up, resting on the bark
        let nx = dy / segLen, ny = -dx / segLen;
        if (ny > 0) { nx = -nx; ny = -ny; }
        const off = segW * 0.45;
        const snowW = Math.max(1.2, segW * 0.9 * horiz * this.snow);
        const x1 = pts[i - 1][0] + nx * off, y1 = pts[i - 1][1] + ny * off;
        const x2 = pts[i][0] + nx * off, y2 = pts[i][1] + ny * off;
        // Cool shadowed underside, then bright white cap on top
        ctx.strokeStyle = `rgba(148,163,184,${0.45 * this.snow})`;
        ctx.lineWidth = snowW + 1;
        ctx.beginPath(); ctx.moveTo(x1, y1 + 0.7); ctx.lineTo(x2, y2 + 0.7); ctx.stroke();
        ctx.strokeStyle = `rgba(255,255,255,${0.95 * this.snow})`;
        ctx.lineWidth = snowW;
        ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      }
    }

    // Leaves: earned by rank (one per action), shown once the branch has
    // grown past the leaf's node; winter and dormancy bare the branches.
    // Low health lets some leaves quietly drop — never below ~40 % of the
    // crown, and the wood is never touched.
    if (this.season !== 'winter' && !this.dormant) {
      const keep = 0.4 + 0.6 * (this.displayedHealth / 100);
      for (const leaf of b.leaves) {
        if (leaf.t > p) continue;
        if (leaf.rank >= this.completedActions) continue; // not earned yet
        if (leaf.rankJitter > keep) continue;             // dropped while unattended
        if (leaf._born === undefined) {
          // First frame this leaf is eligible: unfold now, slightly staggered
          leaf._born = this.time + (leaf.rank % 4) * 0.15;
        }
        const lp = clamp01((this.time - leaf._born) / 1.4);
        if (lp <= 0) continue;
        const [lx, ly] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, leaf.t);
        const tan = bezierTangent(p0x, p0y, cx, cy, p2x, p2y, leaf.t);
        this.drawLeaf(ctx, lx, ly, tan, leaf, easeOut(lp), M, unitLen, S);
      }
    }

    // Blossoms at twig tips: every tip is a candidate, the season decides how
    // many open — spring covers the crown, winter closes them all.
    if (b.blossom && p >= 1 && !this.dormant) {
      const pal = SEASONS[this.season];
      if (b.blossom.chance < pal.blossomRate * S.blossomAffinity) {
        const bp = clamp01((M - b.blossom.revealAt) / 0.03);
        if (bp > 0) this.drawBlossom(ctx, p2x, p2y, b.blossom, easeOut(bp), unitLen);
      }
    }

    // Glimmers attached to this branch: resolve their exact world position
    // (riding the wind-swayed geometry) and queue them to draw on top
    if (this.glimmers.length) {
      for (const g of this.glimmers) {
        if (g.branch !== b || g.done) continue;
        let gx = null, gy = null;
        if (g.kind === 'leaf' && this.season !== 'winter') {
          if (g.leaf.t <= p && g.leaf.rank < this.completedActions) {
            [gx, gy] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, g.leaf.t);
          }
        } else if (g.kind === 'blossom') {
          if (p >= 1 && M - b.blossom.revealAt > 0) { gx = p2x; gy = p2y; }
        } else if (p > 0) {
          // branch pops ride the growing tip; winter leaves fall back here too
          [gx, gy] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, p);
        }
        if (gx !== null) {
          if (g.started === null) g.started = this.time + g.delay;
          const t = (this.time - g.started) / 2.2;
          if (t >= 1) g.done = true;
          else if (t > 0) this._glimmerOps.push([gx, gy, t]);
        } else if (this.time - g.created > 12) {
          g.done = true; // never became visible (e.g. season hid it) — let it go
        }
      }
    }

    // Children — recurse from their attach point with the local tangent
    for (const child of b.children) {
      if (child.attachT > p) continue;
      const [ax, ay] = bezierPoint(p0x, p0y, cx, cy, p2x, p2y, child.attachT);
      const tan = bezierTangent(p0x, p0y, cx, cy, p2x, p2y, child.attachT);
      this.drawBranch(ctx, child, ax, ay, tan, unitLen, unitWidth, M, wind, S);
    }
  }

  drawLeaf(ctx, x, y, tangent, leaf, unfold, M, unitLen, S) {
    const pal = SEASONS[this.season];
    // Leaves earned within the last week of actions are still tender-light
    const isNew = this.completedActions - leaf.rank <= 7;
    let color = isNew ? pal.newLeaf : pal.leaves[leaf.shade];
    // Unattended trees lose vibrancy: fade toward a dry pale tone
    const healthK = this.displayedHealth / 100;
    if (healthK < 0.995) color = fadeToward(color, '#b3ae95', (1 - healthK) * 0.7);
    const flutter = Math.sin(this.time * 2.1 + leaf.flutterPhase) * 0.12 * (1 + this.gust * 2);
    // A seedling's leaves are small; they reach full size as the tree matures
    const youth = 0.55 + 0.45 * clamp01(M / 0.35);
    const size = leaf.size * unitLen * 0.035 * unfold * youth;
    const ang = tangent + leaf.side * leaf.angleOffset + flutter;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(ang);
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.88;
    ctx.beginPath();
    ctx.ellipse(size * 1.1, 0, size * 1.25, size * S.leafAspect, 0, 0, Math.PI * 2);
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

  drawGlimmer(ctx, x, y, t, unitLen) {
    // t ∈ (0,1): quick bloom, long soft fade
    const grow = 1 - Math.pow(1 - t, 2);
    const alpha = t < 0.12 ? t / 0.12 : 1 - (t - 0.12) / 0.88;
    const R = unitLen * 0.08 * (0.35 + 0.65 * grow);

    // Warm glow core
    const glow = ctx.createRadialGradient(x, y, 0, x, y, R * 1.5);
    glow.addColorStop(0, `rgba(255,232,160,${0.72 * alpha})`);
    glow.addColorStop(0.5, `rgba(255,215,130,${0.30 * alpha})`);
    glow.addColorStop(1, 'rgba(255,215,130,0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(x, y, R * 1.5, 0, Math.PI * 2);
    ctx.fill();

    // Expanding ring
    ctx.strokeStyle = `rgba(255,205,110,${0.85 * alpha})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(x, y, R, 0, Math.PI * 2);
    ctx.stroke();

    // A few tiny four-point sparkles drifting outward
    ctx.strokeStyle = `rgba(255,240,190,${0.9 * alpha})`;
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + t * 0.8 + x * 0.01; // x seeds rotation variety
      const d = R * (0.55 + 0.75 * grow);
      const sx = x + Math.cos(a) * d;
      const sy = y + Math.sin(a) * d;
      const s = 3.0 * (1 - t);
      ctx.beginPath();
      ctx.moveTo(sx - s, sy); ctx.lineTo(sx + s, sy);
      ctx.moveTo(sx, sy - s); ctx.lineTo(sx, sy + s);
      ctx.stroke();
    }
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
      ctx.lineWidth = Math.max(0.8, unit * 0.012 * p * this._levelGirth);
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

  hillYAt(hill, xNorm, h, groundY) {
    return groundY - h * hill.lift
      + Math.sin(hill.phase + xNorm * hill.freq * Math.PI * 2) * h * hill.amp
      + Math.sin(hill.phase * 2.7 + xNorm * hill.freq * 5.1) * h * hill.amp * 0.35;
  }

  drawEnvironment(ctx, w, h, groundY) {
    const PAPER = '#f4eee1';
    const winter = this.season === 'winter';
    let hillBase = '#ccd8bc';
    if (this.season === 'autumn') hillBase = '#dbcba9';
    if (winter) hillBase = '#e2e8f0';

    for (let li = 0; li < this.env.hills.length; li++) {
      const hill = this.env.hills[li];
      // Hill band, drawn well past the viewport so zooming out never
      // reveals an edge (world x spans -1..2 in normalized units)
      ctx.beginPath();
      ctx.moveTo(-w, groundY + 60);
      const STEPS = 48;
      for (let s = 0; s <= STEPS; s++) {
        const xNorm = -1 + (s / STEPS) * 3;
        ctx.lineTo(xNorm * w, this.hillYAt(hill, xNorm, h, groundY));
      }
      ctx.lineTo(2 * w, groundY + 60);
      ctx.closePath();
      ctx.fillStyle = winter
        ? fadeToward('#d8e1ec', '#fafbfd', hill.fade)      // snowy: near-white, cool shadow
        : fadeToward(hillBase, PAPER, hill.fade);
      ctx.globalAlpha = 0.85;
      ctx.fill();
      ctx.globalAlpha = 1;

      // This layer's forest stands on its ridge; nearer hills overlap it
      for (const bt of this.env.trees) {
        if (bt.layer === li) this.drawBgTree(ctx, bt, w, h, groundY, hill, PAPER);
      }
    }
  }

  drawBgTree(ctx, bt, w, h, groundY, hill, PAPER) {
    const x = bt.x * w;
    const y = this.hillYAt(hill, bt.x, h, groundY);
    const size = h * (0.033 + bt.layer * 0.014) * bt.scale;
    const sway = Math.sin(this.time * 0.4 + bt.phase) * size * 0.03;
    const pal = SEASONS[this.season];
    const winter = this.season === 'winter';

    // Simple faded trunk
    ctx.strokeStyle = fadeToward('#8a6f57', PAPER, hill.fade * 0.9);
    ctx.lineCap = 'round';
    ctx.lineWidth = Math.max(1, size * 0.09);
    const topX = x + bt.lean * size + sway;
    const topY = y - size * 0.85;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.quadraticCurveTo(x + bt.lean * size * 0.4, y - size * 0.5, topX, topY);
    ctx.stroke();

    if (winter) {
      // Bare limbs, a stroke or two — sleeping neighbours
      ctx.lineWidth = Math.max(0.7, size * 0.05);
      for (const b of bt.blobs) {
        ctx.beginPath();
        ctx.moveTo(x + bt.lean * size * 0.5, y - size * 0.55);
        ctx.lineTo(topX + b.dx * size, topY + b.dy * size * 0.5);
        ctx.stroke();
      }
      return;
    }

    // Watercolor canopy blobs, faded by distance — recognizably a tree,
    // never competing with the user's own
    for (const b of bt.blobs) {
      ctx.fillStyle = fadeToward(pal.leaves[bt.shade], PAPER, hill.fade * 0.85);
      ctx.globalAlpha = 0.75;
      ctx.beginPath();
      ctx.ellipse(topX + b.dx * size, topY + b.dy * size, size * b.r * 1.15, size * b.r * 0.8, bt.lean * 0.3, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  drawGround(ctx, w, groundY) {
    // Soft watercolor soil band
    const g = ctx.createLinearGradient(0, groundY - 4, 0, groundY + 46);
    g.addColorStop(0, 'rgba(139,116,88,0.16)');
    g.addColorStop(1, 'rgba(139,116,88,0)');
    ctx.fillStyle = g;
    ctx.fillRect(-w, groundY, w * 3, 46); // spans past the viewport for zoom-out
    // Ink ground line
    ctx.strokeStyle = `rgba(90,74,58,${0.5 * (1 - this.snow * 0.7)})`;
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(w * 0.08, groundY);
    ctx.lineTo(w * 0.92, groundY);
    ctx.stroke();
    // Snow blanket with a soft shaded crest so it reads against the paper
    if (this.snow > 0) {
      const top = groundY - 7 * this.snow;
      const s = ctx.createLinearGradient(0, top, 0, groundY + 30);
      s.addColorStop(0, `rgba(255,255,255,${0.95 * this.snow})`);
      s.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = s;
      ctx.fillRect(-w, top, w * 3, 40);
      ctx.strokeStyle = `rgba(148,163,184,${0.35 * this.snow})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(w * 0.06, top);
      ctx.lineTo(w * 0.94, top);
      ctx.stroke();
    }
  }

  drawSnowfall(ctx, w, h) {
    // Stateless drifting flakes: position is a pure function of time & index
    const N = 48;
    ctx.fillStyle = `rgba(255,255,255,${0.85 * this.snow})`;
    for (let i = 0; i < N; i++) {
      const speed = 14 + (i % 7) * 4;
      const x = ((i * 191.7) % w + Math.sin(this.time * 0.5 + i * 1.7) * 18 + w) % w;
      const y = ((this.time * speed + i * 211.3) % (h + 20)) - 10;
      const r = 1 + (i % 3) * 0.6;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

// ---------------------------------------------------------------------------
// Convenience runner: wires a tree to a canvas with rAF + DPR handling.
// Pauses when the tab is hidden. Returns a handle with the tree and stop().
// ---------------------------------------------------------------------------

export function mountTree(canvas, options = {}) {
  const tree = new ProgressTree(options);
  const ctx = canvas.getContext('2d');
  const interactive = options.interactive !== false; // pan/zoom on by default
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

  // Deferred-reveal watcher: a step done on another screen only lands — with
  // the zoom-into-the-leaf cinematic — once the tree is really being looked
  // at (canvas mostly in view AND the tab visible), after a short settle.
  let onScreen = true;
  let revealTimer = null;
  const tryReveal = () => {
    if (revealTimer || !tree.hasPendingReveal()) return;
    revealTimer = setTimeout(() => {
      revealTimer = null;
      if (onScreen && !document.hidden && tree.hasPendingReveal()) tree.playReveal();
    }, 450);
  };
  const io = ('IntersectionObserver' in window)
    ? new IntersectionObserver((entries) => {
        onScreen = entries[0].isIntersecting && entries[0].intersectionRatio >= 0.4;
        if (onScreen) tryReveal();
      }, { threshold: [0, 0.4] })
    : null;
  if (io) io.observe(canvas);

  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    tree.tick(dt);
    if (onScreen && tree.hasPendingReveal() && !tree.reveal) tryReveal();
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

  // -- Pan & zoom -------------------------------------------------------------
  // Wheel / trackpad-pinch zooms toward the cursor, drag pans, two-finger
  // touch pinches, double-click/tap resets. All state lives in tree.camera.
  const cleanups = [];
  if (interactive) {
    const cam = tree.camera;
    const pointers = new Map();

    const clampCam = () => {
      cam.zoom = Math.min(8, Math.max(0.5, cam.zoom));
      const r = canvas.getBoundingClientRect();
      // Keep at least a quarter of the scene on screen so the tree can't get lost
      cam.x = Math.min(r.width * 0.75, Math.max(r.width * 0.25 - r.width * cam.zoom, cam.x));
      cam.y = Math.min(r.height * 0.75, Math.max(r.height * 0.25 - r.height * cam.zoom, cam.y));
    };

    const zoomAt = (px, py, factor) => {
      const z0 = cam.zoom;
      const z1 = Math.min(8, Math.max(0.5, z0 * factor));
      cam.x = px - (px - cam.x) * (z1 / z0);
      cam.y = py - (py - cam.y) * (z1 / z0);
      cam.zoom = z1;
      clampCam();
    };

    const on = (target, type, fn, opts) => {
      target.addEventListener(type, fn, opts);
      cleanups.push(() => target.removeEventListener(type, fn, opts));
    };

    canvas.style.touchAction = 'none';
    canvas.style.cursor = 'grab';

    on(canvas, 'wheel', (e) => {
      e.preventDefault();
      if (tree.reveal) return; // the cinematic owns the camera
      const r = canvas.getBoundingClientRect();
      zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * 0.0015));
    }, { passive: false });

    on(canvas, 'pointerdown', (e) => {
      if (tree.reveal) return; // the cinematic owns the camera
      canvas.setPointerCapture(e.pointerId);
      pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      canvas.style.cursor = 'grabbing';
    });

    on(canvas, 'pointermove', (e) => {
      const prev = pointers.get(e.pointerId);
      if (!prev || tree.reveal) return;
      const cur = { x: e.clientX, y: e.clientY };
      if (pointers.size === 1) {
        cam.x += cur.x - prev.x;
        cam.y += cur.y - prev.y;
        clampCam();
      } else if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        const other = (a === prev) ? b : a;
        const d0 = Math.hypot(prev.x - other.x, prev.y - other.y);
        const d1 = Math.hypot(cur.x - other.x, cur.y - other.y);
        const r = canvas.getBoundingClientRect();
        const mid = { x: (cur.x + other.x) / 2 - r.left, y: (cur.y + other.y) / 2 - r.top };
        if (d0 > 0) zoomAt(mid.x, mid.y, d1 / d0);
        cam.x += (cur.x - prev.x) / 2;
        cam.y += (cur.y - prev.y) / 2;
        clampCam();
      }
      pointers.set(e.pointerId, cur);
    });

    const release = (e) => {
      pointers.delete(e.pointerId);
      if (pointers.size === 0) canvas.style.cursor = 'grab';
    };
    on(canvas, 'pointerup', release);
    on(canvas, 'pointercancel', release);

    on(canvas, 'dblclick', () => {
      if (tree.reveal) return;
      cam.zoom = 1; cam.x = 0; cam.y = 0;
    });
  }

  return {
    tree,
    stop() {
      cancelAnimationFrame(raf);
      ro.disconnect();
      if (io) io.disconnect();
      if (revealTimer) clearTimeout(revealTimer);
      document.removeEventListener('visibilitychange', onVis);
      cleanups.forEach((fn) => fn());
    },
  };
}
