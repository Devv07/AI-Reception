import asyncio
import json
import sys
import time
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional

import websockets


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
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

from services.ai.pipeline import chat


# ============================================================
# CONFIGURATION
# ============================================================

ORG_ID = "texas-college"
ORG_NAME = "Texas College of Management and IT"
CHANNEL = "physical"

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

RECORDING_SECONDS = 8

RECORDINGS_DIR = PROJECT_ROOT / "voice" / "recordings"

GREETING_TEXT = (
    "Namaste. Welcome to our reception. "
    "How can I help you today?"
)

GOODBYE_TEXT = (
    "Thank you for visiting. "
    "Have a wonderful day."
)

WEBSOCKET_HOST = "127.0.0.1"
WEBSOCKET_PORT = 8765

MINIMUM_TRANSCRIPT_LENGTH = 2

VISITOR_LEFT_GOODBYE_DELAY = 0.5


# ============================================================
# PHYSICAL RECEPTIONIST
# ============================================================

class PhysicalReceptionist:

    def __init__(self):

        print()
        print("=" * 60)
        print("INITIALIZING AI RECEPTIONIST")
        print("=" * 60)

        # ----------------------------------------------------
        # Camera
        # ----------------------------------------------------

        self.camera = Camera(
            camera_index=CAMERA_INDEX,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
        )

        # ----------------------------------------------------
        # Vision
        # ----------------------------------------------------

        self.tracker = VisitorTracker(
            model_path="yolo11n.pt",
            confidence=0.50,
            tracker="bytetrack.yaml",
        )

        # ----------------------------------------------------
        # Reception controller
        # ----------------------------------------------------

        self.reception = ReceptionController()

        # ----------------------------------------------------
        # Voice
        # ----------------------------------------------------

        self.microphone = Microphone(
            sample_rate=16000,
            channels=1,
        )

        self.stt = WhisperSTT()

        # Speaker uses Microsoft Zira by default.
        self.speaker = Speaker(
            rate=165,
            volume=1.0,
            preferred_voice="zira",
        )

        # ----------------------------------------------------
        # Avatar
        # ----------------------------------------------------

        self.avatar = AvatarController()

        # ----------------------------------------------------
        # WebSocket
        # ----------------------------------------------------

        self.avatar_clients = set()
        self.websocket_server = None

        # ----------------------------------------------------
        # Conversation
        # ----------------------------------------------------

        self.conversation_id: Optional[str] = None
        self.current_visitor_id: Optional[int] = None

        self.visitor_session_active = False

        # Prevent processing multiple conversation turns
        # simultaneously.
        self.processing_turn = False

        # ----------------------------------------------------
        # Runtime
        # ----------------------------------------------------

        self.running = True

        # ----------------------------------------------------
        # Recordings
        # ----------------------------------------------------

        RECORDINGS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        print("AI Reception components initialized.")
        print()


    # ========================================================
    # WEBSOCKET SERVER
    # ========================================================

    async def start_websocket_server(self):

        self.websocket_server = await websockets.serve(
            self.avatar_websocket_handler,
            WEBSOCKET_HOST,
            WEBSOCKET_PORT,
        )

        print(
            f"Avatar WebSocket server started: "
            f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"
        )


    async def avatar_websocket_handler(self, websocket):

        self.avatar_clients.add(websocket)

        print(
            f"[WEBSOCKET] Avatar connected "
            f"({len(self.avatar_clients)} client(s))"
        )

        try:

            await websocket.send(
                json.dumps(
                    {
                        "type": "avatar_state",
                        **self.avatar.get_status(),
                    }
                )
            )

            await websocket.wait_closed()

        except websockets.exceptions.ConnectionClosed:
            pass

        except Exception as error:

            print(
                f"[WEBSOCKET] Client error: {error}"
            )

        finally:

            self.avatar_clients.discard(websocket)

            print(
                f"[WEBSOCKET] Avatar disconnected "
                f"({len(self.avatar_clients)} client(s))"
            )


    async def broadcast_avatar_state(self):

        if not self.avatar_clients:
            return

        message = json.dumps(
            {
                "type": "avatar_state",
                **self.avatar.get_status(),
            }
        )

        disconnected = set()

        for websocket in list(self.avatar_clients):

            try:

                await websocket.send(message)

            except Exception:

                disconnected.add(websocket)

        for websocket in disconnected:

            self.avatar_clients.discard(websocket)


    # ========================================================
    # AVATAR STATE
    # ========================================================

    def reception_to_avatar_state(
        self,
        reception_state: ReceptionState,
    ) -> AvatarState:

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

        return mapping.get(
            reception_state,
            AvatarState.IDLE,
        )


    async def sync_avatar_state(self):

        reception_state = self.reception.state

        avatar_state = self.reception_to_avatar_state(
            reception_state
        )

        self.avatar.set_state(
            avatar_state
        )

        print(
            f"[AVATAR] {avatar_state.value}"
        )

        await self.broadcast_avatar_state()


    async def sync_if_reception_changed(
        self,
        previous_state: ReceptionState,
    ):

        if self.reception.state != previous_state:

            # ReceptionController already prints the
            # state transition. Do NOT print it again here.
            await self.sync_avatar_state()


    # ========================================================
    # CONVERSATION ID
    # ========================================================

    def create_conversation_id(
        self,
        visitor_id: int,
    ) -> str:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        return (
            f"physical-visitor-{visitor_id}-{timestamp}"
        )


    # ========================================================
    # TTS
    # ========================================================

    async def speak(
        self,
        text: str,
    ) -> None:
        """
        Speak receptionist response.

        pyttsx3 is intentionally called directly rather than
        through asyncio.to_thread() because the Windows TTS
        engine is COM-based.
        """

        if not text or not text.strip():
            return

        self.reception.start_speaking()

        await self.sync_avatar_state()

        print()
        print("AI RECEPTIONIST")
        print(text)
        print()

        try:

            self.speaker.speak(text)

        except Exception as error:

            print(
                f"[TTS ERROR] {error}"
            )

        finally:

            # Greeting and normal AI responses return to
            # listening when a visitor session is active.
            if self.visitor_session_active:

                self.reception.return_to_listening()

                await self.sync_avatar_state()

                print(
                    "[RECEPTION] Ready for visitor input."
                )


    # ========================================================
    # GREETING
    # ========================================================

    async def greet_visitor(
        self,
        visitor_id: int,
    ):

        self.current_visitor_id = visitor_id

        self.conversation_id = (
            self.create_conversation_id(
                visitor_id
            )
        )

        self.visitor_session_active = True

        print()
        print("=" * 60)
        print(
            f"NEW VISITOR DETECTED — Visitor #{visitor_id}"
        )
        print(
            f"Conversation ID: {self.conversation_id}"
        )
        print("=" * 60)

        await self.sync_avatar_state()

        await self.speak(
            GREETING_TEXT
        )


    # ========================================================
    # AUDIO RECORDING
    # ========================================================

    async def record_visitor_audio(self) -> Optional[Path]:

        if not self.visitor_session_active:
            return None

        print()
        print(
            f"[VOICE] Recording visitor audio "
            f"for {RECORDING_SECONDS} seconds..."
        )

        try:

            recording = await asyncio.to_thread(
                self.microphone.record,
                RECORDING_SECONDS,
            )

        except Exception as error:

            print(
                f"[MIC ERROR] {error}"
            )

            return None

        if recording is None:
            print("[MIC ERROR] No audio recorded.")
            return None

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        audio_file = (
            RECORDINGS_DIR
            / f"physical_{timestamp}.wav"
        )

        try:

            with wave.open(
                str(audio_file),
                "wb",
            ) as wav_file:

                wav_file.setnchannels(
                    self.microphone.channels
                )

                wav_file.setsampwidth(2)

                wav_file.setframerate(
                    self.microphone.sample_rate
                )

                wav_file.writeframes(
                    recording.tobytes()
                )

        except Exception as error:

            print(
                f"[AUDIO SAVE ERROR] {error}"
            )

            return None

        print(
            f"[VOICE] Audio saved: "
            f"{audio_file.name}"
        )

        return audio_file


    # ========================================================
    # SPEECH TO TEXT
    # ========================================================

    async def transcribe_audio(
        self,
        audio_file: Path,
    ) -> str:

        self.reception.start_thinking()

        await self.sync_avatar_state()

        print()
        print("[STT] Sending audio to Groq Whisper...")

        try:

            transcript = await asyncio.to_thread(
                self.stt.transcribe_wav,
                str(audio_file),
            )

        except Exception as error:

            print(
                f"[STT ERROR] {error}"
            )

            return ""

        transcript = (
            transcript or ""
        ).strip()

        print(
            f"[STT] Transcription: "
            f"{transcript or '[empty]'}"
        )

        return transcript


    # ========================================================
    # TRANSCRIPT VALIDATION
    # ========================================================

    def is_meaningful_transcript(
        self,
        transcript: str,
    ) -> bool:

        if not transcript:
            return False

        text = transcript.strip()

        if len(text) < MINIMUM_TRANSCRIPT_LENGTH:
            return False

        ignored = {
            ".",
            "..",
            "...",
            "。",
            "…",
        }

        if text in ignored:
            return False

        # Require at least one alphabetic character.
        if not any(
            character.isalpha()
            for character in text
        ):
            return False

        return True


    # ========================================================
    # AI BRAIN
    # ========================================================

    async def ask_ai_brain(
        self,
        transcript: str,
    ) -> Optional[str]:

        if not self.conversation_id:
            print(
                "[AI ERROR] Missing conversation ID."
            )
            return None

        print()
        print("[AI BRAIN] Processing visitor request...")
        print(
            f"[AI BRAIN] Query: {transcript}"
        )

        try:

            result = await chat(
                query=transcript,
                org_id=ORG_ID,
                conversation_id=self.conversation_id,
                channel=CHANNEL,
                org_name=ORG_NAME,
            )

        except Exception as error:

            print(
                f"[AI ERROR] {error}"
            )

            return None

        response = str(
            result.get(
                "response",
                "",
            )
        ).strip()

        intent = result.get(
            "intent",
            "unknown",
        )

        confidence = result.get(
            "confidence",
            0.0,
        )

        language = result.get(
            "language",
            "unknown",
        )

        handoff_required = result.get(
            "handoff_required",
            False,
        )

        handoff_department = result.get(
            "handoff_department",
            "",
        )

        sources = result.get(
            "sources",
            [],
        )

        print()
        print("[AI BRAIN RESULT]")
        print(
            f"Intent: {intent}"
        )
        print(
            f"Confidence: {confidence}"
        )
        print(
            f"Language: {language}"
        )
        print(
            f"Handoff required: "
            f"{handoff_required}"
        )

        if handoff_department:
            print(
                f"Handoff department: "
                f"{handoff_department}"
            )

        print(
            f"Response: {response}"
        )

        if not response:
            print(
                "[AI ERROR] AI returned empty response."
            )
            return None

        return response


    # ========================================================
    # ONE CONVERSATION TURN
    # ========================================================

    async def process_conversation_turn(self):

        if (
            not self.visitor_session_active
            or self.processing_turn
        ):
            return

        self.processing_turn = True

        try:

            # ------------------------------------------------
            # 1. Record
            # ------------------------------------------------

            audio_file = (
                await self.record_visitor_audio()
            )

            if audio_file is None:
                self.reception.return_to_listening()
                await self.sync_avatar_state()
                return

            # ------------------------------------------------
            # 2. Whisper
            # ------------------------------------------------

            transcript = await self.transcribe_audio(
                audio_file
            )

            if not self.is_meaningful_transcript(
                transcript
            ):

                print(
                    "[STT] No meaningful speech detected."
                )

                self.reception.return_to_listening()

                await self.sync_avatar_state()

                return

            # ------------------------------------------------
            # 3. AI Brain
            # ------------------------------------------------

            response = await self.ask_ai_brain(
                transcript
            )

            if not response:

                response = (
                    "I'm sorry, I couldn't process "
                    "that request. Please try again."
                )

            # ------------------------------------------------
            # 4. TTS
            # ------------------------------------------------

            await self.speak(
                response
            )

        except Exception as error:

            print()
            print(
                f"[CONVERSATION ERROR] {error}"
            )

            try:

                self.reception.return_to_listening()

                await self.sync_avatar_state()

            except Exception:
                pass

        finally:

            self.processing_turn = False


    # ========================================================
    # VISITOR LEFT
    # ========================================================

    async def visitor_left(self):

        if not self.current_visitor_id:
            return

        visitor_id = self.current_visitor_id

        print()
        print("=" * 60)
        print(
            f"VISITOR LEFT — Visitor #{visitor_id}"
        )
        print("=" * 60)

        # ----------------------------------------------------
        # End active session first.
        # ----------------------------------------------------

        self.visitor_session_active = False

        self.processing_turn = False

        # ----------------------------------------------------
        # Reception controller visitor-left state.
        # ----------------------------------------------------

        try:

            self.reception.finish_interaction()

        except Exception as error:

            print(
                f"[RECEPTION] Finish interaction: {error}"
            )

        await self.sync_avatar_state()

        # ----------------------------------------------------
        # Goodbye
        # ----------------------------------------------------

        await asyncio.sleep(
            VISITOR_LEFT_GOODBYE_DELAY
        )

        try:

            self.reception.start_speaking()

            await self.sync_avatar_state()

            print()
            print("AI RECEPTIONIST")
            print(GOODBYE_TEXT)
            print()

            self.speaker.speak(
                GOODBYE_TEXT
            )

        except Exception as error:

            print(
                f"[GOODBYE ERROR] {error}"
            )

        # ----------------------------------------------------
        # Return to idle.
        # ----------------------------------------------------

        try:

            self.reception.update_visitors([])

        except Exception:
            pass

        self.current_visitor_id = None
        self.conversation_id = None

        await asyncio.sleep(0.5)

        if self.reception.state != ReceptionState.IDLE:

            try:
                self.reception.finish_interaction()
            except Exception:
                pass

        await self.sync_avatar_state()

        print(
            "[RECEPTION] Ready for next visitor."
        )


    # ========================================================
    # MAIN LOOP
    # ========================================================

    async def run(self):

        await self.start_websocket_server()

        self.camera.start()

        self.avatar.set_state(
            AvatarState.IDLE
        )

        await self.broadcast_avatar_state()

        print()
        print("=" * 60)
        print("PHYSICAL RECEPTIONIST STARTED")
        print("=" * 60)
        print()
        print(
            "Camera is running internally."
        )
        print(
            "Camera view is hidden from the customer."
        )
        print()
        print(
            "Customer-facing interface:"
        )
        print(
            "Avatar only"
        )
        print()
        print(
            f"Avatar WebSocket: "
            f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"
        )
        print()
        print(
            "Press Ctrl+C in this terminal to stop."
        )
        print()

        previous_state = self.reception.state

        try:

            while self.running:

                # --------------------------------------------
                # Camera frame
                # --------------------------------------------

                frame = self.camera.read()

                if frame is None:

                    print(
                        "[CAMERA] Failed to read frame."
                    )

                    await asyncio.sleep(0.05)

                    continue

                # --------------------------------------------
                # Visitor tracking
                # --------------------------------------------

                visitors = self.tracker.track(
                    frame
                )

                visitor_ids = [
                    visitor["visitor_id"]
                    for visitor in visitors
                ]

                # --------------------------------------------
                # Update reception state
                # --------------------------------------------

                previous_state = (
                    self.reception.state
                )

                self.reception.update_visitors(
                    visitor_ids
                )

                await self.sync_if_reception_changed(
                    previous_state
                )

                current_state = (
                    self.reception.state
                )

                # --------------------------------------------
                # New visitor greeting
                # --------------------------------------------

                if (
                    current_state
                    == ReceptionState.GREETING
                    and not self.visitor_session_active
                ):

                    active_visitors = (
                        self.reception.get_active_visitors()
                    )

                    if active_visitors:

                        visitor_id = (
                            self.reception.primary_visitor_id
                        )

                        if visitor_id is None:

                            visitor_id = (
                                active_visitors[0]
                            )

                        await self.greet_visitor(
                            visitor_id
                        )

                # --------------------------------------------
                # Visitor conversation
                # --------------------------------------------

                elif (
                    current_state
                    == ReceptionState.LISTENING
                    and self.visitor_session_active
                    and not self.processing_turn
                ):

                    await self.process_conversation_turn()

                # --------------------------------------------
                # Visitor left
                # --------------------------------------------

                elif (
                    current_state
                    == ReceptionState.VISITOR_LEFT
                    and self.current_visitor_id is not None
                ):

                    await self.visitor_left()

                await asyncio.sleep(0.01)

        finally:

            await self.shutdown()


    # ========================================================
    # SHUTDOWN
    # ========================================================

    async def shutdown(self):

        if not self.running:
            return

        self.running = False

        print()
        print("=" * 60)
        print("SHUTTING DOWN AI RECEPTIONIST")
        print("=" * 60)

        # ----------------------------------------------------
        # Stop speaker
        # ----------------------------------------------------

        try:

            self.speaker.stop()

        except Exception:
            pass

        # ----------------------------------------------------
        # Camera
        # ----------------------------------------------------

        try:

            self.camera.release()

        except Exception as error:

            print(
                f"[SHUTDOWN] Camera error: {error}"
            )

        # ----------------------------------------------------
        # WebSocket
        # ----------------------------------------------------

        if self.websocket_server is not None:

            try:

                self.websocket_server.close()

                await self.websocket_server.wait_closed()

                print(
                    "[WEBSOCKET] Server closed."
                )

            except Exception as error:

                print(
                    f"[WEBSOCKET] Shutdown error: "
                    f"{error}"
                )

        # ----------------------------------------------------
        # Avatar clients
        # ----------------------------------------------------

        for websocket in list(
            self.avatar_clients
        ):

            try:

                await websocket.close()

            except Exception:
                pass

        self.avatar_clients.clear()

        print(
            "AI Receptionist stopped."
        )


# ============================================================
# ENTRY POINT
# ============================================================

async def main():

    receptionist = PhysicalReceptionist()

    await receptionist.run()


if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print()
        print(
            "Receptionist stopped by user."
        )