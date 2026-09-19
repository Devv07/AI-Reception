from __future__ import annotations

import time
from enum import Enum
from typing import Dict, List, Optional

from vision.reception.event_bridge import VisionEventBridge


class ReceptionState(str, Enum):
    IDLE = "idle"
    VISITOR_DETECTED = "visitor_detected"
    GREETING = "greeting"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    VISITOR_LEFT = "visitor_left"


class ReceptionController:
    """
    Physical receptionist state controller.

    IMPORTANT:
    ByteTrack IDs are NOT used to determine whether the
    physical visitor is present.

    A person being detected by YOLO is enough to consider
    the visitor present.

    This prevents ByteTrack ID changes such as:

        #1 -> #2 -> #5 -> #8

    from being interpreted as different visitors.

    Phase 12.5:
    Real reception lifecycle events are forwarded to the
    shared backend integration layer through VisionEventBridge.
    """

    LOGICAL_VISITOR_ID = 1

    def __init__(
        self,
        greeting_delay: float = 1.0,
        visitor_timeout: float = 5.0,
    ):
        self.state = ReceptionState.IDLE

        self.greeting_delay = greeting_delay
        self.visitor_timeout = visitor_timeout

        # Logical visitor only.
        # We deliberately do NOT store ByteTrack IDs here.
        self.primary_visitor_id: Optional[int] = None

        # These are only informational.
        self.active_visitors: Dict[int, Dict[str, float]] = {}

        self.last_event: Optional[str] = None

        self._greeting_started_at: Optional[float] = None

        # Last time YOLO detected at least one person.
        self._last_person_seen_at: Optional[float] = None

        # Whether a person was detected in the previous update.
        self._person_was_present = False

    # =========================================================
    # EVENT INTEGRATION
    # =========================================================

    def _publish_event(
        self,
        event_type: str,
        data: Optional[dict] = None,
    ) -> None:
        """
        Publish a reception event through VisionEventBridge.

        Integration failures are isolated by the bridge and must
        never stop the physical reception controller.
        """

        visitor_id = str(
            self.primary_visitor_id
            or self.LOGICAL_VISITOR_ID
        )

        VisionEventBridge.publish(
            event_type=event_type,
            visitor_id=visitor_id,
            data={
                "state": self.state.value,
                "last_event": self.last_event,
                **(data or {}),
            },
        )

    # =========================================================
    # UPDATE PERSON PRESENCE
    # =========================================================

    def update_visitors(self, visitor_ids: List[int]) -> None:
        """
        Update physical visitor presence.

        visitor_ids comes from ByteTrack, but the actual numeric
        IDs are NOT used to determine visitor identity.

        Any non-empty list means:

            A person is present.

        Empty list means:

            No person detected in this frame.
        """

        now = time.time()

        # -----------------------------------------------------
        # PERSON PRESENT
        # -----------------------------------------------------

        if visitor_ids:

            # At least one person is visible.
            self._last_person_seen_at = now

            visitor = self.active_visitors.get(
                self.LOGICAL_VISITOR_ID,
            )

            self.active_visitors = {
                self.LOGICAL_VISITOR_ID: {
                    "first_seen": (
                        visitor["first_seen"]
                        if visitor is not None
                        else now
                    ),
                    "last_seen": now,
                }
            }

            # -------------------------------------------------
            # NEW PHYSICAL VISITOR
            # -------------------------------------------------

            if not self._person_was_present:

                self.primary_visitor_id = self.LOGICAL_VISITOR_ID

                self.state = ReceptionState.VISITOR_DETECTED

                self._greeting_started_at = now

                self.last_event = "visitor_detected"

                print(
                    "[RECEPTION] Visitor presence detected."
                )

                print(
                    "[RECEPTION] Logical visitor ID: #1"
                )

                # Notify shared backend.
                self._publish_event(
                    "visitor_detected",
                    {
                        "detected_tracker_ids": list(
                            visitor_ids
                        ),
                        "visitor_count": len(
                            visitor_ids
                        ),
                    },
                )

                # A physical visitor has actually arrived.
                self._publish_event(
                    "visitor_arrived",
                    {
                        "detected_tracker_ids": list(
                            visitor_ids
                        ),
                        "visitor_count": len(
                            visitor_ids
                        ),
                    },
                )

            # -------------------------------------------------
            # EXISTING PHYSICAL VISITOR
            # -------------------------------------------------

            else:

                # Keep the logical visitor alive.
                if self.primary_visitor_id is None:

                    self.primary_visitor_id = (
                        self.LOGICAL_VISITOR_ID
                    )

                # If state was VISITOR_LEFT, a person has
                # returned and should start a new greeting.
                if self.state == ReceptionState.VISITOR_LEFT:

                    self.state = ReceptionState.VISITOR_DETECTED

                    self._greeting_started_at = now

                    self.last_event = "visitor_detected"

                    print(
                        "[RECEPTION] Visitor returned."
                    )

                    self._publish_event(
                        "visitor_detected",
                        {
                            "detected_tracker_ids": list(
                                visitor_ids
                            ),
                            "visitor_count": len(
                                visitor_ids
                            ),
                            "returned": True,
                        },
                    )

                    self._publish_event(
                        "visitor_arrived",
                        {
                            "detected_tracker_ids": list(
                                visitor_ids
                            ),
                            "visitor_count": len(
                                visitor_ids
                            ),
                            "returned": True,
                        },
                    )

            # -------------------------------------------------
            # START GREETING
            # -------------------------------------------------

            if self.should_greet():

                self.state = ReceptionState.GREETING

                self.last_event = "greeting"

                self._publish_event(
                    "reception_started",
                    {
                        "reason": "visitor_present",
                    },
                )

            self._person_was_present = True

            return

        # -----------------------------------------------------
        # NO PERSON IN CURRENT FRAME
        # -----------------------------------------------------

        if self._last_person_seen_at is None:

            self._person_was_present = False

            return

        time_since_seen = (
            now - self._last_person_seen_at
        )

        # -----------------------------------------------------
        # TEMPORARY DETECTION LOSS
        # -----------------------------------------------------

        if time_since_seen < self.visitor_timeout:

            # Do NOTHING.

            # YOLO/ByteTrack can temporarily lose a person.
            # We do not end the interaction immediately.

            return

        # -----------------------------------------------------
        # REAL VISITOR LEFT
        # -----------------------------------------------------

        visitor_was_present = self._person_was_present

        if visitor_was_present:

            print(
                "[RECEPTION] No person detected for "
                f"{self.visitor_timeout:.1f}s."
            )

            print(
                "[RECEPTION] Visitor actually left."
            )

        # Keep the visitor ID available while publishing the
        # visitor_left event.
        visitor_id = (
            self.primary_visitor_id
            or self.LOGICAL_VISITOR_ID
        )

        self.active_visitors.clear()

        self.primary_visitor_id = None

        self._greeting_started_at = None

        self._last_person_seen_at = None

        self._person_was_present = False

        self.state = ReceptionState.VISITOR_LEFT

        self.last_event = "visitor_left"

        if visitor_was_present:

            VisionEventBridge.publish(
                event_type="visitor_left",
                visitor_id=str(visitor_id),
                data={
                    "reason": "visitor_timeout",
                    "timeout_seconds": (
                        self.visitor_timeout
                    ),
                },
            )

    # =========================================================
    # GREETING
    # =========================================================

    def should_greet(self) -> bool:

        if self.primary_visitor_id is None:
            return False

        if self.state != ReceptionState.VISITOR_DETECTED:
            return False

        if self._greeting_started_at is None:
            return False

        elapsed = (
            time.time()
            - self._greeting_started_at
        )

        return elapsed >= self.greeting_delay

    # =========================================================
    # RECEPTION STATES
    # =========================================================

    def start_listening(self) -> None:

        if self.primary_visitor_id is None:
            return

        self.state = ReceptionState.LISTENING

        self.last_event = "listening"

    def start_thinking(self) -> None:

        if self.primary_visitor_id is None:
            return

        self.state = ReceptionState.THINKING

        self.last_event = "thinking"

    def start_speaking(self) -> None:

        if self.primary_visitor_id is None:
            return

        self.state = ReceptionState.SPEAKING

        self.last_event = "speaking"

    def return_to_listening(self) -> None:

        if self.primary_visitor_id is not None:

            self.state = ReceptionState.LISTENING

            self.last_event = "listening"

        else:

            self.state = ReceptionState.IDLE

    # =========================================================
    # FINISH INTERACTION
    # =========================================================

    def finish_interaction(self) -> None:

        visitor_id = (
            self.primary_visitor_id
            or self.LOGICAL_VISITOR_ID
        )

        previous_state = self.state.value

        self.state = ReceptionState.IDLE

        self.primary_visitor_id = None

        self.active_visitors.clear()

        self._greeting_started_at = None

        self._last_person_seen_at = None

        self._person_was_present = False

        self.last_event = "interaction_finished"

        VisionEventBridge.publish(
            event_type="reception_ended",
            visitor_id=str(visitor_id),
            data={
                "reason": "interaction_finished",
                "previous_state": previous_state,
            },
        )

    # =========================================================
    # INFORMATION
    # =========================================================

    def get_active_visitors(self) -> List[int]:

        if self.primary_visitor_id is None:
            return []

        return [self.primary_visitor_id]

    def get_active_visitor_count(self) -> int:

        if self.primary_visitor_id is None:
            return 0

        return 1

    def get_primary_visitor(self) -> Optional[int]:

        return self.primary_visitor_id

    def get_last_event(self) -> Optional[str]:

        return self.last_event

    def get_status(self) -> dict:

        return {
            "state": self.state.value,
            "active_visitors": self.get_active_visitors(),
            "active_visitor_count": self.get_active_visitor_count(),
            "primary_visitor": self.primary_visitor_id,
            "last_event": self.last_event,
        }