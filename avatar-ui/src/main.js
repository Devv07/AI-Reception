import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRMLoaderPlugin } from "@pixiv/three-vrm";

// ============================================================
// CONFIGURATION
// ============================================================

const VRM_PATH = "/models/receptionist.vrm";
const WS_URL = "ws://127.0.0.1:8765";

// Set this to true when testing avatar without Python.
const AUTO_DEMO = false;

// ============================================================
// DOM
// ============================================================

const app = document.getElementById("app");

if (!app) {
  throw new Error("Element #app was not found.");
}

// ============================================================
// THREE.JS
// ============================================================

const scene = new THREE.Scene();

scene.background = new THREE.Color(0x171b21);

const camera = new THREE.PerspectiveCamera(
  32,
  window.innerWidth / window.innerHeight,
  0.01,
  100
);

camera.position.set(0, 1.4, 3.35);
camera.lookAt(0, 1.35, 0);

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.9;

renderer.shadowMap.enabled = false;

app.appendChild(renderer.domElement);

// ============================================================
// LIGHTING
// ============================================================

const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);

scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xfff4e8, 1.35);

keyLight.position.set(1.5, 2.8, 3.5);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xb8d4ff, 0.3);

fillLight.position.set(-2, 1.5, 2.5);
scene.add(fillLight);

// ============================================================
// LOOK TARGET
// ============================================================

const lookTarget = new THREE.Object3D();

lookTarget.position.set(
  0,
  1.5,
  2.5
);

scene.add(lookTarget);

// ============================================================
// VRM
// ============================================================

let vrm = null;

const loader = new GLTFLoader();

loader.register((parser) => {
  return new VRMLoaderPlugin(parser);
});

loader.load(
  VRM_PATH,

  (gltf) => {
    console.log("=================================");
    console.log("VRM LOADED");
    console.log("=================================");

    vrm = gltf.userData.vrm;

    if (!vrm) {
      console.error("VRM object not found.");
      return;
    }

    // IMPORTANT:
    // Do NOT call VRMUtils / springbone update logic here.
    // We want stable clothing.

    vrm.scene.visible = true;

    vrm.scene.position.set(0, 0, 0);
    vrm.scene.scale.setScalar(1.15);

    // Front-facing orientation.
    vrm.scene.rotation.y = 0;

    scene.add(vrm.scene);

    // Look-at system.
    if (vrm.lookAt) {
      vrm.lookAt.target = lookTarget;
    }

    setupHumanoid();
    applyInitialFormalArms();

    setupExpressions();

    printAvatarDiagnostics();

    console.log("=================================");
    console.log("AVATAR READY");
    console.log("=================================");
  },

  (progress) => {
    if (progress.total > 0) {
      const percent =
        (progress.loaded / progress.total) * 100;

      console.log(
        `Loading receptionist: ${percent.toFixed(0)}%`
      );
    }
  },

  (error) => {
    console.error(
      "================================="
    );

    console.error(
      "VRM LOAD ERROR"
    );

    console.error(error);

    console.error(
      "================================="
    );
  }
);

// ============================================================
// HUMANOID BONES
// ============================================================

const bones = {};

const restRotations = {};

const BONE_NAMES = [
  "hips",
  "spine",
  "chest",
  "upperChest",
  "neck",
  "head",

  "leftShoulder",
  "leftUpperArm",
  "leftLowerArm",
  "leftHand",

  "rightShoulder",
  "rightUpperArm",
  "rightLowerArm",
  "rightHand",
];

// ------------------------------------------------------------
// Get normalized bone
// ------------------------------------------------------------

function getNormalizedBone(name) {
  try {
    if (
      vrm &&
      vrm.humanoid &&
      typeof vrm.humanoid.getNormalizedBoneNode === "function"
    ) {
      return vrm.humanoid.getNormalizedBoneNode(name);
    }
  } catch (error) {
    console.warn(
      `Normalized bone failed: ${name}`,
      error
    );
  }

  return null;
}

// ------------------------------------------------------------
// Get raw bone fallback
// ------------------------------------------------------------

