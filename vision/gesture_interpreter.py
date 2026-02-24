import math
from typing import List, Dict, Any, Optional

class GestureInterpreter:
    """Interprets hand landmarks into game-specific commands."""
    
    def __init__(self, pinch_threshold: float = 0.05):
        self.pinch_threshold = pinch_threshold
        
    def get_command(self, landmarks: List[tuple]) -> Dict[str, Any]:
        """
        Analyzes landmarks and returns a command dictionary.
        Landmark indices:
        0: Wrist
        4: Thumb Tip
        8: Index Tip
        12: Middle Tip
        16: Ring Tip
        20: Pinky Tip
        """
        command = {
            "direction": None,
            "phase": False,
            "boost": False
        }
        
        if not landmarks:
            return command
            
        wrist = landmarks[0]
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]
        
        # 1. Direction Detection (Relative to wrist)
        dx = index_tip[0] - wrist[0]
        dy = index_tip[1] - wrist[1]
        
        # We look for the dominant axis
        if abs(dx) > abs(dy):
            if abs(dx) > 0.1: # Deadzone
                command["direction"] = "LEFT" if dx < 0 else "RIGHT"
        else:
            if abs(dy) > 0.1: # Deadzone
                command["direction"] = "UP" if dy < 0 else "DOWN"
                
        # 2. Pinch Detection (Thumb Tip to Index Tip)
        dist = math.sqrt(
            (thumb_tip[0] - index_tip[0])**2 + 
            (thumb_tip[1] - index_tip[1])**2
        )
        if dist < self.pinch_threshold:
            command["phase"] = True
            
        # 3. Fist Detection (Speed Boost)
        # Check if index, middle, ring, and pinky tips are all below their PIP joints
        # MediaPipe landmark indices for joints:
        # index: 6 (PIP), 8 (TIP)
        # middle: 10 (PIP), 12 (TIP)
        # ring: 14 (PIP), 16 (TIP)
        # pinky: 18 (PIP), 20 (TIP)
        
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        fingers_folded = True
        for tip_idx, pip_idx in zip(tips, pips):
            # In MediaPipe, y decreases as you go UP. 
            # So if tip.y > pip.y, the finger is folded (tip is below joint)
            if landmarks[tip_idx][1] < landmarks[pip_idx][1]:
                fingers_folded = False
                break
                
        command["boost"] = fingers_folded
        
        return command
