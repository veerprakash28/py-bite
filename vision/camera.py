import cv2
import threading
import time

class Camera:
    """Threaded camera capture to prevent blocking the game loop."""
    
    def __init__(self, camera_index: int = 0):
        self.cap = cv2.VideoCapture(camera_index)
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            
    def start(self):
        """Starts the background thread for frame capture."""
        thread = threading.Thread(target=self._update, args=(), daemon=True)
        thread.start()
        return self
        
    def _update(self):
        """Internal loop to keep reading frames."""
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
                
            with self.lock:
                # Flip frame horizontally for natural 'mirror' interaction
                self.frame = cv2.flip(frame, 1)
                
    def read(self):
        """Returns the latest captured frame."""
        with self.lock:
            return self.frame
            
    def stop(self):
        """Stops the capture thread and releases the camera."""
        self.stopped = True
        self.cap.release()
