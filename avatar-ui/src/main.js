import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { VRMLoaderPlugin } from "@pixiv/three-vrm";

import "./style.css";


// ============================================================
// BASIC SETUP
// ============================================================

const canvas = document.getElementById("avatar-canvas");
const statusElement = document.getElementById("status");
const stateLabel = document.getElementById("state-label");

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  28,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);

camera.position.set(0, 1.35, 3.0);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: true,
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;


// ============================================================
// LIGHTING
// ============================================================

const ambientLight = new THREE.AmbientLight(0xffffff, 2.2);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.0);
keyLight.position.set(1.5, 2.5, 3);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 1.0);
fillLight.position.set(-2, 1.5, 2);
scene.add(fillLight);


// ============================================================
// LOOK-AT TARGET
// ============================================================

const visitorTarget = new THREE.Object3D();

visitorTarget.position.set(
  0,
  1.45,
  2.5
);

scene.add(visitorTarget);


// ============================================================
// GLOBAL VARIABLES
// ============================================================

let vrm = null;
let clock = new THREE.Clock();

let currentState = "idle";
let targetState = "idle";

let demoRunning = false;
let demoTimer = null;

let speechTimer = null;
let blinkTimer = null;
let nextBlinkTime = 2.5;

let namasteProgress = 0;

let attentionTarget = {
  x: 0,
  y: 1.45,
  z: 2.5,
};


// ============================================================
// HUMANOID BONES
// ============================================================

const bones = {};

const REQUIRED_BONES = [
  "head",
  "neck",
  "spine",
  "chest",
  "upperChest",

  "leftShoulder",
  "leftUpperArm",
  "leftLowerArm",
  "leftHand",

  "rightShoulder",
  "rightUpperArm",
  "rightLowerArm",
  "rightHand",
];


// ============================================================
// ANIMATION POSES
// ============================================================

/*
    Important:

    These are normalized humanoid rotations.

    Normalized VRM bones are standardized by three-vrm,
    which makes this much more reliable than manipulating
    the raw model bones directly.
*/


