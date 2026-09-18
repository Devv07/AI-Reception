import sys
import time
from pathlib import Path

import cv2


# Add project root to Python path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from vision.camera.camera import Camera
from vision.detection.person_detector import PersonDetector


WINDOW_NAME = "AI Reception - Vision MVP"


def main():
    print("=" * 60)
    print("AI RECEPTION - PHASE 1")
    print("Camera + YOLO11n Person Detection")
    print("=" * 60)

    camera = Camera(
        camera_index=0,
        width=1280,
        height=720,
    )

    detector = PersonDetector(
        model_path="yolo11n.pt",
        confidence=0.50,
    )

    try:
        camera.start()

        print("Camera started successfully.")
        print("Person detection is running.")
        print("Press Q to quit.")
        print("-" * 60)

        previous_time = time.time()

        while True:
            frame = camera.read()

            if frame is None:
                print("Failed to read frame from camera.")
                break

            detections = detector.detect(frame)

            frame = detector.draw_detections(
                frame,
                detections,
            )

            current_time = time.time()
            elapsed = current_time - previous_time

            fps = 1 / elapsed if elapsed > 0 else 0

            previous_time = current_time

            person_count = len(detections)

            cv2.putText(
                frame,
                f"Persons: {person_count}",
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
                "Press Q to quit",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")

    except Exception as error:
        print("\nERROR:")
        print(error)

    finally:
        camera.release()
        cv2.destroyAllWindows()

        print("Camera released.")
        print("Vision system stopped.")


if __name__ == "__main__":
    main()