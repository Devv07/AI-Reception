import sys
import time
import threading
from pathlib import Path
from typing import Optional

import cv2

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# EXISTING PROJECT MODULES
# ============================================================

from vision.camera.camera import Camera
from vision.tracking.visitor_tracker import VisitorTracker
from vision.reception.reception_controller import (
    ReceptionController,
    ReceptionState,
)

from voice.microphone.microphone import Microphone
from voice.stt.whisper_stt import WhisperSTT
from voice.tts.speaker import Speaker

from avatar.controller.avatar_controller import (
    AvatarController,
    AvatarState,
)


# ============================================================
# AI BRAIN ADAPTER
# ============================================================

class AIBrainAdapter:
    """
    Adapter for the shared AI Brain.

    The exact implementation of app/ai/brain.py may evolve
    as Member 1 develops the shared AI system.

    This adapter keeps Phase 9 independent from the internal
    implementation of the AI Brain.

    Supported methods:
        process()
        respond()
        generate_response()
        chat()

    The first available method is used.
    """

    def __init__(self):
        try:
            from app.ai.brain import AIBrain

            self.brain = AIBrain()

        except ImportError:

            try:
                from app.ai.brain import AIBrainService

                self.brain = AIBrainService()

            except ImportError as error:

                raise RuntimeError(
                    "Unable to import the shared AI Brain.\n"
                    "Expected AIBrain or AIBrainService in:\n"
                    "app/ai/brain.py"
                ) from error

        print("AI Brain initialized.")

    def process(self, user_text: str) -> str:

        if not user_text.strip():
            return (
                "I am sorry, I did not hear your request."
            )

        methods = [
            "process",
            "respond",
            "generate_response",
            "chat",
        ]

        for method_name in methods:

            method = getattr(
                self.brain,
                method_name,
                None,
            )

            if not callable(method):
                continue

            try:

                result = method(user_text)

                if result is None:
                    continue

                if isinstance(result, str):
                    return result.strip()

                if isinstance(result, dict):

                    for key in [
                        "response",
                        "answer",
                        "message",
                        "text",
                    ]:

                        value = result.get(key)

                        if value:
                            return str(value).strip()

                return str(result).strip()

            except TypeError:
                continue

        raise RuntimeError(
            "The shared AI Brain does not expose a supported "
            "text-processing method.\n"
            "Expected one of:\n"
            "process()\n"
            "respond()\n"
            "generate_response()\n"
            "chat()"
        )


# ============================================================
# PHYSICAL RECEPTIONIST
# ============================================================

