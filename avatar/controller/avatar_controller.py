from enum import Enum
from typing import Optional


class AvatarState(str, Enum):
    """
    States supported by the AI Reception avatar.
    """

    IDLE = "idle"
    VISITOR_DETECTED = "visitor_detected"
    GREETING = "greeting"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    VISITOR_LEFT = "visitor_left"


class AvatarController:
    """
    Controls the visual state of the receptionist avatar.

    This class does not render the avatar.

    It only manages:
        - current state
        - state transitions
        - animation name
        - speaking/listening indicators

    A future VRM/Three.js renderer can consume this state.
    """

    STATE_ANIMATIONS = {
        AvatarState.IDLE: "idle",
        AvatarState.VISITOR_DETECTED: "attention",
        AvatarState.GREETING: "greeting",
        AvatarState.LISTENING: "listening",
        AvatarState.THINKING: "thinking",
        AvatarState.SPEAKING: "speaking",
        AvatarState.VISITOR_LEFT: "idle",
    }

    def __init__(self):
        self.state = AvatarState.IDLE
        self.previous_state: Optional[AvatarState] = None

    def set_state(self, state: AvatarState) -> None:
        """
        Change the avatar state.
        """

        if not isinstance(state, AvatarState):
            raise ValueError(
                f"Invalid avatar state: {state}"
            )

        if state == self.state:
            return

        self.previous_state = self.state
        self.state = state

    def get_state(self) -> str:
        """
        Return the current state as a string.
        """

        return self.state.value

    def get_animation(self) -> str:
        """
        Return the animation associated with the current state.
        """

        return self.STATE_ANIMATIONS[self.state]

    def is_listening(self) -> bool:
        return self.state == AvatarState.LISTENING

    def is_thinking(self) -> bool:
        return self.state == AvatarState.THINKING

    def is_speaking(self) -> bool:
        return self.state == AvatarState.SPEAKING

    def is_idle(self) -> bool:
        return self.state == AvatarState.IDLE

    def get_status(self) -> dict:
        """
        Return avatar information for a future
        WebSocket/VRM frontend.
        """

        return {
            "state": self.state.value,
            "animation": self.get_animation(),
            "previous_state": (
                self.previous_state.value
                if self.previous_state
                else None
            ),
            "is_listening": self.is_listening(),
            "is_thinking": self.is_thinking(),
            "is_speaking": self.is_speaking(),
        }