import cv2
import re
import numpy as np
import torch
from typing import Dict, Any, Optional, Tuple, List
from backend.config import OCR_CONFIDENCE_THRESHOLD

class OCREngine:
    """
    License Plate OCR Engine.
    Uses EasyOCR with preprocessing and license plate string normalization.
    """
    def __init__(self, conf_threshold: float = OCR_CONFIDENCE_THRESHOLD):
        self.conf_threshold = conf_threshold
        self.reader = None
        self._init_reader()

    def _init_reader(self):
        try:
            import easyocr
            use_gpu = torch.cuda.is_available()
            # Initialize EasyOCR reader for English alphanumeric characters
            self.reader = easyocr.Reader(['en'], gpu=use_gpu, verbose=False)
            print(f"[OCREngine] EasyOCR initialized successfully (GPU={use_gpu})")
        except Exception as e:
            print(f"[OCREngine] Warning: Failed to initialize EasyOCR: {e}")
            self.reader = None

    def preprocess_plate(self, plate_crop: np.ndarray) -> List[np.ndarray]:
        """
        Applies a series of image enhancements to maximize OCR readability:
        1. Resizing to standard height (approx 80-100px)
        2. Bilateral filtering to smooth noise while keeping crisp character edges
        3. Contrast stretching / CLAHE
        4. Adaptive thresholding & Otsu binary variations
        Returns a list of preprocessed image variants to try for OCR.
        """
        if plate_crop is None or plate_crop.size == 0:
            return []

        h, w = plate_crop.shape[:2]
        target_h = 90
        scale = target_h / max(h, 1)
        target_w = max(int(w * scale), 120)
        resized = cv2.resize(plate_crop, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Bilateral filter + CLAHE produces the sharpest OCR output
        bilateral = cv2.bilateralFilter(gray, 7, 50, 50)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6, 6))
        contrast_enhanced = clahe.apply(bilateral)

        return [contrast_enhanced]

    def read_plate(self, plate_crop: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Runs OCR on plate crop with preprocessed variations.
        Returns normalized plate text, confidence, and raw text if successful, or None.
        """
        if self.reader is None or plate_crop is None or plate_crop.size == 0:
            return None

        variants = self.preprocess_plate(plate_crop)
        best_result = None
        best_conf = 0.0

        for img in variants:
            try:
                results = self.reader.readtext(
                    img,
                    detail=1,
                    paragraph=False,
                    allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                )

                if not results:
                    continue

                # Combine all text detected inside the plate crop
                combined_text = ""
                total_conf = 0.0
                valid_boxes = 0

                for (_, text, conf) in results:
                    cleaned_seg = re.sub(r'[^A-Z0-9]', '', text.upper())
                    if cleaned_seg:
                        combined_text += cleaned_seg
                        total_conf += conf
                        valid_boxes += 1

                if valid_boxes > 0:
                    avg_conf = total_conf / valid_boxes
                    normalized = self.normalize_plate_text(combined_text)

                    if normalized and avg_conf > best_conf:
                        best_conf = avg_conf
                        best_result = {
                            "plate_number": normalized,
                            "ocr_confidence": round(float(avg_conf), 2),
                            "raw_text": combined_text
                        }

            except Exception as e:
                continue

        if best_result and best_result["ocr_confidence"] >= self.conf_threshold:
            return best_result
        elif best_result:
            best_result["uncertain"] = True
            return best_result

        return None

    @staticmethod
    def normalize_plate_text(raw_text: str) -> Optional[str]:
        """
        Cleans and normalizes license plate string.
        - Converts to uppercase
        - Strips spaces, punctuation, special symbols
        - Fixes common character-number confusions based on standard vehicle plate schemas
        """
        if not raw_text:
            return None

        text = re.sub(r'[^A-Z0-9]', '', raw_text.upper())
        if len(text) < 4 or len(text) > 13:
            return None

        # Check standard Indian License Plate pattern (e.g., MH12AB1234, DL01C1234, RJ14EF5678)
        # 2 letters (State) + 1-2 digits (RTO) + 0-3 letters (Series) + 4 digits (Unique Number)
        indian_pattern = re.compile(r'^([A-Z]{2})([0-9]{1,2})([A-Z]{1,3})([0-9]{4})$')
        m = indian_pattern.match(text)
        if m:
            state, rto, series, num = m.groups()
            return f"{state}{rto}{series}{num}"

        # If slightly off, try correcting first 2 chars to letters (e.g. '0' -> 'D', '1' -> 'I')
        chars = list(text)
        if len(chars) >= 6:
            # Common fix for state code in pos 0 and 1
            char_map_num_to_alpha = {'0': 'O', '1': 'I', '5': 'S', '8': 'B', '2': 'Z'}
            if chars[0].isdigit() and chars[0] in char_map_num_to_alpha:
                chars[0] = char_map_num_to_alpha[chars[0]]
            if chars[1].isdigit() and chars[1] in char_map_num_to_alpha:
                chars[1] = char_map_num_to_alpha[chars[1]]

            # Common fix for last 4 digits (alpha to digit)
            char_map_alpha_to_num = {'O': '0', 'I': '1', 'S': '5', 'B': '8', 'Z': '2', 'A': '4'}
            for idx in range(max(len(chars) - 4, 2), len(chars)):
                if chars[idx].isalpha() and chars[idx] in char_map_alpha_to_num:
                    chars[idx] = char_map_alpha_to_num[chars[idx]]

            corrected = "".join(chars)
            m2 = indian_pattern.match(corrected)
            if m2:
                state, rto, series, num = m2.groups()
                return f"{state}{rto}{series}{num}"

        return text
