import mediapipe as mp
import cv2
import numpy as np
from typing import List, Optional, NamedTuple

class HandTracker:
    """Wraps MediaPipe Hands for landmark detection."""
    
    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        
    def find_hands(self, frame: np.ndarray) -> Optional[NamedTuple]:
        """Processes a frame and returns hand landmarks."""
        if frame is None:
            return None
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return self.results
        
    def draw_landmarks(self, frame: np.ndarray):
        """Draws detected hand landmarks on the frame (for debug)."""
        if self.results and self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return frame
        
    def get_landmarks(self, hand_index: int = 0) -> List[tuple]:
        """Extracts (x, y, z) list of landmarks for a specific hand."""
        landmarks = []
        if self.results and self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_index:
                hand = self.results.multi_hand_landmarks[hand_index]
                for lm in hand.landmark:
                    landmarks.append((lm.x, lm.y, lm.z))
        return landmarks