const POSES = {

  // --------------------------------------------------------
  // PROFESSIONAL RECEPTIONIST
  // --------------------------------------------------------

  idle: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.05 },
    leftUpperArm: { x: 0.00, y: 0.00, z: -0.90 },
    leftLowerArm: { x: 0.00, y: 0.00, z: -0.18 },
    leftHand: { x: 0.00, y: 0.00, z: 0.00 },

    rightShoulder: { x: 0.00, y: 0.00, z: 0.05 },
    rightUpperArm: { x: 0.00, y: 0.00, z: 0.90 },
    rightLowerArm: { x: 0.00, y: 0.00, z: 0.18 },
    rightHand: { x: 0.00, y: 0.00, z: 0.00 },

    spine: { x: 0.00, y: 0.00, z: 0.00 },
    chest: { x: 0.00, y: 0.00, z: 0.00 },
    upperChest: { x: 0.00, y: 0.00, z: 0.00 },

    head: { x: 0.00, y: 0.00, z: 0.00 },
    neck: { x: 0.00, y: 0.00, z: 0.00 },
  },


  // --------------------------------------------------------
  // LISTENING
  // --------------------------------------------------------

  listening: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.12 },
    leftUpperArm: { x: 0.00, y: 0.00, z: -0.82 },
    leftLowerArm: { x: -0.18, y: 0.00, z: -0.28 },

    rightShoulder: { x: 0.00, y: 0.00, z: 0.12 },
    rightUpperArm: { x: 0.00, y: 0.00, z: 0.82 },
    rightLowerArm: { x: -0.18, y: 0.00, z: 0.28 },

    spine: { x: 0.015, y: 0.00, z: 0.00 },
    chest: { x: 0.015, y: 0.00, z: 0.00 },

    head: { x: -0.025, y: 0.00, z: 0.00 },
    neck: { x: 0.015, y: 0.00, z: 0.00 },
  },


  // --------------------------------------------------------
  // THINKING
  // --------------------------------------------------------

  thinking: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.08 },
    leftUpperArm: { x: 0.00, y: 0.00, z: -0.90 },
    leftLowerArm: { x: -0.30, y: 0.00, z: -0.35 },

    rightShoulder: { x: 0.00, y: 0.00, z: 0.08 },
    rightUpperArm: { x: 0.00, y: 0.00, z: 0.90 },
    rightLowerArm: { x: -0.30, y: 0.00, z: 0.35 },

    spine: { x: 0.02, y: 0.00, z: 0.00 },
    chest: { x: 0.02, y: 0.00, z: 0.00 },

    head: { x: 0.10, y: 0.12, z: 0.02 },
    neck: { x: -0.04, y: 0.04, z: 0.00 },
  },


  // --------------------------------------------------------
  // SPEAKING
  // --------------------------------------------------------

  speaking: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.08 },
    leftUpperArm: { x: 0.00, y: 0.00, z: -0.90 },
    leftLowerArm: { x: -0.15, y: 0.00, z: -0.22 },

    rightShoulder: { x: 0.00, y: 0.00, z: 0.08 },
    rightUpperArm: { x: 0.00, y: 0.00, z: 0.90 },
    rightLowerArm: { x: -0.15, y: 0.00, z: 0.22 },

    spine: { x: 0.00, y: 0.015, z: 0.00 },
    chest: { x: 0.00, y: 0.015, z: 0.00 },

    head: { x: -0.015, y: 0.00, z: 0.00 },
    neck: { x: 0.00, y: 0.00, z: 0.00 },
  },


  // --------------------------------------------------------
  // NAMASTE
  // --------------------------------------------------------

  namaste: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.35 },

    leftUpperArm: {
      x: 0.00,
      y: 0.00,
      z: -1.45,
    },

    leftLowerArm: {
      x: -0.95,
      y: 0.00,
      z: -0.85,
    },

    leftHand: {
      x: 0.00,
      y: 0.00,
      z: -0.30,
    },


    rightShoulder: { x: 0.00, y: 0.00, z: 0.35 },

    rightUpperArm: {
      x: 0.00,
      y: 0.00,
      z: 1.45,
    },

    rightLowerArm: {
      x: -0.95,
      y: 0.00,
      z: 0.85,
    },

    rightHand: {
      x: 0.00,
      y: 0.00,
      z: 0.30,
    },


    spine: {
      x: 0.04,
      y: 0.00,
      z: 0.00,
    },

    chest: {
      x: 0.04,
      y: 0.00,
      z: 0.00,
    },

    head: {
      x: 0.20,
      y: 0.00,
      z: 0.00,
    },

    neck: {
      x: 0.05,
      y: 0.00,
      z: 0.00,
    },
  },


  // --------------------------------------------------------
  // VISITOR DETECTED
  // --------------------------------------------------------

  visitor_detected: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.05 },
    leftUpperArm: { x: 0.00, y: 0.00, z: -0.90 },
    leftLowerArm: { x: 0.00, y: 0.00, z: -0.18 },

    rightShoulder: { x: 0.00, y: 0.00, z: 0.05 },
    rightUpperArm: { x: 0.00, y: 0.00, z: 0.90 },
    rightLowerArm: { x: 0.00, y: 0.00, z: 0.18 },

    head: { x: 0.00, y: 0.12, z: 0.00 },
    neck: { x: 0.00, y: 0.05, z: 0.00 },

    spine: { x: 0.00, y: 0.02, z: 0.00 },
    chest: { x: 0.00, y: 0.02, z: 0.00 },
  },


  // --------------------------------------------------------
  // VISITOR LEFT
  // --------------------------------------------------------

  visitor_left: {

    leftShoulder: { x: 0.00, y: 0.00, z: -0.05 },
    leftUpperArm: { x: 0.00, y: 0.00, z: -0.90 },
    leftLowerArm: { x: 0.00, y: 0.00, z: -0.18 },

    rightShoulder: { x: 0.00, y: 0.00, z: 0.05 },
    rightUpperArm: { x: 0.00, y: 0.00, z: 0.90 },
    rightLowerArm: { x: 0.00, y: 0.00, z: 0.18 },

    head: { x: 0.00, y: -0.08, z: 0.00 },
    neck: { x: 0.00, y: -0.03, z: 0.00 },

    spine: { x: 0.00, y: -0.015, z: 0.00 },
    chest: { x: 0.00, y: -0.015, z: 0.00 },
  },
};


// ============================================================
// CURRENT / TARGET BONE ROTATIONS
// ============================================================

const currentPose = {};
const targetPose = {};


// ============================================================
// HELPER
// ============================================================

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}


