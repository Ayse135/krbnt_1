import cv2
import numpy as np
from PIL import Image
import os

class VisionUtils:
    """Utility class for computer vision tasks in banner generation."""
    
    # Standard Haar Cascade for Face Detection
    # On many systems, this is available via cv2.data.haarcascades
    _cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    _face_cascade = cv2.CascadeClassifier(_cascade_path)

    @classmethod
    def get_face_center(cls, pil_img):
        """
        Detects the face in a PIL image and returns the center coordinates.
        Returns: (center_x, center_y, face_width, face_height)
        If no face is detected, returns (image_center_x, image_height * 0.3) as fallback.
        """
        # Convert PIL to OpenCV (BGR)
        open_cv_image = np.array(pil_img.convert('RGB'))
        # RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect Faces
        faces = cls._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) > 0:
            # Take the largest face found (assuming it's the player)
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            (x, y, w, h) = faces[0]
            
            center_x = x + w // 2
            center_y = y + h // 2
            return (center_x, center_y, w, h)
        
        # Fallback: Assume head is in the upper middle
        w, h = pil_img.size
        return (w // 2, int(h * 0.3), int(w * 0.2), int(h * 0.2))

    @classmethod
    def align_player_to_anchor(cls, player_pil, anchor_pos, target_face_h=180):
        """
        Calculates the necessary transform to place the player's face on the anchor.
        anchor_pos: (target_x, target_y) on the canvas.
        Returns: (transformed_player_pil, paste_pos)
        """
        curr_x, curr_y, curr_w, curr_h = cls.get_face_center(player_pil)
        
        # 1. Scale based on target face height
        scale = target_face_h / curr_h
        new_size = (int(player_pil.width * scale), int(player_pil.height * scale))
        player_resized = player_pil.resize(new_size, Image.Resampling.LANCZOS)
        
        # 2. Re-calculate face center on the resized image
        scaled_x = int(curr_x * scale)
        scaled_y = int(curr_y * scale)
        
        # 3. Calculate paste position so scaled_face lands on anchor_pos
        paste_x = anchor_pos[0] - scaled_x
        paste_y = anchor_pos[1] - scaled_y
        
        return player_resized, (paste_x, paste_y)