function getRawBone(name) {
  try {
    if (
      vrm &&
      vrm.humanoid &&
      typeof vrm.humanoid.getRawBoneNode === "function"
    ) {
      return vrm.humanoid.getRawBoneNode(name);
    }
  } catch (error) {
    console.warn(
      `Raw bone failed: ${name}`,
      error
    );
  }

  return null;
}

// ------------------------------------------------------------
// Setup
// ------------------------------------------------------------

function setupHumanoid() {
  if (!vrm?.humanoid) {
    console.error(
      "This VRM does not contain a humanoid."
    );

    return;
  }

  for (const name of BONE_NAMES) {
    let bone = getNormalizedBone(name);

    let source = "normalized";

    if (!bone) {
      bone = getRawBone(name);
      source = "raw";
    }

    if (!bone) {
      continue;
    }

    bones[name] = bone;

    restRotations[name] =
      bone.quaternion.clone();

    console.log(
      `[BONE] ${name} -> ${source}`
    );
  }
}

// ============================================================
// DIAGNOSTICS
// ============================================================

function printAvatarDiagnostics() {
  console.log("");
  console.log("========== AVATAR DIAGNOSTICS ==========");

  for (const name of BONE_NAMES) {
    if (bones[name]) {
      console.log(`✓ ${name}`);
    } else {
      console.warn(`✗ ${name} NOT FOUND`);
    }
  }

  console.log(
    "Total usable bones:",
    Object.keys(bones).length
  );

  console.log(
    "Expression manager:",
    !!vrm?.expressionManager
  );

  console.log(
    "LookAt:",
    !!vrm?.lookAt
  );

  console.log("========================================");
}

// ============================================================
// EXPRESSIONS
// ============================================================

let expressionManager = null;

function setupExpressions() {
  expressionManager =
    vrm?.expressionManager || null;

  if (!expressionManager) {
    console.warn(
      "No VRM expression manager found."
    );
  }
}

// ============================================================
// STATE
// ============================================================

const STATES = {
  IDLE: "idle",
  VISITOR_DETECTED: "visitor_detected",
  GREETING: "greeting",
  LISTENING: "listening",
  THINKING: "thinking",
  SPEAKING: "speaking",
  VISITOR_LEFT: "visitor_left",
};

let currentState = STATES.IDLE;

let stateChangedAt = performance.now();

function setAvatarState(state) {
  if (!state) {
    return;
  }

  if (currentState === state) {
    return;
  }

  console.log(
    `[AVATAR] ${currentState} -> ${state}`
  );

  currentState = state;

  stateChangedAt = performance.now();
}

// ============================================================
// ROTATION HELPERS
// ============================================================

const tempEuler = new THREE.Euler();

const tempQuaternion = new THREE.Quaternion();

const desiredQuaternion =
  new THREE.Quaternion();

const FORMAL_ARM_ROTATIONS = {
  leftUpperArm: [0, 0, -0.9],
  rightUpperArm: [0, 0, 0.9],
};

function applyInitialFormalArms() {
  for (const [name, rotation] of Object.entries(
    FORMAL_ARM_ROTATIONS
  )) {
    const bone = bones[name];
    const rest = restRotations[name];

    if (!bone || !rest) {
      continue;
    }

    const [x, y, z] = rotation;
    const offset = new THREE.Quaternion().setFromEuler(
      new THREE.Euler(x, y, z)
    );

    bone.quaternion.copy(rest).multiply(offset);
  }

  if (typeof vrm?.humanoid?.update === "function") {
    vrm.humanoid.update();
  }
}

function setBoneTarget(
  name,
  x,
  y,
  z,
  delta,
  speed = 5
) {
  const bone = bones[name];

  const rest = restRotations[name];

  if (!bone || !rest) {
    return;
  }

  tempEuler.set(x, y, z);

  tempQuaternion.setFromEuler(
    tempEuler
  );

  desiredQuaternion
    .copy(rest)
    .multiply(tempQuaternion);

  const interpolation =
    1 - Math.exp(-speed * delta);

  bone.quaternion.slerp(
    desiredQuaternion,
    interpolation
  );
}

// ============================================================
// FORMAL RESTORE
// ============================================================

