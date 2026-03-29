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
    def align_player_to_anchor(cls, player_pil, anchor_pos, canvas_h=628, target_face_h=190):
        """
        Calculates the necessary transform to place the player's face on the anchor.
        anchor_pos: (target_x, target_y) on the canvas.
        canvas_h: Total height of the target canvas (to ensure bottom contact).
        Returns: (transformed_player_pil, paste_pos)
        """
        curr_x, curr_y, curr_w, curr_h = cls.get_face_center(player_pil)
        
        # 1. Base Scale: Target face size
        scale_face = target_face_h / curr_h
        
        # 2. Safety Scale (v28): Ensure player torso reaches the bottom
        # Remaining height on canvas from anchor to bottom
        dist_to_bottom = canvas_h - anchor_pos[1]
        # Remaining height in photo from face center to bottom
        dist_in_img = player_pil.height - curr_y
        
        # If photo is short (portrait), we might need a larger scale 
        # to ensure the body doesn't float.
        scale_safety = dist_to_bottom / dist_in_img if dist_in_img > 0 else scale_face
        
        # Final Scale: Use the larger of the two
        final_scale = max(scale_face, scale_safety)
        
        new_size = (int(player_pil.width * final_scale), int(player_pil.height * final_scale))
        player_resized = player_pil.resize(new_size, Image.Resampling.LANCZOS)
        
        # 3. Calculate paste position so scaled_face lands on anchor_pos
        scaled_x = int(curr_x * final_scale)
        scaled_y = int(curr_y * final_scale)
        
        paste_x = anchor_pos[0] - scaled_x
        paste_y = anchor_pos[1] - scaled_y
        
        return player_resized, (paste_x, paste_y)
