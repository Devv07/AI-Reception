from typing import Dict, List
from ultralytics import YOLO


class VisitorTracker:
    """
    Tracks people across video frames using YOLO11n + ByteTrack.

    Each detected person receives a stable tracking ID.
    """

    PERSON_CLASS_ID = 0

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        confidence: float = 0.50,
        tracker: str = "bytetrack.yaml",
    ):
        self.model_path = model_path
        self.confidence = confidence
        self.tracker = tracker

        print(f"Loading tracking model: {model_path}")

        self.model = YOLO(model_path)

        print("Tracking model loaded successfully.")

    def track(self, frame) -> List[Dict]:
        """
        Track people in a single frame.

        Returns:
            List of dictionaries:

            {
                "visitor_id": int,
                "class": "person",
                "confidence": float,
                "bbox": (x1, y1, x2, y2)
            }
        """

        results = self.model.track(
            source=frame,
            conf=self.confidence,
            classes=[self.PERSON_CLASS_ID],
            tracker=self.tracker,
            persist=True,
            verbose=False,
        )

        visitors = []

        for result in results:

            if result.boxes is None:
                continue

            boxes = result.boxes

            # Tracking IDs may not exist yet.
            if boxes.id is None:
                continue

            tracking_ids = boxes.id.int().cpu().tolist()
            coordinates = boxes.xyxy.cpu().tolist()
            confidences = boxes.conf.cpu().tolist()

            for visitor_id, bbox, confidence in zip(
                tracking_ids,
                coordinates,
                confidences,
            ):

                x1, y1, x2, y2 = map(
                    int,
                    bbox,
                )

                visitors.append(
                    {
                        "visitor_id": int(visitor_id),
                        "class": "person",
                        "confidence": float(confidence),
                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2,
                        ),
                    }
                )

        return visitors

    def draw_tracks(
        self,
        frame,
        visitors: List[Dict],
    ):
        """
        Draw tracked visitor boxes and IDs.
        """

        for visitor in visitors:

            x1, y1, x2, y2 = visitor["bbox"]

            visitor_id = visitor["visitor_id"]
            confidence = visitor["confidence"]

            # Bounding box
            cv2_rectangle_color = (
                0,
                255,
                0,
            )

            import cv2

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                cv2_rectangle_color,
                2,
            )

            # Visitor label
            label = (
                f"Visitor #{visitor_id} "
                f"{confidence:.2f}"
            )

            label_y = max(
                y1 - 10,
                25,
            )

            cv2.putText(
                frame,
                label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                cv2_rectangle_color,
                2,
                cv2.LINE_AA,
            )

        return frame