function formalPosture(delta) {
  // Body
  setBoneTarget(
    "hips",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "spine",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "chest",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "upperChest",
    0,
    0,
    0,
    delta,
    5
  );

  // Head
  setBoneTarget(
    "neck",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "head",
    0,
    0,
    0,
    delta,
    5
  );

  // Arms back to formal position.
  setBoneTarget(
    "leftShoulder",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "rightShoulder",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "leftUpperArm",
    0,
    0,
    -0.9,
    delta,
    5
  );

  setBoneTarget(
    "rightUpperArm",
    0,
    0,
    0.9,
    delta,
    5
  );

  setBoneTarget(
    "leftLowerArm",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "rightLowerArm",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "leftHand",
    0,
    0,
    0,
    delta,
    5
  );

  setBoneTarget(
    "rightHand",
    0,
    0,
    0,
    delta,
    5
  );
}

// ============================================================
// IDLE
// ============================================================

function animateIdle(time, delta) {
  formalPosture(delta);

  // Natural breathing.
  const breathing =
    Math.sin(time * 1.8) * 0.015;

  setBoneTarget(
    "chest",
    breathing,
    Math.sin(time * 0.7) * 0.012,
    0,
    delta,
    3
  );

  // Small natural head movement.
  setBoneTarget(
    "head",
    Math.sin(time * 0.65) * 0.018,
    Math.sin(time * 0.45) * 0.025,
    Math.sin(time * 0.4) * 0.01,
    delta,
    3
  );
}

// ============================================================
// VISITOR ATTENTION
// ============================================================

function animateVisitorDetected(
  time,
  delta
) {
  formalPosture(delta);

  // Slightly raise attention toward visitor.
  setBoneTarget(
    "neck",
    -0.025,
    Math.sin(time * 0.5) * 0.015,
    0,
    delta,
    6
  );

  setBoneTarget(
    "head",
    -0.055,
    Math.sin(time * 0.8) * 0.025,
    0,
    delta,
    6
  );

  // Slight professional body orientation.
  setBoneTarget(
    "chest",
    0.015,
    Math.sin(time * 0.5) * 0.015,
    0,
    delta,
    5
  );
}

// ============================================================
// NAMASKAR
// ============================================================

