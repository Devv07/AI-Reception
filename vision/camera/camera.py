import cv2


class Camera:
    """
    Handles webcam initialization, frame capture,
    and camera cleanup for the AI Reception system.
    """

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

    def start(self) -> None:
        """
        Open the webcam using Windows DirectShow first.
        Falls back to OpenCV's default backend if necessary.
        """

        print(
            f"Opening camera {self.camera_index} "
            f"at {self.width}x{self.height}..."
        )

        # ---------------------------------------------------------
        # Try Windows DirectShow first.
        # ---------------------------------------------------------
        self.cap = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_DSHOW,
        )

        if not self.cap.isOpened():
            print("DirectShow camera backend failed.")
            print("Trying default OpenCV camera backend...")

            if self.cap is not None:
                self.cap.release()

            self.cap = cv2.VideoCapture(
                self.camera_index
            )

        # ---------------------------------------------------------
        # Final camera check.
        # ---------------------------------------------------------
        if not self.cap.isOpened():
            self.cap = None

            raise RuntimeError(
                f"Unable to open camera with index "
                f"{self.camera_index}."
            )

        # ---------------------------------------------------------
        # Configure camera resolution.
        # ---------------------------------------------------------
        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width,
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height,
        )

        # ---------------------------------------------------------
        # Read actual camera properties.
        # ---------------------------------------------------------
        actual_width = int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        actual_height = int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        print(
            f"Camera opened successfully: "
            f"{actual_width}x{actual_height}"
        )

    def read(self):
        """
        Read one frame from the camera.

        Returns:
            OpenCV frame if successful.
            None if the frame could not be read.
        """

        if self.cap is None:
            raise RuntimeError(
                "Camera has not been started. "
                "Call start() first."
            )

        success, frame = self.cap.read()

        if not success:
            return None

        return frame

    def is_opened(self) -> bool:
        """
        Check whether the camera is currently open.
        """

        return (
            self.cap is not None
            and self.cap.isOpened()
        )

    def release(self) -> None:
        """
        Release the camera.
        """

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        print("Camera released.")