function lerpAngle(current, target, amount) {
  return current + (target - current) * amount;
}


function createRotation(data = {}) {
  return {
    x: data.x || 0,
    y: data.y || 0,
    z: data.z || 0,
  };
}


// ============================================================
// FIND BONE
// ============================================================

function getBone(name) {

  if (!vrm || !vrm.humanoid) {
    return null;
  }

  const bone = vrm.humanoid.getNormalizedBoneNode(name);

  return bone || null;
}


// ============================================================
// BUILD BONE MAP
// ============================================================

function initializeBones() {

  console.log("");
  console.log("==========================================");
  console.log("VRM HUMANOID BONE DIAGNOSTICS");
  console.log("==========================================");

  for (const name of REQUIRED_BONES) {

    const bone = getBone(name);

    bones[name] = bone;

    if (bone) {

      console.log(`✓ ${name}`);

      currentPose[name] = createRotation({
        x: bone.rotation.x,
        y: bone.rotation.y,
        z: bone.rotation.z,
      });

      targetPose[name] = createRotation({
        x: bone.rotation.x,
        y: bone.rotation.y,
        z: bone.rotation.z,
      });

    } else {

      console.warn(`✗ MISSING: ${name}`);
    }
  }

  console.log("==========================================");
  console.log("");


  const availableCount = Object.values(bones)
    .filter(Boolean)
    .length;

  console.log(
    `Humanoid bones available: ${availableCount}/${REQUIRED_BONES.length}`
  );


  if (availableCount < 8) {

    console.error(
      "WARNING: This VRM has too few humanoid bones mapped."
    );

  } else {

    console.log(
      "VRM humanoid mapping looks usable."
    );
  }
}


// ============================================================
// SET TARGET POSE
// ============================================================

function setTargetPose(poseName) {

  const pose = POSES[poseName];

  if (!pose) {
    console.warn(`Unknown pose: ${poseName}`);
    return;
  }


  for (const boneName of Object.keys(currentPose)) {

    const target = pose[boneName];

    if (!target) {
      continue;
    }

    targetPose[boneName] = createRotation(target);
  }
}


// ============================================================
// SMOOTH POSE
// ============================================================

function updatePose(delta) {

  const speed = 7.0;

  const amount = clamp(
    delta * speed,
    0,
    1
  );


  for (const boneName of Object.keys(bones)) {

    const bone = bones[boneName];

    if (!bone) {
      continue;
    }


    const current = currentPose[boneName];

    const target = targetPose[boneName];

    if (!current || !target) {
      continue;
    }


    current.x = lerpAngle(
      current.x,
      target.x,
      amount
    );

    current.y = lerpAngle(
      current.y,
      target.y,
      amount
    );

    current.z = lerpAngle(
      current.z,
      target.z,
      amount
    );


    bone.rotation.set(
      current.x,
      current.y,
      current.z
    );
  }


  /*
      IMPORTANT:

      This updates normalized humanoid bones -> raw VRM bones.

      We intentionally do NOT call:

          vrm.update(delta)

      because that would also update SpringBone physics,
      which causes the clothing/hair movement we do not want.
  */

  if (vrm && vrm.humanoid) {
    vrm.humanoid.update();
  }
}


// ============================================================
// LOOK AT VISITOR
// ============================================================

function updateVisitorAttention(delta) {

  if (!vrm || !vrm.lookAt) {
    return;
  }


  const targetPosition = new THREE.Vector3(
    attentionTarget.x,
    attentionTarget.y,
    attentionTarget.z
  );


  visitorTarget.position.lerp(
    targetPosition,
    clamp(delta * 4.0, 0, 1)
  );


  vrm.lookAt.target = visitorTarget;

  vrm.lookAt.autoUpdate = true;

  vrm.lookAt.update(delta);
}


// ============================================================
// HEAD NATURAL MOVEMENT
// ============================================================

function updateNaturalHeadMovement(time) {

  const head = bones.head;
  const neck = bones.neck;

  if (!head) {
    return;
  }


  let movementAmount = 0.015;

  if (currentState === "speaking") {
    movementAmount = 0.025;
  }

  if (currentState === "thinking") {
    movementAmount = 0.035;
  }

  if (currentState === "listening") {
    movementAmount = 0.018;
  }


  const movementX =
    Math.sin(time * 1.25) * movementAmount;

  const movementZ =
    Math.sin(time * 0.85) * movementAmount * 0.5;


  head.rotation.x += movementX;
  head.rotation.z += movementZ;


  if (neck) {

    neck.rotation.x += movementX * 0.35;
    neck.rotation.z += movementZ * 0.35;
  }
}