function animateNamaskar(
  elapsed,
  time,
  delta
) {
  // Start from formal posture.
  formalPosture(delta);

  // ----------------------------------------------------------
  // Phase 1:
  // Hands begin coming toward chest.
  // ----------------------------------------------------------

  if (elapsed < 0.8) {
    const progress =
      THREE.MathUtils.clamp(
        elapsed / 0.8,
        0,
        1
      );

    // Smooth ease.
    const p =
      progress *
      progress *
      (3 - 2 * progress);

    setBoneTarget(
      "leftUpperArm",
      THREE.MathUtils.lerp(
        0,
        -0.9,
        p
      ),
      THREE.MathUtils.lerp(
        0,
        0.25,
        p
      ),
      THREE.MathUtils.lerp(
        -0.9,
        -0.25,
        p
      ),
      delta,
      7
    );

    setBoneTarget(
      "rightUpperArm",
      THREE.MathUtils.lerp(
        0,
        -0.9,
        p
      ),
      THREE.MathUtils.lerp(
        0,
        -0.25,
        p
      ),
      THREE.MathUtils.lerp(
        0.9,
        0.25,
        p
      ),
      delta,
      7
    );

    setBoneTarget(
      "leftLowerArm",
      THREE.MathUtils.lerp(
        0,
        -1.1,
        p
      ),
      0,
      THREE.MathUtils.lerp(
        0,
        -0.25,
        p
      ),
      delta,
      7
    );

    setBoneTarget(
      "rightLowerArm",
      THREE.MathUtils.lerp(
        0,
        -1.1,
        p
      ),
      0,
      THREE.MathUtils.lerp(
        0,
        0.25,
        p
      ),
      delta,
      7
    );
  }

  // ----------------------------------------------------------
  // Phase 2:
  // Namaskar pose + respectful bow.
  // ----------------------------------------------------------

  else if (elapsed < 2.2) {
    const bow =
      Math.sin(
        ((elapsed - 0.8) / 1.4) *
        Math.PI
      ) * 0.12;

    // Hands together near chest.
    setBoneTarget(
      "leftUpperArm",
      -0.9,
      0.25,
      -0.25,
      delta,
      8
    );

    setBoneTarget(
      "rightUpperArm",
      -0.9,
      -0.25,
      0.25,
      delta,
      8
    );

    setBoneTarget(
      "leftLowerArm",
      -1.1,
      0,
      -0.25,
      delta,
      8
    );

    setBoneTarget(
      "rightLowerArm",
      -1.1,
      0,
      0.25,
      delta,
      8
    );

    // Respectful small head bow.
    setBoneTarget(
      "neck",
      bow,
      0,
      0,
      delta,
      8
    );

    setBoneTarget(
      "head",
      bow * 1.3,
      0,
      0,
      delta,
      8
    );
  }

  // ----------------------------------------------------------
  // Phase 3:
  // Hold Namaskar briefly.
  // ----------------------------------------------------------

  else if (elapsed < 3.1) {
    setBoneTarget(
      "leftUpperArm",
      -0.9,
      0.25,
      -0.25,
      delta,
      8
    );

    setBoneTarget(
      "rightUpperArm",
      -0.9,
      -0.25,
      0.25,
      delta,
      8
    );

    setBoneTarget(
      "leftLowerArm",
      -1.1,
      0,
      -0.25,
      delta,
      8
    );

    setBoneTarget(
      "rightLowerArm",
      -1.1,
      0,
      0.25,
      delta,
      8
    );

    setBoneTarget(
      "head",
      0.035,
      0,
      0,
      delta,
      6
    );
  }

  // ----------------------------------------------------------
  // Phase 4:
  // Hands return to formal position.
  // ----------------------------------------------------------

  else {
    formalPosture(delta);

    setBoneTarget(
      "head",
      Math.sin(time * 0.8) * 0.01,
      0,
      0,
      delta,
      5
    );
  }
}

// ============================================================
// LISTENING
// ============================================================

function animateListening(
  time,
  delta
) {
  formalPosture(delta);

  // Slight forward attention.
  setBoneTarget(
    "neck",
    -0.025,
    0,
    0,
    delta,
    5
  );

  // Natural small nod.
  setBoneTarget(
    "head",
    -0.025 +
    Math.sin(time * 1.7) * 0.025,
    Math.sin(time * 0.8) * 0.025,
    0,
    delta,
    5
  );

  // Slight chest attention.
  setBoneTarget(
    "chest",
    0.012,
    0,
    0,
    delta,
    4
  );
}

// ============================================================
// THINKING
// ============================================================

function animateThinking(
  time,
  delta
) {
  formalPosture(delta);

  // Thoughtful head tilt.
  setBoneTarget(
    "head",
    -0.035,
    0.02,
    Math.sin(time * 0.7) * 0.09,
    delta,
    5
  );

  setBoneTarget(
    "neck",
    0,
    0,
    Math.sin(time * 0.6) * 0.035,
    delta,
    4
  );

  // Small body shift.
  setBoneTarget(
    "chest",
    0,
    Math.sin(time * 0.5) * 0.02,
    0,
    delta,
    4
  );
}

// ============================================================
// SPEAKING
// ============================================================

function animateSpeaking(
  time,
  delta
) {
  formalPosture(delta);

  // Natural conversational head movement.
  setBoneTarget(
    "neck",
    Math.sin(time * 2.2) * 0.018,
    Math.sin(time * 1.3) * 0.035,
    Math.sin(time * 1.1) * 0.015,
    delta,
    6
  );

  setBoneTarget(
    "head",
    Math.sin(time * 3.0) * 0.025,
    Math.sin(time * 1.7) * 0.035,
    Math.sin(time * 1.4) * 0.018,
    delta,
    6
  );

  // Small speaking body movement.
  setBoneTarget(
    "chest",
    Math.sin(time * 2.8) * 0.018,
    Math.sin(time * 1.5) * 0.012,
    0,
    delta,
    5
  );
}