class PhysicalReceptionist:

    """
    Complete Phase 9 physical receptionist.

    Pipeline:

        Camera
            ↓
        YOLO + ByteTrack
            ↓
        ReceptionController
            ↓
        Microphone
            ↓
        Whisper STT
            ↓
        Shared AI Brain
            ↓
        TTS Speaker

    Avatar state is synchronized with the same reception state.
    """

    GREETING_TEXT = (
        "Namaste. Welcome to our reception. "
        "How can I help you today?"
    )

    NO_INPUT_TEXT = (
        "I am sorry, I could not hear you clearly. "
        "Could you please repeat that?"
    )

    GOODBYE_TEXT = (
        "Thank you. Have a wonderful day."
    )

    def __init__(
        self,
        camera_index: int = 0,
        microphone_duration: float = 5.0,
    ):

        self.camera_index = camera_index

        self.microphone_duration = (
            microphone_duration
        )

        self.running = False

        self.interaction_active = False

        self.last_visitor_ids = set()

        # ----------------------------------------------------
        # CORE COMPONENTS
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("INITIALIZING AI RECEPTIONIST")
        print("=" * 70)

        print("\n[1/7] Initializing camera...")

        self.camera = Camera(
            camera_index=camera_index
        )

        print("Camera initialized.")

        print("\n[2/7] Initializing visitor tracker...")

        self.tracker = VisitorTracker()

        print("Visitor tracker initialized.")

        print("\n[3/7] Initializing reception controller...")

        self.reception = ReceptionController()

        print("Reception controller initialized.")

        print("\n[4/7] Initializing microphone...")

        self.microphone = Microphone(
            sample_rate=16000,
            channels=1,
            dtype="int16",
        )

        print("Microphone initialized.")

        print("\n[5/7] Initializing Whisper STT...")

        self.stt = WhisperSTT()

        print("Whisper STT initialized.")

        print("\n[6/7] Initializing speaker...")

        self.speaker = Speaker(
            rate=165,
            volume=1.0,
        )

        print("Speaker initialized.")

        print("\n[7/7] Initializing avatar controller...")

        self.avatar = AvatarController()

        print("Avatar controller initialized.")

        # ----------------------------------------------------
        # AI BRAIN
        # ----------------------------------------------------

        print("\nInitializing shared AI Brain...")

        self.ai_brain = AIBrainAdapter()

        print("Shared AI Brain ready.")

        print()
        print("=" * 70)
        print("AI RECEPTIONIST INITIALIZATION COMPLETE")
        print("=" * 70)
        print()


    # ========================================================
    # AVATAR STATE
    # ========================================================

    def set_state(self, state: ReceptionState):

        """
        Synchronize ReceptionController state with AvatarController.
        """

        mapping = {

            ReceptionState.IDLE:
                AvatarState.IDLE,

            ReceptionState.VISITOR_DETECTED:
                AvatarState.VISITOR_DETECTED,

            ReceptionState.GREETING:
                AvatarState.GREETING,

            ReceptionState.LISTENING:
                AvatarState.LISTENING,

            ReceptionState.THINKING:
                AvatarState.THINKING,

            ReceptionState.SPEAKING:
                AvatarState.SPEAKING,

            ReceptionState.VISITOR_LEFT:
                AvatarState.VISITOR_LEFT,
        }

        avatar_state = mapping.get(state)

        if avatar_state is not None:

            self.avatar.set_state(
                avatar_state
            )

            print(
                f"[AVATAR] {avatar_state.value}"
            )


    # ========================================================
    # SPEAK
    # ========================================================

    def speak(self, text: str):

        if not text:
            return

        self.set_state(
            ReceptionState.SPEAKING
        )

        self.speaker.speak(text)


    # ========================================================
    # GREETING
    # ========================================================

    def greet_visitor(self):

        print()
        print("=" * 70)
        print("GREETING VISITOR")
        print("=" * 70)

        self.set_state(
            ReceptionState.GREETING
        )

        self.speak(
            self.GREETING_TEXT
        )

        self.set_state(
            ReceptionState.LISTENING
        )


    # ========================================================
    # RECORD VISITOR
    # ========================================================

    def record_visitor(self) -> Optional[Path]:

        recordings_dir = (
            PROJECT_ROOT
            / "voice"
            / "recordings"
        )

        recordings_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        audio_path = (
            recordings_dir
            / f"phase9_{timestamp}.wav"
        )

        self.set_state(
            ReceptionState.LISTENING
        )

        try:

            audio = self.microphone.record(
                duration=self.microphone_duration
            )

            level = (
                self.microphone
                .get_audio_level(audio)
            )

            print(
                f"Microphone RMS level: {level:.6f}"
            )

            if level <= 0.0001:

                print(
                    "No useful microphone audio detected."
                )

                return None

            self.microphone.save_wav(
                audio,
                str(audio_path),
            )

            return audio_path

        except Exception as error:

            print(
                f"Microphone error: {error}"
            )

            return None


    # ========================================================
    # TRANSCRIBE
    # ========================================================

    def transcribe(
        self,
        audio_path: Path,
    ) -> str:

        self.set_state(
            ReceptionState.THINKING
        )

        print()
        print("Transcribing visitor speech...")

        try:

            text = self.stt.transcribe_wav(
                str(audio_path)
            )

            text = text.strip()

            print(
                f"Visitor: {text}"
            )

            return text

        except Exception as error:

            print(
                f"STT error: {error}"
            )

            return ""


    # ========================================================
    # AI RESPONSE
    # ========================================================

    def generate_response(
        self,
        visitor_text: str,
    ) -> str:

        self.set_state(
            ReceptionState.THINKING
        )

        print()
        print("AI Brain processing...")

        try:

            response = (
                self.ai_brain.process(
                    visitor_text
                )
            )

            response = response.strip()

            if not response:

                return (
                    "I am sorry, I do not have "
                    "a response for that yet."
                )

            print(
                f"AI: {response}"
            )

            return response

        except Exception as error:

            print(
                f"AI Brain error: {error}"
            )

            return (
                "I am sorry, I am having "
                "trouble processing your request."
            )


    # ========================================================
    # COMPLETE CONVERSATION TURN
    # ========================================================

    def handle_conversation_turn(self):

        print()
        print("-" * 70)
        print("LISTENING TO VISITOR")
        print("-" * 70)

        audio_path = (
            self.record_visitor()
        )

        if audio_path is None:

            self.speak(
                self.NO_INPUT_TEXT
            )

            self.set_state(
                ReceptionState.LISTENING
            )

            return


        visitor_text = (
            self.transcribe(
                audio_path
            )
        )


        if not visitor_text:

            self.speak(
                self.NO_INPUT_TEXT
            )

            self.set_state(
                ReceptionState.LISTENING
            )

            return


        response = (
            self.generate_response(
                visitor_text
            )
        )


        self.speak(
            response
        )


        self.set_state(
            ReceptionState.LISTENING
        )


    # ========================================================
    # VISITOR ENTERED
    # ========================================================

    def visitor_entered(
        self,
        visitor_ids,
    ):

        print()
        print("=" * 70)
        print(
            "VISITOR DETECTED:",
            visitor_ids,
        )
        print("=" * 70)

        self.set_state(
            ReceptionState.VISITOR_DETECTED
        )

        self.interaction_active = True

        self.greet_visitor()


    # ========================================================
    # VISITOR LEFT
    # ========================================================

    def visitor_left(self):

        print()
        print("=" * 70)
        print("VISITOR LEFT")
        print("=" * 70)

        self.interaction_active = False

        self.set_state(
            ReceptionState.VISITOR_LEFT
        )

        self.speak(
            self.GOODBYE_TEXT
        )

        self.set_state(
            ReceptionState.IDLE
        )


    # ========================================================
    # CAMERA DISPLAY
    # ========================================================

    def draw_overlay(
        self,
        frame,
        visitors,
    ):

        state = self.reception.get_status()

        current_state = (
            state.get("state", "idle")
        )

        visitor_count = len(
            visitors
        )

        cv2.rectangle(
            frame,
            (10, 10),
            (390, 125),
            (15, 20, 35),
            -1,
        )

        cv2.putText(
            frame,
            "AI RECEPTION",
            (25, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"State: {current_state}",
            (25, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"Visitors: {visitor_count}",
            (25, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            "Q = quit",
            (25, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )

        return frame


    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):

        print()
        print("=" * 70)
        print("PHASE 9 - COMPLETE PHYSICAL RECEPTIONIST")
        print("=" * 70)
        print()
        print("Starting camera...")
        print("Press Q to quit.")
        print()

        self.running = True

        try:

            while self.running:

                frame = (
                    self.camera.read()
                )

                if frame is None:

                    print(
                        "Camera frame unavailable."
                    )

                    break


                # ------------------------------------------------
                # VISION
                # ------------------------------------------------

                visitors = (
                    self.tracker.track(
                        frame
                    )
                )


                visitor_ids = {
                    visitor["visitor_id"]
                    for visitor in visitors
                }


                # ------------------------------------------------
                # UPDATE RECEPTION CONTROLLER
                # ------------------------------------------------

                self.reception.update_visitors(
                    list(visitor_ids)
                )


                # ------------------------------------------------
                # DRAW TRACKING
                # ------------------------------------------------

                frame = (
                    self.tracker.draw_tracks(
                        frame,
                        visitors
                    )
                )


                # ------------------------------------------------
                # VISITOR ARRIVAL
                # ------------------------------------------------

                new_visitors = (
                    visitor_ids
                    - self.last_visitor_ids
                )


                if (
                    new_visitors
                    and not self.interaction_active
                ):

                    self.visitor_entered(
                        new_visitors
                    )


                # ------------------------------------------------
                # CONVERSATION
                # ------------------------------------------------

                if (
                    self.interaction_active
                    and visitor_ids
                ):

                    self.handle_conversation_turn()


                # ------------------------------------------------
                # VISITOR LEFT
                # ------------------------------------------------

                if (
                    self.interaction_active
                    and not visitor_ids
                ):

                    self.visitor_left()


                self.last_visitor_ids = (
                    visitor_ids
                )


                # ------------------------------------------------
                # OVERLAY
                # ------------------------------------------------

                frame = (
                    self.draw_overlay(
                        frame,
                        visitors,
                    )
                )


                cv2.imshow(
                    "AI Reception - Phase 9",
                    frame,
                )


                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )


                if key == ord("q"):

                    self.running = False


        except KeyboardInterrupt:

            print(
                "\nReception stopped by user."
            )

        finally:

            self.shutdown()


    # ========================================================
    # SHUTDOWN
    # ========================================================

    def shutdown(self):

        print()
        print("=" * 70)
        print("SHUTTING DOWN AI RECEPTION")
        print("=" * 70)

        self.running = False

        try:
            self.speaker.stop()
        except Exception:
            pass

        try:
            self.camera.release()
        except Exception:
            pass

        cv2.destroyAllWindows()

        print("Camera released.")
        print("Speaker stopped.")
        print("Reception system stopped.")
        print()


# ============================================================
# MAIN
# ============================================================

def main():

    receptionist = PhysicalReceptionist(
        camera_index=0,
        microphone_duration=5.0,
    )

    receptionist.run()


if __name__ == "__main__":
    main()