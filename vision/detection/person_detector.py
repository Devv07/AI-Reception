import cv2
from ultralytics import YOLO


class PersonDetector:
    """
    Detects people using YOLO11n.
    """

    PERSON_CLASS_ID = 0

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        confidence: float = 0.50,
    ):
        self.model_path = model_path
        self.confidence = confidence

        print(f"Loading YOLO model: {model_path}")

        self.model = YOLO(model_path)

        print("YOLO model loaded successfully.")

    def detect(self, frame):
        """
        Detect people in a frame.

        Returns:
            List of dictionaries containing:
            - class
            - confidence
            - bbox
        """

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            classes=[self.PERSON_CLASS_ID],
            verbose=False,
        )

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                coordinates = box.xyxy[0].tolist()
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    coordinates,
                )

                detections.append(
                    {
                        "class": "person",
                        "confidence": confidence,
                        "bbox": (x1, y1, x2, y2),
                    }
                )

        return detections

    def draw_detections(
        self,
        frame,
        detections,
    ):
        """
        Draw detection boxes and labels on the frame.
        """

        for detection in detections:

            x1, y1, x2, y2 = detection["bbox"]
            confidence = detection["confidence"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            label = f"Person {confidence:.2f}"

            label_y = max(y1 - 10, 25)

            cv2.putText(
                frame,
                label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        return frame