// ============================================================
// VISITOR LEFT
// ============================================================

function animateVisitorLeft(
  time,
  delta
) {
  formalPosture(delta);

  // Small respectful farewell head movement.
  setBoneTarget(
    "head",
    Math.sin(time * 2.2) * 0.025,
    Math.sin(time * 1.3) * 0.04,
    0,
    delta,
    5
  );
}

// ============================================================
// BODY STATE UPDATE
// ============================================================

function updateBody(
  time,
  delta
) {
  const elapsed =
    (performance.now() -
      stateChangedAt) /
    1000;

  switch (currentState) {
    case STATES.IDLE:
      animateIdle(time, delta);
      break;

    case STATES.VISITOR_DETECTED:
      animateVisitorDetected(
        time,
        delta
      );
      break;

    case STATES.GREETING:
      animateNamaskar(
        elapsed,
        time,
        delta
      );
      break;

    case STATES.LISTENING:
      animateListening(
        time,
        delta
      );
      break;

    case STATES.THINKING:
      animateThinking(
        time,
        delta
      );
      break;

    case STATES.SPEAKING:
      animateSpeaking(
        time,
        delta
      );
      break;

    case STATES.VISITOR_LEFT:
      animateVisitorLeft(
        time,
        delta
      );
      break;

    default:
      formalPosture(delta);
  }
}

// ============================================================
// FACE
// ============================================================

function updateFace(time) {
  if (!expressionManager) {
    return;
  }

  // ----------------------------------------------------------
  // Natural blinking
  // ----------------------------------------------------------

  const blinkCycle =
    time % 4.8;

  let blink = 0;

  if (
    blinkCycle > 4.35 &&
    blinkCycle < 4.50
  ) {
    blink = 1;
  }

  expressionManager.setValue(
    "blink",
    blink
  );

  // ----------------------------------------------------------
  // Mouth
  // ----------------------------------------------------------

  let mouth = 0;

  if (currentState === STATES.SPEAKING) {
    mouth =
      0.25 +
      Math.abs(
        Math.sin(time * 9)
      ) *
      0.55;
  }

  expressionManager.setValue(
    "aa",
    mouth
  );

  expressionManager.setValue(
    "ih",
    mouth * 0.35
  );

  expressionManager.setValue(
    "ou",
    mouth * 0.25
  );

  expressionManager.setValue(
    "ee",
    mouth * 0.20
  );

  expressionManager.update();
}

// ============================================================
// EYE / FACE ATTENTION
// ============================================================

function updateLookAt(time, delta) {
  if (!vrm?.lookAt) {
    return;
  }

  let x = 0;
  let y = 1.45;

  switch (currentState) {
    case STATES.IDLE:
      x = Math.sin(time * 0.25) * 0.05;
      y = 1.45;
      break;

    case STATES.VISITOR_DETECTED:
      x = 0;
      y = 1.50;
      break;

    case STATES.GREETING:
      x = 0;
      y = 1.48;
      break;

    case STATES.LISTENING:
      x = Math.sin(time * 0.7) * 0.04;
      y = 1.48;
      break;

    case STATES.THINKING:
      x = Math.sin(time * 0.35) * 0.10;
      y = 1.55;
      break;

    case STATES.SPEAKING:
      x = Math.sin(time * 0.9) * 0.04;
      y = 1.47;
      break;

    case STATES.VISITOR_LEFT:
      x = Math.sin(time * 0.5) * 0.06;
      y = 1.40;
      break;

    default:
      break;
  }

  lookTarget.position.x = x;
  lookTarget.position.y = y;

  vrm.lookAt.update(delta);
}

// ============================================================
// IMPORTANT VRM UPDATE POLICY
// ============================================================
//
// DO NOT:
//
//     vrm.update(delta)
//
// because that can update SpringBone systems.
//
// We intentionally update:
//
//     humanoid
//     lookAt
//     expressionManager
//
// Clothing remains stable.
// ============================================================

function updateHumanoid() {
  if (!vrm?.humanoid) {
    return;
  }

  if (
    typeof vrm.humanoid.update ===
    "function"
  ) {
    vrm.humanoid.update();
  }
}