// ============================================================
// THINKING MOVEMENT
// ============================================================

function updateThinkingMovement(time) {

  if (currentState !== "thinking") {
    return;
  }


  const head = bones.head;

  if (!head) {
    return;
  }


  const thinkingMovement =
    Math.sin(time * 1.7) * 0.05;


  head.rotation.y += thinkingMovement;
}


// ============================================================
// SPEAKING MOVEMENT
// ============================================================

function updateSpeakingMovement(time) {

  if (currentState !== "speaking") {
    return;
  }


  const chest = bones.chest;

  if (!chest) {
    return;
  }


  const movement =
    Math.sin(time * 3.0) * 0.018;


  chest.rotation.y += movement;
}


// ============================================================
// EXPRESSIONS
// ============================================================

function setExpression(name, value) {

  if (!vrm || !vrm.expressionManager) {
    return;
  }


  try {

    vrm.expressionManager.setValue(
      name,
      clamp(value, 0, 1)
    );

  } catch (error) {

    // Expression may not exist on this VRM.
  }
}


// ============================================================
// EXPRESSION AVAILABILITY
// ============================================================

function inspectExpressions() {

  if (!vrm || !vrm.expressionManager) {

    console.warn(
      "This VRM has no expression manager."
    );

    return;
  }


  console.log("");
  console.log("==========================================");
  console.log("VRM EXPRESSIONS");
  console.log("==========================================");


  try {

    const expressions =
      vrm.expressionManager.expressions;

    if (expressions) {

      expressions.forEach(
        (expression, index) => {

          console.log(
            `[${index}]`,
            expression.name
          );
        }
      );
    }

  } catch (error) {

    console.warn(
      "Unable to inspect expressions."
    );
  }


  console.log("==========================================");
}


// ============================================================
// BLINKING
// ============================================================

function updateBlink(time) {

  if (time < nextBlinkTime) {
    return;
  }


  let blinkStart = time;


  function performBlink() {

    const elapsed = performance.now() / 1000 - blinkStart;

    if (elapsed < 0.08) {

      const value = elapsed / 0.08;

      setExpression("blink", value);

    } else if (elapsed < 0.16) {

      const value =
        1 - ((elapsed - 0.08) / 0.08);

      setExpression("blink", value);

    } else {

      setExpression("blink", 0);

      nextBlinkTime =
        time +
        2.5 +
        Math.random() * 4.0;

      return;
    }


    requestAnimationFrame(performBlink);
  }


  performBlink();
}


// ============================================================
// MOUTH ANIMATION
// ============================================================

function updateMouth(time) {

  if (currentState !== "speaking") {

    setExpression("aa", 0);
    setExpression("ih", 0);
    setExpression("ou", 0);
    setExpression("ee", 0);
    setExpression("oh", 0);

    return;
  }


  const wave =
    Math.abs(Math.sin(time * 7.0));


  const wave2 =
    Math.abs(Math.sin(time * 4.5));


  setExpression(
    "aa",
    wave * 0.55
  );

  setExpression(
    "ih",
    wave2 * 0.20
  );

  setExpression(
    "ou",
    Math.abs(Math.sin(time * 5.5)) * 0.15
  );
}


// ============================================================
// SMOOTH NAMASTE ANIMATION
// ============================================================

function updateNamaste(time, delta) {

  if (currentState !== "greeting") {

    namasteProgress = 0;

    return;
  }


  /*
      0 -> 0.8 sec
      Arms move to Namaste + head bow.

      0.8 -> 2.0 sec
      Hold Namaste.

      2.0 -> 2.8 sec
      Return to formal position.
  */


  const greetingDuration = 2.8;

  namasteProgress += delta;


  if (namasteProgress <= 0.8) {

    setTargetPose("namaste");

  } else if (namasteProgress <= 2.0) {

    setTargetPose("namaste");

  } else if (namasteProgress <= greetingDuration) {

    setTargetPose("idle");

  } else {

    currentState = "listening";

    targetState = "listening";

    setTargetPose("listening");

    updateStateUI();
  }
}


// ============================================================
// STATE MANAGEMENT
// ============================================================

