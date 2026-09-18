import sys
import time
from pathlib import Path

import cv2


# Add project root to Python path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from vision.camera.camera import Camera
from vision.tracking.visitor_tracker import VisitorTracker


WINDOW_NAME = "AI Reception - Visitor Tracking"


def main():

    print("=" * 60)
    print("AI RECEPTION - PHASE 2")
    print("Visitor Tracking")
    print("=" * 60)

    camera = Camera(
        camera_index=0,
        width=1280,
        height=720,
    )

    tracker = VisitorTracker(
        model_path="yolo11n.pt",
        confidence=0.50,
        tracker="bytetrack.yaml",
    )

    try:

        camera.start()

        print("Camera started successfully.")
        print("ByteTrack visitor tracking is running.")
        print("Move around in front of the camera.")
        print("Press Q to quit.")
        print("-" * 60)

        previous_time = time.time()

        while True:

            frame = camera.read()

            if frame is None:

                print(
                    "Failed to read frame from camera."
                )

                break

            # -------------------------------------------------
            # Track visitors
            # -------------------------------------------------

            visitors = tracker.track(frame)

            # -------------------------------------------------
            # Draw tracking information
            # -------------------------------------------------

            frame = tracker.draw_tracks(
                frame,
                visitors,
            )

            # -------------------------------------------------
            # FPS
            # -------------------------------------------------

            current_time = time.time()

            elapsed = (
                current_time
                - previous_time
            )

            fps = (
                1 / elapsed
                if elapsed > 0
                else 0
            )

            previous_time = current_time

            # -------------------------------------------------
            # Visitor count
            # -------------------------------------------------

            visitor_count = len(visitors)

            # -------------------------------------------------
            # Display information
            # -------------------------------------------------

            cv2.putText(
                frame,
                f"Visitors: {visitor_count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                "ByteTrack",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # -------------------------------------------------
            # Show frame
            # -------------------------------------------------

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break

    except KeyboardInterrupt:

        print(
            "\nProgram interrupted by user."
        )

    except Exception as error:

        print("\nERROR:")
        print(error)

    finally:

        camera.release()

        cv2.destroyAllWindows()

        print("Vision tracking system stopped.")


if __name__ == "__main__":
    main()