// ============================================================
// WEBSOCKET
// ============================================================

let socket = null;

let reconnectTimer = null;

function connectReception() {
  if (
    socket &&
    (
      socket.readyState ===
      WebSocket.OPEN ||
      socket.readyState ===
      WebSocket.CONNECTING
    )
  ) {
    return;
  }

  console.log(
    `[WEBSOCKET] Connecting to ${WS_URL}`
  );

  try {
    socket = new WebSocket(
      WS_URL
    );
  } catch (error) {
    console.error(
      "WebSocket creation failed:",
      error
    );

    scheduleReconnect();

    return;
  }

  socket.onopen = () => {
    console.log(
      "[WEBSOCKET] Connected"
    );
  };

  socket.onmessage = (event) => {
    try {
      const data =
        JSON.parse(event.data);

      console.log(
        "[WEBSOCKET] Message:",
        data
      );

      if (
        data.type ===
        "avatar_state"
      ) {
        setAvatarState(
          data.state
        );
      }
    } catch (error) {
      console.error(
        "Invalid WebSocket data:",
        error
      );
    }
  };

  socket.onerror = () => {
    console.warn(
      "[WEBSOCKET] Connection error"
    );
  };

  socket.onclose = () => {
    console.log(
      "[WEBSOCKET] Disconnected"
    );

    scheduleReconnect();
  };
}

function scheduleReconnect() {
  clearTimeout(
    reconnectTimer
  );

  reconnectTimer =
    setTimeout(() => {
      connectReception();
    }, 2000);
}

connectReception();

// ============================================================
// AUTOMATIC DEMO
// ============================================================
//
// This allows you to verify every animation without
// Python physical_reception.py.
//
// Sequence:
//
// IDLE
// ↓
// VISITOR DETECTED
// ↓
// NAMASKAR
// ↓
// LISTENING
// ↓
// THINKING
// ↓
// SPEAKING
// ↓
// VISITOR LEFT
// ↓
// IDLE
//
// ============================================================

const DEMO_SEQUENCE = [
  {
    state: STATES.IDLE,
    duration: 4000,
  },

  {
    state: STATES.VISITOR_DETECTED,
    duration: 2500,
  },

  {
    state: STATES.GREETING,
    duration: 4200,
  },

  {
    state: STATES.LISTENING,
    duration: 4000,
  },

  {
    state: STATES.THINKING,
    duration: 3500,
  },

  {
    state: STATES.SPEAKING,
    duration: 7000,
  },

  {
    state: STATES.LISTENING,
    duration: 3500,
  },

  {
    state: STATES.VISITOR_LEFT,
    duration: 3000,
  },
];

let demoIndex = 0;

let demoTimer = null;

function startDemo() {
  if (!AUTO_DEMO) {
    return;
  }

  clearTimeout(demoTimer);

  const item =
    DEMO_SEQUENCE[demoIndex];

  setAvatarState(
    item.state
  );

  demoTimer =
    setTimeout(() => {
      demoIndex =
        (demoIndex + 1) %
        DEMO_SEQUENCE.length;

      startDemo();
    }, item.duration);
}

// Only run automatic demo if
// Python has not yet taken control.

if (AUTO_DEMO) {
  setTimeout(() => {
    startDemo();
  }, 1500);
}

// ============================================================
// ANIMATION LOOP
// ============================================================

const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(
    animate
  );

  const delta = Math.min(
    clock.getDelta(),
    0.05
  );

  const time =
    clock.elapsedTime;

  if (vrm) {
    updateBody(
      time,
      delta
    );

    updateFace(
      time
    );

    updateLookAt(
      time,
      delta
    );

    updateHumanoid();
  }

  renderer.render(
    scene,
    camera
  );
}

animate();

// ============================================================
// RESIZE
// ============================================================

window.addEventListener(
  "resize",
  () => {
    camera.aspect =
      window.innerWidth /
      window.innerHeight;

    camera.updateProjectionMatrix();

    renderer.setSize(
      window.innerWidth,
      window.innerHeight
    );
  }
);