function setState(state) {

  const validStates = [
    "idle",
    "visitor_detected",
    "greeting",
    "listening",
    "thinking",
    "speaking",
    "visitor_left",
  ];


  if (!validStates.includes(state)) {

    console.warn(
      `Invalid avatar state: ${state}`
    );

    return;
  }


  currentState = state;
  targetState = state;


  if (state === "greeting") {

    namasteProgress = 0;

    setTargetPose("namaste");

  } else {

    setTargetPose(state);
  }


  updateStateUI();

  console.log(
    `Avatar state -> ${state}`
  );
}


// ============================================================
// STATE UI
// ============================================================

function updateStateUI() {

  if (!stateLabel) {
    return;
  }


  stateLabel.textContent =
    currentState.replaceAll("_", " ").toUpperCase();


  if (!statusElement) {
    return;
  }


  const messages = {

    idle:
      "Ready to welcome visitors.",

    visitor_detected:
      "Visitor detected. Paying attention.",

    greeting:
      "Namaste. Welcome to our reception.",

    listening:
      "Listening to the visitor.",

    thinking:
      "Thinking about the request.",

    speaking:
      "Speaking with the visitor.",

    visitor_left:
      "Visitor leaving. Returning to standby.",
  };


  statusElement.textContent =
    messages[currentState] ||
    "AI Receptionist";


  statusElement.dataset.type = "ready";
}


// ============================================================
// AUTOMATIC DEMO
// ============================================================

function stopAutomaticDemo() {

  demoRunning = false;

  if (demoTimer) {

    clearTimeout(demoTimer);

    demoTimer = null;
  }
}


function scheduleDemoStep(delay, state, nextStep) {

  demoTimer = setTimeout(() => {

    if (!demoRunning) {
      return;
    }

    setState(state);

    if (nextStep) {
      nextStep();
    }

  }, delay);
}


function startAutomaticDemo() {

  stopAutomaticDemo();

  demoRunning = true;


  console.log("");
  console.log("==========================================");
  console.log("AUTOMATIC RECEPTIONIST DEMO STARTED");
  console.log("==========================================");


  // 1. IDLE
  setState("idle");


  // 2. Visitor arrives
  scheduleDemoStep(
    2500,
    "visitor_detected"
  );


  // 3. Namaste
  scheduleDemoStep(
    5000,
    "greeting"
  );


  // 4. Listening
  scheduleDemoStep(
    8500,
    "listening"
  );


  // 5. Thinking
  scheduleDemoStep(
    12500,
    "thinking"
  );


  // 6. Speaking
  scheduleDemoStep(
    16000,
    "speaking"
  );


  // 7. Listening again
  scheduleDemoStep(
    22000,
    "listening"
  );


  // 8. Visitor leaves
  scheduleDemoStep(
    26000,
    "visitor_left"
  );


  // 9. Back to idle
  scheduleDemoStep(
    30000,
    "idle",
    () => {

      if (demoRunning) {

        demoTimer = setTimeout(
          startAutomaticDemo,
          3000
        );
      }
    }
  );
}


// ============================================================
// DEBUG CONTROLS
// ============================================================

window.setAvatarState = function (state) {

  stopAutomaticDemo();

  setState(state);
};


window.playNamaste = function () {

  stopAutomaticDemo();

  setState("greeting");
};


window.startSpeaking = function () {

  stopAutomaticDemo();

  setState("speaking");
};


window.stopSpeaking = function () {

  setExpression("aa", 0);
  setExpression("ih", 0);
  setExpression("ou", 0);
  setExpression("ee", 0);
  setExpression("oh", 0);

  setState("listening");
};


window.attendVisitor = function () {

  stopAutomaticDemo();

  attentionTarget = {
    x: 0.35,
    y: 1.5,
    z: 2.5,
  };

  setState("visitor_detected");
};


window.setFormalPose = function () {

  stopAutomaticDemo();

  setState("idle");
};


window.startReceptionDemo = function () {

  startAutomaticDemo();
};


window.stopReceptionDemo = function () {

  stopAutomaticDemo();

  setState("idle");
};


// ============================================================
// VRM LOADING
// ============================================================

