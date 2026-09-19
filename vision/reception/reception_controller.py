from enum import Enum
from typing import Dict, List, Optional
import time


class ReceptionState(Enum):
    """
    Main state of the physical AI receptionist.
    """

    IDLE = "idle"
    VISITOR_DETECTED = "visitor_detected"
    GREETING = "greeting"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    VISITOR_LEFT = "visitor_left"


class ReceptionController:
    """
    Controls the reception state based on visitor tracking events.

    This class does NOT handle:
        - Speech recognition
        - LLM/AI reasoning
        - Text-to-speech
        - Avatar rendering

    It only manages the receptionist's state and visitor events.
    """

    def __init__(
        self,
        greeting_delay: float = 1.0,
        visitor_timeout: float = 2.0,
    ):
        self.greeting_delay = greeting_delay
        self.visitor_timeout = visitor_timeout

        self.state = ReceptionState.IDLE

        self.active_visitors: Dict[int, Dict] = {}

        self.primary_visitor_id: Optional[int] = None

        self.state_changed_at = time.time()

        self.last_event = None

    # ---------------------------------------------------------
    # State management
    # ---------------------------------------------------------

    def set_state(self, new_state: ReceptionState) -> None:
        """
        Change the receptionist state.
        """

        if self.state == new_state:
            return

        previous_state = self.state

        self.state = new_state
        self.state_changed_at = time.time()

        print(
            f"[RECEPTION] "
            f"{previous_state.value.upper()} "
            f"-> "
            f"{new_state.value.upper()}"
        )

    def get_state(self) -> ReceptionState:
        """
        Return the current reception state.
        """

        return self.state

    def get_state_name(self) -> str:
        """
        Return the current state as a string.
        """

        return self.state.value

    def get_state_duration(self) -> float:
        """
        Return how long the current state has been active.
        """

        return time.time() - self.state_changed_at

    # ---------------------------------------------------------
    # Visitor handling
    # ---------------------------------------------------------

    def update_visitors(
        self,
        visitor_ids: List[int],
    ) -> None:
        """
        Update the controller with currently visible visitor IDs.

        Example:

            [1]
            [1, 2]
            []
        """

        current_time = time.time()

        current_ids = set(visitor_ids)
        previous_ids = set(self.active_visitors.keys())

        # -----------------------------------------------------
        # Detect new visitors
        # -----------------------------------------------------

        new_visitors = current_ids - previous_ids

        for visitor_id in new_visitors:

            self.active_visitors[visitor_id] = {
                "visitor_id": visitor_id,
                "first_seen": current_time,
                "last_seen": current_time,
            }

            print(
                f"[RECEPTION] "
                f"New visitor detected: #{visitor_id}"
            )

        # -----------------------------------------------------
        # Update existing visitors
        # -----------------------------------------------------

        for visitor_id in current_ids:

            if visitor_id in self.active_visitors:

                self.active_visitors[visitor_id][
                    "last_seen"
                ] = current_time

        # -----------------------------------------------------
        # Detect visitors that disappeared
        # -----------------------------------------------------

        missing_visitors = previous_ids - current_ids

        for visitor_id in missing_visitors:

            visitor = self.active_visitors.get(
                visitor_id
            )

            if visitor is None:
                continue

            time_since_seen = (
                current_time
                - visitor["last_seen"]
            )

            if time_since_seen >= self.visitor_timeout:

                duration = (
                    visitor["last_seen"]
                    - visitor["first_seen"]
                )

                print(
                    f"[RECEPTION] "
                    f"Visitor #{visitor_id} left. "
                    f"Duration: {duration:.1f}s"
                )

                del self.active_visitors[
                    visitor_id
                ]

                self.last_event = {
                    "type": "visitor_left",
                    "visitor_id": visitor_id,
                    "duration": duration,
                    "timestamp": current_time,
                }

        # -----------------------------------------------------
        # Determine primary visitor
        # -----------------------------------------------------

        self._update_primary_visitor()

        # -----------------------------------------------------
        # Update reception state
        # -----------------------------------------------------

        self._update_state()

    # ---------------------------------------------------------
    # Primary visitor
    # ---------------------------------------------------------

    def _update_primary_visitor(self) -> None:
        """
        Select the primary visitor.

        Currently the first detected visitor is treated
        as the primary visitor.
        """

        if not self.active_visitors:

            self.primary_visitor_id = None

            return

        visitors = sorted(
            self.active_visitors.values(),
            key=lambda visitor: visitor["first_seen"],
        )

        self.primary_visitor_id = visitors[0][
            "visitor_id"
        ]

    def get_primary_visitor_id(
        self,
    ) -> Optional[int]:
        """
        Return the current primary visitor ID.
        """

        return self.primary_visitor_id

    # ---------------------------------------------------------
    # State decision
    # ---------------------------------------------------------

    def _update_state(self) -> None:
        """
        Determine the appropriate reception state.
        """

        visitor_count = len(
            self.active_visitors
        )

        # -----------------------------------------------------
        # No visitors
        # -----------------------------------------------------

        if visitor_count == 0:

            if self.state != ReceptionState.IDLE:

                self.set_state(
                    ReceptionState.IDLE
                )

            return

        # -----------------------------------------------------
        # New visitor
        # -----------------------------------------------------

        if self.state == ReceptionState.IDLE:

            self.set_state(
                ReceptionState.VISITOR_DETECTED
            )

            return

        # -----------------------------------------------------
        # Visitor detected → greeting
        # -----------------------------------------------------

        if (
            self.state
            == ReceptionState.VISITOR_DETECTED
        ):

            if (
                self.get_state_duration()
                >= self.greeting_delay
            ):

                self.set_state(
                    ReceptionState.GREETING
                )

            return

    # ---------------------------------------------------------
    # External state controls
    # ---------------------------------------------------------

    def start_listening(self) -> None:
        """
        Called when microphone/STT starts listening.
        """

        self.set_state(
            ReceptionState.LISTENING
        )

    def start_thinking(self) -> None:
        """
        Called when AI Brain starts processing.
        """

        self.set_state(
            ReceptionState.THINKING
        )

    def start_speaking(self) -> None:
        """
        Called when TTS starts speaking.
        """

        self.set_state(
            ReceptionState.SPEAKING
        )

    def return_to_listening(self) -> None:
        """
        Return to listening after speaking.
        """

        if self.primary_visitor_id is not None:

            self.set_state(
                ReceptionState.LISTENING
            )

        else:

            self.set_state(
                ReceptionState.IDLE
            )

    def finish_interaction(self) -> None:
        """
        Finish the current interaction.

        If the visitor is still present, return to listening.
        Otherwise return to idle.
        """

        if self.primary_visitor_id is not None:

            self.set_state(
                ReceptionState.LISTENING
            )

        else:

            self.set_state(
                ReceptionState.IDLE
            )

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def get_active_visitors(self) -> List[Dict]:
        """
        Return information about active visitors.
        """

        return list(
            self.active_visitors.values()
        )

    def get_active_visitor_count(self) -> int:
        """
        Return number of currently active visitors.
        """

        return len(self.active_visitors)

    def get_last_event(self):
        """
        Return the latest reception event.
        """

        event = self.last_event

        self.last_event = None

        return event

    def get_status(self) -> Dict:
        """
        Return the complete reception status.
        """

        return {
            "state": self.state.value,
            "active_visitors": (
                self.get_active_visitor_count()
            ),
            "primary_visitor_id": (
                self.primary_visitor_id
            ),
            "state_duration": (
                self.get_state_duration()
            ),
        }