import sys
import time
from pathlib import Path


# ---------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from vision.reception.reception_controller import (
    ReceptionController,
    ReceptionState,
)


def print_status(controller):
    """
    Print the current reception controller status.
    """

    status = controller.get_status()

    print()
    print("-" * 50)

    print(
        f"State: "
        f"{status['state']}"
    )

    print(
        f"Active visitors: "
        f"{status['active_visitors']}"
    )

    print(
        f"Primary visitor: "
        f"{status['primary_visitor_id']}"
    )

    print(
        f"State duration: "
        f"{status['state_duration']:.2f}s"
    )

    print("-" * 50)


def main():

    print("=" * 60)
    print("AI RECEPTION - PHASE 3")
    print("Reception Controller Test")
    print("=" * 60)

    controller = ReceptionController(
        greeting_delay=1.0,
        visitor_timeout=2.0,
    )

    # ---------------------------------------------------------
    # TEST 1
    # Initial state
    # ---------------------------------------------------------

    print("\n[TEST 1] Initial state")

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.IDLE
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 2
    # Visitor enters
    # ---------------------------------------------------------

    print("\n[TEST 2] Visitor #1 enters")

    controller.update_visitors([1])

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.VISITOR_DETECTED
    )

    assert (
        controller.get_primary_visitor_id()
        == 1
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 3
    # Wait for greeting
    # ---------------------------------------------------------

    print(
        "\n[TEST 3] Waiting for greeting..."
    )

    time.sleep(1.2)

    controller.update_visitors([1])

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.GREETING
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 4
    # Start listening
    # ---------------------------------------------------------

    print(
        "\n[TEST 4] Reception starts listening"
    )

    controller.start_listening()

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.LISTENING
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 5
    # AI starts thinking
    # ---------------------------------------------------------

    print(
        "\n[TEST 5] AI starts thinking"
    )

    controller.start_thinking()

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.THINKING
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 6
    # TTS starts speaking
    # ---------------------------------------------------------

    print(
        "\n[TEST 6] Reception starts speaking"
    )

    controller.start_speaking()

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.SPEAKING
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 7
    # Return to listening
    # ---------------------------------------------------------

    print(
        "\n[TEST 7] Return to listening"
    )

    controller.return_to_listening()

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.LISTENING
    )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 8
    # Visitor disappears
    # ---------------------------------------------------------

    print(
        "\n[TEST 8] Visitor #1 disappears"
    )

    controller.update_visitors([])

    print(
        "Waiting for visitor timeout..."
    )

    time.sleep(2.2)

    controller.update_visitors([])

    print_status(controller)

    assert (
        controller.get_state()
        == ReceptionState.IDLE
    )

    assert (
        controller.get_primary_visitor_id()
        is None
    )

    assert (
        controller.get_active_visitor_count()
        == 0
    )

    print("PASS")

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("ALL PHASE 3 TESTS PASSED")
    print("Reception Controller is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    main()