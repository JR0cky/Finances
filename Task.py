import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import time
import random
#from ui_style import setup_ui_footer_and_sidebar
st.set_page_config(layout="wide")  # Use wide mode for more space
# UI Setup
#setup_ui_footer_and_sidebar()

# Constants
GRID_WIDTH = 6
GRID_HEIGHT = 10
BLOCK_SIZE = 25
SPEED = 1  # blocks per second
AUTO_ADVANCE_SCORE = 200   # Example: switch after 500 points
AUTO_ADVANCE_TIME = 60     # Example: switch after 60 seconds


# Block types
BLOCK_TYPES = [
    {'shape': [(0,0)], 'color': 'red'},
    {"shape": [(0, 0), (1, 0)], "color": "blue"},
    {'shape': [(0,0), (0,1)], 'color': 'green'},
    {'shape': [(0,0), (1,0), (1,1)], 'color': 'purple'},
    {'shape': [(0,0), (1,0), (0,1), (1,1)], 'color': 'orange'}
]

# Game state
if "grid" not in st.session_state:
    st.session_state.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
if "current_block" not in st.session_state:
    block_type = random.choice(BLOCK_TYPES)
    st.session_state.current_block = {
        "x": GRID_WIDTH // 2,
        "y": 0,
        "last_move": time.time(),
        "shape": block_type["shape"],
        "color": block_type["color"],
    }
if "score" not in st.session_state:
    st.session_state.score = 0
if "started" not in st.session_state:
    st.session_state.started = False
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None


def clear_lines():
    lines_cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if all(st.session_state.grid[y]):
            for y2 in range(y, 0, -1):
                st.session_state.grid[y2] = st.session_state.grid[y2 - 1].copy()
            st.session_state.grid[0] = 0
            lines_cleared += 1
    return lines_cleared

def create_game_board():
    img = Image.new("RGB", (GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), "white")
    draw = ImageDraw.Draw(img)

    for i in range(GRID_WIDTH + 1):
        draw.line([(i * BLOCK_SIZE, 0), (i * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE)], fill="gray")
    for i in range(GRID_HEIGHT + 1):
        draw.line([(0, i * BLOCK_SIZE), (GRID_WIDTH * BLOCK_SIZE, i * BLOCK_SIZE)], fill="gray")

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if st.session_state.grid[y, x] == 1:
                draw.rectangle(
                    [(x * BLOCK_SIZE, y * BLOCK_SIZE), ((x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE)],
                    fill="gray",
                )

    for block_part in st.session_state.current_block["shape"]:
        x = st.session_state.current_block["x"] + block_part[0]
        y = st.session_state.current_block["y"] + block_part[1]
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            draw.rectangle(
                [(x * BLOCK_SIZE, y * BLOCK_SIZE), ((x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE)],
                fill=st.session_state.current_block["color"],
            )
    return img

def check_collision():
    for block_part in st.session_state.current_block["shape"]:
        x = st.session_state.current_block["x"] + block_part[0]
        y = st.session_state.current_block["y"] + block_part[1]
        if y + 1 >= GRID_HEIGHT or x < 0 or x >= GRID_WIDTH:
            return True
        if y + 1 < GRID_HEIGHT and st.session_state.grid[y + 1, x] == 1:
            return True
    return False

def check_side_collision(dx):
    for block_part in st.session_state.current_block["shape"]:
        x = st.session_state.current_block["x"] + block_part[0] + dx
        y = st.session_state.current_block["y"] + block_part[1]
        if x < 0 or x >= GRID_WIDTH:
            return True
        if y < GRID_HEIGHT and st.session_state.grid[y, x] == 1:
            return True
    return False

def check_rotation_collision(rotated_shape):
    for block_part in rotated_shape:
        x = st.session_state.current_block["x"] + block_part[0]
        y = st.session_state.current_block["y"] + block_part[1]
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True
        if st.session_state.grid[y, x] == 1:
            return True
    return False

def rotate_shape(shape, clockwise=True):
    return [(-y, x) if clockwise else (y, -x) for x, y in shape]

def update_game_state():
    current_time = time.time()
    if current_time - st.session_state.current_block["last_move"] >= 1 / SPEED:
        if not check_collision():
            st.session_state.current_block["y"] += 1
            st.session_state.current_block["last_move"] = current_time
        else:
            for part in st.session_state.current_block["shape"]:
                x = st.session_state.current_block["x"] + part[0]
                y = st.session_state.current_block["y"] + part[1]
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    st.session_state.grid[y, x] = 1
            lines = clear_lines()
            if lines > 0:
                st.session_state.score += lines * 100
            new_block = random.choice(BLOCK_TYPES)
            st.session_state.current_block = {
                "x": GRID_WIDTH // 2,
                "y": 0,
                "last_move": current_time,
                "shape": new_block["shape"],
                "color": new_block["color"],
            }
            if lines > 0:
                st.rerun()

def check_game_over():
    if np.any(st.session_state.grid[0] == 1):
        st.session_state.game_over = True
        return True
    return False

st.title("🧱 Tetris")
st.markdown("""
    <style>
    button[kind="secondary"] {
        font-size: 18px !important;
        padding: 0.4em 0.6em !important;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown(f"**Score:** {st.session_state.score}")
# Layout: left for game board, right for vertical controls
board_col, controls_col = st.columns([3, 1])  # Adjust ratio as needed

with board_col:
    if st.session_state.started or st.session_state.game_over:
        st.image(create_game_board(), use_container_width=False)

    # Game Start / Restart logic
    if not st.session_state.started and not st.session_state.game_over:
        if st.button("▶️ Spiel beginnen", use_container_width=True):
            st.session_state.started = True
            st.session_state.start_time = time.time()

    elif st.session_state.game_over:
        st.error("💀 **Game Over!**")
        if st.button("🔄 Neues Spiel", use_container_width=True):
            st.session_state.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
            st.session_state.score = 0
            st.session_state.started = True
            st.session_state.game_over = False
            st.session_state.start_time = time.time()

with controls_col:
    if st.session_state.started and not st.session_state.game_over:
        if st.button("⬅️", use_container_width=True):
            if not check_side_collision(-1):
                st.session_state.current_block["x"] -= 1

        if st.button("↺", use_container_width=True):
            rotated = rotate_shape(st.session_state.current_block["shape"], clockwise=False)
            if not check_rotation_collision(rotated):
                st.session_state.current_block["shape"] = rotated

        if st.button("➡️", use_container_width=True):
            if not check_side_collision(1):
                st.session_state.current_block["x"] += 1

        if st.button("↻", use_container_width=True):
            rotated = rotate_shape(st.session_state.current_block["shape"], clockwise=True)
            if not check_rotation_collision(rotated):
                st.session_state.current_block["shape"] = rotated

        if st.button("⬇️", use_container_width=True):
            if not check_collision():
                st.session_state.current_block["y"] += 1
                st.session_state.current_block["last_move"] = time.time()

# Auto switch
if st.session_state.start_time:
    elapsed = time.time() - st.session_state.start_time
    if st.session_state.score >= AUTO_ADVANCE_SCORE or elapsed >= AUTO_ADVANCE_TIME:
        st.switch_page("pages/6_Texts.py")

# Game logic loop
if st.session_state.started and not st.session_state.game_over:
    if not check_game_over():
        update_game_state()
    time.sleep(0.1)
    st.rerun()


       
        

        







# Game loop
if st.session_state.started and not st.session_state.game_over:
    if not check_game_over():
        update_game_state()
    time.sleep(0.1)
    st.rerun()