async function loadVRM() {

  statusElement.textContent =
    "Loading receptionist avatar...";

  statusElement.dataset.type = "loading";


  const loader = new GLTFLoader();

  loader.register(
    (parser) => new VRMLoaderPlugin(parser)
  );


  try {

    const gltf = await loader.loadAsync(
      "/models/receptionist.vrm"
    );


    vrm = gltf.userData.vrm;


    if (!vrm) {

      throw new Error(
        "VRM model was loaded but VRM data was not found."
      );
    }


    console.log(
      "VRM avatar loaded successfully."
    );


    // ----------------------------------------------------
    // MODEL ORIENTATION
    // ----------------------------------------------------

    vrm.scene.rotation.y = 0;


    // ----------------------------------------------------
    // CENTER MODEL
    // ----------------------------------------------------

    const box =
      new THREE.Box3().setFromObject(
        vrm.scene
      );


    const center =
      box.getCenter(
        new THREE.Vector3()
      );


    const size =
      box.getSize(
        new THREE.Vector3()
      );


    vrm.scene.position.x =
      -center.x;


    vrm.scene.position.y =
      -box.min.y;


    vrm.scene.position.z =
      -center.z;


    scene.add(vrm.scene);


    // ----------------------------------------------------
    // HUMANOID
    // ----------------------------------------------------

    if (vrm.humanoid) {

      /*
          We control normalized bones ourselves.

          The humanoid synchronizes those normalized
          bones to the actual VRM model.
      */

      vrm.humanoid.autoUpdateHumanBones = true;
    }


    // ----------------------------------------------------
    // LOOK AT
    // ----------------------------------------------------

    if (vrm.lookAt) {

      vrm.lookAt.target =
        visitorTarget;

      vrm.lookAt.autoUpdate = true;

      console.log(
        "VRM LookAt system available."
      );

    } else {

      console.warn(
        "VRM LookAt system is not available."
      );
    }


    // ----------------------------------------------------
    // DIAGNOSTICS
    // ----------------------------------------------------

    initializeBones();

    inspectExpressions();


    // ----------------------------------------------------
    // INITIAL STATE
    // ----------------------------------------------------

    setState("idle");


    statusElement.textContent =
      "Receptionist ready.";

    statusElement.dataset.type = "ready";


    console.log("");
    console.log(
      "=========================================="
    );
    console.log(
      "AVATAR SYSTEM READY"
    );
    console.log(
      "=========================================="
    );


  } catch (error) {

    console.error(
      "Failed to load VRM:",
      error
    );


    statusElement.textContent =
      "Failed to load receptionist avatar.";

    statusElement.dataset.type = "error";
  }
}


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


// ============================================================
// MAIN ANIMATION LOOP
// ============================================================

function animate() {

  requestAnimationFrame(animate);


  const delta =
    Math.min(
      clock.getDelta(),
      0.05
    );


  const elapsed =
    clock.elapsedTime;


  if (!vrm) {

    renderer.render(
      scene,
      camera
    );

    return;
  }


  // --------------------------------------------------------
  // NAMASTE
  // --------------------------------------------------------

  updateNamaste(
    elapsed,
    delta
  );


  // --------------------------------------------------------
  // SMOOTH BODY POSE
  // --------------------------------------------------------

  updatePose(delta);


  // --------------------------------------------------------
  // NATURAL HEAD
  // --------------------------------------------------------

  updateNaturalHeadMovement(
    elapsed
  );


  // --------------------------------------------------------
  // THINKING
  // --------------------------------------------------------

  updateThinkingMovement(
    elapsed
  );


  // --------------------------------------------------------
  // SPEAKING
  // --------------------------------------------------------

  updateSpeakingMovement(
    elapsed
  );


  // --------------------------------------------------------
  // VISITOR ATTENTION / EYES
  // --------------------------------------------------------

  updateVisitorAttention(
    delta
  );


  // --------------------------------------------------------
  // MOUTH
  // --------------------------------------------------------

  updateMouth(
    elapsed
  );


  // --------------------------------------------------------
  // BLINK
  // --------------------------------------------------------

  updateBlink(
    elapsed
  );


  // --------------------------------------------------------
  // EXPRESSIONS
  // --------------------------------------------------------

  if (vrm.expressionManager) {

    vrm.expressionManager.update();
  }


  // --------------------------------------------------------
  // RENDER
  // --------------------------------------------------------

  renderer.render(
    scene,
    camera
  );
}


// ============================================================
// START
// ============================================================

loadVRM();

animate();