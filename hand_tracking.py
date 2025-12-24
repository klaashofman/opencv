import cv2
import mediapipe as mp
import numpy as np
import math

class HandArmTracker:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        # Calculate angle using dot product
        dot_product = np.dot(vector1, vector2)
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        angle = math.acos(np.clip(dot_product / (magnitude1 * magnitude2), -1.0, 1.0))
        return math.degrees(angle)
    
    def calculate_rotation(self, wrist, middle_mcp, index_mcp):
        """Calculate hand rotation (yaw, pitch, roll estimation)"""
        # Calculate hand plane orientation
        dx = middle_mcp[0] - wrist[0]
        dy = middle_mcp[1] - wrist[1]
        
        # Rotation angle in 2D plane
        rotation_angle = math.degrees(math.atan2(dy, dx))
        
        return rotation_angle
    
    def is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id, finger_mcp_id):
        """Check if a finger is extended by comparing tip position with PIP joint"""
        tip = landmarks[finger_tip_id]
        pip = landmarks[finger_pip_id]
        mcp = landmarks[finger_mcp_id]
        
        # Finger is extended if tip is farther from wrist than PIP
        return tip.y < pip.y
    
    def is_thumb_extended(self, landmarks):
        """Special case for thumb extension detection"""
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Thumb is extended if tip is farther from palm center
        return thumb_tip.x < thumb_ip.x if thumb_tip.x < 0.5 else thumb_tip.x > thumb_ip.x
    
    def detect_finger_states(self, hand_landmarks):
        """Detect which fingers are extended/closed"""
        landmarks = hand_landmarks.landmark
        
        fingers = {
            'thumb': self.is_thumb_extended(landmarks),
            'index': self.is_finger_extended(landmarks, 8, 6, 5),
            'middle': self.is_finger_extended(landmarks, 12, 10, 9),
            'ring': self.is_finger_extended(landmarks, 16, 14, 13),
            'pinky': self.is_finger_extended(landmarks, 20, 18, 17)
        }
        
        extended_count = sum(fingers.values())
        
        return fingers, extended_count
    
    def get_hand_position(self, hand_landmarks, frame_shape):
        """Get hand center position"""
        h, w, _ = frame_shape
        wrist = hand_landmarks.landmark[0]
        middle_mcp = hand_landmarks.landmark[9]
        
        # Calculate center point
        center_x = int((wrist.x + middle_mcp.x) / 2 * w)
        center_y = int((wrist.y + middle_mcp.y) / 2 * h)
        
        return (center_x, center_y)
    
    def calculate_arm_angle(self, hand_landmarks, frame_shape):
        """Calculate arm angle based on wrist and middle finger base"""
        h, w, _ = frame_shape
        wrist = hand_landmarks.landmark[0]
        middle_mcp = hand_landmarks.landmark[9]
        
        wrist_pos = (int(wrist.x * w), int(wrist.y * h))
        mcp_pos = (int(middle_mcp.x * w), int(middle_mcp.y * h))
        
        # Calculate angle from vertical
        dx = mcp_pos[0] - wrist_pos[0]
        dy = mcp_pos[1] - wrist_pos[1]
        angle = math.degrees(math.atan2(dx, dy))
        
        return angle, wrist_pos, mcp_pos
    
    def draw_info(self, frame, hand_landmarks, handedness):
        """Draw tracking information on frame"""
        h, w, _ = frame.shape
        
        # Get hand position
        position = self.get_hand_position(hand_landmarks, frame.shape)
        
        # Get finger states
        fingers, extended_count = self.detect_finger_states(hand_landmarks)
        
        # Calculate arm angle and rotation
        arm_angle, wrist_pos, mcp_pos = self.calculate_arm_angle(hand_landmarks, frame.shape)
        
        # Calculate hand rotation
        landmarks = hand_landmarks.landmark
        wrist = (int(landmarks[0].x * w), int(landmarks[0].y * h))
        middle_mcp = (int(landmarks[9].x * w), int(landmarks[9].y * h))
        index_mcp = (int(landmarks[5].x * w), int(landmarks[5].y * h))
        hand_rotation = self.calculate_rotation(wrist, middle_mcp, index_mcp)
        
        # Draw hand landmarks
        self.mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style()
        )
        
        # Draw arm direction line
        cv2.line(frame, wrist_pos, mcp_pos, (0, 255, 0), 3)
        
        # Draw hand center
        cv2.circle(frame, position, 10, (255, 0, 0), -1)
        
        # Prepare info text
        hand_label = handedness.classification[0].label
        y_offset = 30
        
        info_texts = [
            f"{hand_label} Hand",
            f"Position: ({position[0]}, {position[1]})",
            f"Arm Angle: {arm_angle:.1f}°",
            f"Hand Rotation: {hand_rotation:.1f}°",
            f"Fingers Extended: {extended_count}",
            f"Thumb: {'Open' if fingers['thumb'] else 'Closed'}",
            f"Index: {'Open' if fingers['index'] else 'Closed'}",
            f"Middle: {'Open' if fingers['middle'] else 'Closed'}",
            f"Ring: {'Open' if fingers['ring'] else 'Closed'}",
            f"Pinky: {'Open' if fingers['pinky'] else 'Closed'}"
        ]
        
        # Draw background rectangle for text
        text_height = len(info_texts) * 25 + 20
        cv2.rectangle(frame, (10, 10), (350, text_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (350, text_height), (255, 255, 255), 2)
        
        # Draw info text
        for i, text in enumerate(info_texts):
            y_pos = y_offset + i * 25
            color = (0, 255, 255) if i == 0 else (255, 255, 255)
            cv2.putText(frame, text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Detect gestures
        gesture = self.detect_gesture(fingers, extended_count)
        if gesture:
            cv2.putText(frame, f"Gesture: {gesture}", (20, text_height + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    def detect_gesture(self, fingers, extended_count):
        """Detect common hand gestures"""
        if extended_count == 0:
            return "FIST"
        elif extended_count == 5:
            return "OPEN HAND"
        elif fingers['thumb'] and fingers['index'] and extended_count == 2:
            return "PEACE / VICTORY"
        elif fingers['index'] and extended_count == 1:
            return "POINTING"
        elif fingers['thumb'] and extended_count == 1:
            return "THUMBS UP"
        elif fingers['index'] and fingers['middle'] and extended_count == 2:
            return "PEACE SIGN"
        elif fingers['index'] and fingers['middle'] and fingers['ring'] and extended_count == 3:
            return "THREE FINGERS"
        return None
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks and info
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                self.draw_info(frame, hand_landmarks, handedness)
        
        return frame
    
    def run(self):
        """Run the hand tracking application"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Hand and Arm Tracking Started")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame
            frame = self.process_frame(frame)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (frame.shape[1] - 250, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Hand and Arm Tracking', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

def main():
    tracker = HandArmTracker()
    tracker.run()

if __name__ == "__main__":
    main()
