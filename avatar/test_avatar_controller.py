import sys
from pathlib import Path


# ---------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from avatar.controller.avatar_controller import (
    AvatarController,
    AvatarState,
)


def main():

    print("=" * 60)
    print("AI RECEPTION - PHASE 8")
    print("Avatar Controller")
    print("=" * 60)

    avatar = AvatarController()

    # -----------------------------------------------------
    # TEST 1
    # -----------------------------------------------------

    print("\n[TEST 1] Initial avatar state")

    if avatar.get_state() != "idle":
        print("FAILED")
        return

    print("State: idle")
    print("Animation:", avatar.get_animation())
    print("PASS")

    # -----------------------------------------------------
    # TEST 2
    # -----------------------------------------------------

    print("\n[TEST 2] Visitor detected")

    avatar.set_state(
        AvatarState.VISITOR_DETECTED
    )

    print("State:", avatar.get_state())
    print("Animation:", avatar.get_animation())

    if avatar.get_state() != "visitor_detected":
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # TEST 3
    # -----------------------------------------------------

    print("\n[TEST 3] Greeting")

    avatar.set_state(
        AvatarState.GREETING
    )

    print("State:", avatar.get_state())
    print("Animation:", avatar.get_animation())

    if avatar.get_animation() != "greeting":
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # TEST 4
    # -----------------------------------------------------

    print("\n[TEST 4] Listening")

    avatar.set_state(
        AvatarState.LISTENING
    )

    print("State:", avatar.get_state())
    print("Animation:", avatar.get_animation())
    print("Listening:", avatar.is_listening())

    if not avatar.is_listening():
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # TEST 5
    # -----------------------------------------------------

    print("\n[TEST 5] Thinking")

    avatar.set_state(
        AvatarState.THINKING
    )

    print("State:", avatar.get_state())
    print("Animation:", avatar.get_animation())
    print("Thinking:", avatar.is_thinking())

    if not avatar.is_thinking():
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # TEST 6
    # -----------------------------------------------------

    print("\n[TEST 6] Speaking")

    avatar.set_state(
        AvatarState.SPEAKING
    )

    print("State:", avatar.get_state())
    print("Animation:", avatar.get_animation())
    print("Speaking:", avatar.is_speaking())

    if not avatar.is_speaking():
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # TEST 7
    # -----------------------------------------------------

    print("\n[TEST 7] Visitor leaves")

    avatar.set_state(
        AvatarState.VISITOR_LEFT
    )

    print("State:", avatar.get_state())
    print("Animation:", avatar.get_animation())

    if avatar.get_animation() != "idle":
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # TEST 8
    # -----------------------------------------------------

    print("\n[TEST 8] Avatar status")

    status = avatar.get_status()

    print()
    print("Avatar status:")

    for key, value in status.items():
        print(f"  {key}: {value}")

    required_keys = {
        "state",
        "animation",
        "previous_state",
        "is_listening",
        "is_thinking",
        "is_speaking",
    }

    if not required_keys.issubset(status.keys()):
        print("FAILED")
        return

    print("PASS")

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("PHASE 8 AVATAR CONTROLLER TEST COMPLETED")
    print("=" * 60)

    print()
    print("Avatar state pipeline:")
    print()
    print("IDLE")
    print("  ↓")
    print("VISITOR DETECTED")
    print("  ↓")
    print("GREETING")
    print("  ↓")
    print("LISTENING")
    print("  ↓")
    print("THINKING")
    print("  ↓")
    print("SPEAKING")
    print("  ↓")
    print("LISTENING")
    print("  ↓")
    print("VISITOR LEFT")
    print("  ↓")
    print("IDLE")

    print()
    print("Phase 8.1 complete.")
    print("Next: VRM avatar renderer")


if __name__ == "__main__":
    main()