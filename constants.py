import os

# --- Constants ---
WIDTH = 1280
HEIGHT = 720
FPS = 60
SAVE_FILE = "savegame.json"
HIGHSCORE_FILE = "highscore.json"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)

# --- Game States ---
ACCOUNT_SELECTION = 'account_selection'
START_SCREEN = 'start_screen'
PLAYING = 'playing'
UPGRADING = 'upgrading'
GAME_OVER = 'game_over'
GAME_WON = 'game_won'
PAUSED = 'paused'
SKILL_TREE_VIEW = 'skill_tree_view'
TUTORIAL_POPUP = 'tutorial_popup'

# --- Game Modes ---
NORMAL = 'normal'
DUNGEON = 'dungeon'
ENDLESS = 'endless'
TUTORIAL = 'tutorial'

# --- Game Settings ---
PLAYER_SIZE = 30
PLAYER_SPEED = 250
PLAYER_HEALTH = 100
PLAYER_ATTACK_SPEED = 500  # ms

ENEMY_SIZE = 25
ENEMY_SPEED = 120
ENEMY_HEALTH = 10
ENEMY_DAMAGE = 10

PROJECTILE_SIZE = 10
PROJECTILE_SPEED = 600

# --- File Paths ---
# Get the absolute path to the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
FONT_NAME = os.path.join(assets_dir, "SourceHanSansSC-Regular.ttf")
