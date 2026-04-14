# =============================================================================
# AI-Based Autonomous Navigation System — Global Configuration
# =============================================================================
# This file centralizes ALL project settings across perception, navigation,
# simulation, and utility modules. Edit here to tune the entire system.

# ─────────────────────────────────────────────
# DISPLAY / SIMULATION WINDOW
# ─────────────────────────────────────────────
WIDTH  = 900          # Pygame window width  (pixels)
HEIGHT = 650          # Pygame window height (pixels)
FPS    = 60           # Target frames per second

WINDOW_TITLE = "AI Autonomous Navigation System — Simulation"

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
BLACK       = (15,  15,  20)     # Background / map fill
WHITE       = (255, 255, 255)    # Path waypoints
GRAY        = (60,  60,  70)     # Road surface
DARK_GRAY   = (40,  40,  50)     # Road border
YELLOW      = (255, 220, 50)     # Lane markings
GREEN       = (50,  220, 100)    # Car body
BLUE        = (50,  120, 255)    # Goal marker
RED         = (220, 50,  50)     # Obstacle / danger
ORANGE      = (255, 140, 0)      # Sensor rays
CYAN        = (0,   200, 200)    # HUD text
PURPLE      = (160, 80,  220)    # Alternate path
LIGHT_GRAY  = (180, 180, 190)    # Grid lines

# ─────────────────────────────────────────────
# CAR PHYSICS
# ─────────────────────────────────────────────
CAR_SPEED        = 3.0    # Pixels per frame
CAR_WIDTH        = 24     # Car rectangle width  (pixels)
CAR_HEIGHT       = 14     # Car rectangle height (pixels)
WAYPOINT_RADIUS  = 8      # Distance (px) to consider a waypoint reached
MAX_STEER_ANGLE  = 30     # Maximum steering angle (degrees) — future use

# ─────────────────────────────────────────────
# PATH PLANNING (A*)
# ─────────────────────────────────────────────
GRID_SIZE       = 20      # Grid cell size in pixels
OBSTACLE_RADIUS = 30      # Safety buffer around each detected obstacle (px)

# Start and goal positions (pixel coordinates on the 900×650 map)
START_POS = (60,  60)
GOAL_POS  = (820, 570)

# ─────────────────────────────────────────────
# VIRTUAL SENSORS
# ─────────────────────────────────────────────
SENSOR_RANGE     = 100    # Ultrasonic sensor range (pixels)
SENSOR_ANGLES    = [-60, -30, 0, 30, 60]   # Sensor beam angles (degrees)
DANGER_THRESHOLD = 40     # Distance (px) below which STOP is triggered

# ─────────────────────────────────────────────
# YOLO PERCEPTION
# ─────────────────────────────────────────────
YOLO_MODEL_PATH  = "yolov8n.pt"
YOLO_CONFIDENCE  = 0.40          # Minimum confidence threshold (0–1)
# Classes we treat as obstacles (COCO class IDs):
# 0=person,1=bicycle,2=car,5=bus,7=truck,9=traffic light,11=stop sign
OBSTACLE_CLASSES = [0, 1, 2, 5, 7, 9, 11]

# ─────────────────────────────────────────────
# LANE DETECTION (OpenCV HoughLines)
# ─────────────────────────────────────────────
LANE_CANNY_LOW   = 50
LANE_CANNY_HIGH  = 150
LANE_RHO         = 1
LANE_THETA_DEG   = 1           # Degrees
LANE_THRESHOLD   = 40
LANE_MIN_LEN     = 40
LANE_MAX_GAP     = 20

# ─────────────────────────────────────────────
# DECISION STATES
# ─────────────────────────────────────────────
STATE_DRIVE  = "DRIVE"
STATE_SLOW   = "SLOW"
STATE_STOP   = "STOP"
STATE_AVOID  = "AVOID"
STATE_ARRIVE = "ARRIVE"

# ─────────────────────────────────────────────
# OUTPUT PATHS
# ─────────────────────────────────────────────
LOG_DIR        = "outputs/logs"
SCREENSHOT_DIR = "outputs/screenshots"
PATH_DIR       = "outputs/paths"