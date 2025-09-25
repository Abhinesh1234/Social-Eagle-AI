import streamlit as st
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="🐍 Advanced Snake Game",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"

@dataclass
class Position:
    x: int
    y: int
    
    def __add__(self, other):
        return Position(self.x + other.value[0], self.y + other.value[1])
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

@dataclass
class GameConfig:
    board_width: int = 20
    board_height: int = 15
    initial_length: int = 3
    speeds: dict = field(default_factory=lambda: {
        "Easy": 1000,    # milliseconds between moves
        "Medium": 600, 
        "Hard": 300, 
        "Expert": 150
    })

@dataclass
class GameStats:
    score: int = 0
    food_eaten: int = 0
    time_played: float = 0
    moves_made: int = 0
    high_score: int = 0
    games_played: int = 0

class SnakeGame:
    def __init__(self, config: GameConfig):
        self.config = config
        self.reset_game()
        
    def reset_game(self):
        center_x = self.config.board_width // 2
        center_y = self.config.board_height // 2
        
        self.snake = [
            Position(center_x, center_y),
            Position(center_x - 1, center_y),
            Position(center_x - 2, center_y)
        ]
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.food_eaten = 0
        self.start_time = time.time()
        self.moves_made = 0
        self.game_state = GameState.PLAYING
        
    def generate_food(self) -> Position:
        while True:
            food_pos = Position(
                random.randint(0, self.config.board_width - 1),
                random.randint(0, self.config.board_height - 1)
            )
            if food_pos not in self.snake:
                return food_pos
    
    def is_valid_position(self, pos: Position) -> bool:
        return (0 <= pos.x < self.config.board_width and 
                0 <= pos.y < self.config.board_height)
    
    def move_snake(self) -> bool:
        head = self.snake[0]
        new_head = head + self.direction
        
        # Check wall collision
        if not self.is_valid_position(new_head):
            return False
            
        # Check self collision
        if new_head in self.snake:
            return False
        
        self.snake.insert(0, new_head)
        self.moves_made += 1
        
        # Check food consumption
        if new_head == self.food:
            self.score += 10
            self.food_eaten += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()
            
        return True
    
    def change_direction(self, new_direction: Direction):
        # Prevent reversing into itself
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite[self.direction]:
            self.direction = new_direction
    
    def get_game_time(self) -> float:
        return time.time() - self.start_time

def load_stats() -> GameStats:
    """Load game statistics from session state"""
    if 'game_stats' not in st.session_state:
        st.session_state.game_stats = GameStats()
    return st.session_state.game_stats

def save_stats(stats: GameStats):
    """Save game statistics to session state"""
    st.session_state.game_stats = stats

def apply_custom_css():
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .game-board {
        display: grid;
        gap: 1px;
        background-color: #2d5a27;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        margin: 20px auto;
        width: fit-content;
    }
    
    .cell {
        width: 25px;
        height: 25px;
        border-radius: 3px;
        transition: all 0.1s ease;
    }
    
    .empty { background-color: #90EE90; }
    .snake-head { 
        background: radial-gradient(circle, #2E7D32, #1B5E20);
        box-shadow: inset 0 0 10px rgba(255,255,255,0.3);
        border: 2px solid #4CAF50;
    }
    .snake-body { 
        background: linear-gradient(45deg, #4CAF50, #45a049);
        border: 1px solid #2E7D32;
    }
    .food { 
        background: radial-gradient(circle, #FF5722, #D84315);
        box-shadow: 0 0 10px rgba(255, 87, 34, 0.7);
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .game-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .control-info {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .game-over {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 20px 0;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .achievement {
        background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        color: #2d3436;
        font-weight: bold;
        text-align: center;
        animation: bounce 0.5s ease;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .moving-indicator {
        background: linear-gradient(135deg, #00b894, #00cec9);
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        animation: pulse 1s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def render_game_board(game: SnakeGame) -> str:
    board_html = f'<div class="game-board" style="grid-template-columns: repeat({game.config.board_width}, 1fr);">'
    
    for y in range(game.config.board_height):
        for x in range(game.config.board_width):
            pos = Position(x, y)
            cell_class = "empty"
            
            if pos == game.snake[0]:  # Head
                cell_class = "snake-head"
            elif pos in game.snake[1:]:  # Body
                cell_class = "snake-body"
            elif pos == game.food:
                cell_class = "food"
            
            board_html += f'<div class="cell {cell_class}"></div>'
    
    board_html += '</div>'
    return board_html

def show_achievements(stats: GameStats):
    achievements = []
    
    if stats.food_eaten >= 10:
        achievements.append("🍎 Food Lover - Ate 10+ foods!")
    if stats.food_eaten >= 50:
        achievements.append("🏆 Snake Master - Ate 50+ foods!")
    if stats.high_score >= 100:
        achievements.append("💯 Century Club - Scored 100+!")
    if stats.games_played >= 10:
        achievements.append("🎮 Persistent Player - 10+ games played!")
    if stats.moves_made >= 1000:
        achievements.append("🚀 Movement Master - 1000+ moves made!")
    
    if achievements:
        st.markdown("### 🏅 Achievements")
        for achievement in achievements[-3:]:  # Show last 3 achievements
            st.markdown(f'<div class="achievement">{achievement}</div>', unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    # Header
    st.markdown('<h1 class="main-header">🐍 Advanced Snake Game</h1>', unsafe_allow_html=True)
    
    # Initialize game state
    if 'game' not in st.session_state:
        st.session_state.game = SnakeGame(GameConfig())
        st.session_state.last_move_time = time.time()
    
    game = st.session_state.game
    stats = load_stats()
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎮 Game Controls")
        
        # Difficulty selection
        difficulty = st.selectbox(
            "Select Difficulty",
            options=["Easy", "Medium", "Hard", "Expert"],
            index=1,
            key="difficulty_select"
        )
        
        speed_ms = GameConfig().speeds[difficulty]
        
        st.markdown(f"""
        <div class="control-info">
            <strong>Controls:</strong><br>
            ⬆️ W or ↑ - Move Up<br>
            ⬇️ S or ↓ - Move Down<br>
            ⬅️ A or ← - Move Left<br>
            ➡️ D or → - Move Right<br>
            <strong>Speed:</strong> {1000/speed_ms:.1f} moves/sec
        </div>
        """, unsafe_allow_html=True)
        
        # Game controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎮 New Game"):
                st.session_state.game = SnakeGame(GameConfig())
                st.session_state.last_move_time = time.time()
                st.rerun()
        
        with col2:
            if game.game_state == GameState.PLAYING:
                if st.button("⏸️ Pause"):
                    game.game_state = GameState.PAUSED
                    st.rerun()
            elif game.game_state == GameState.PAUSED:
                if st.button("▶️ Resume"):
                    game.game_state = GameState.PLAYING
                    st.session_state.last_move_time = time.time()
                    st.rerun()
        
        # Statistics
        st.markdown(f"""
        <div class="game-stats">
            <h3>📊 Current Game</h3>
            <strong>Score:</strong> {game.score}<br>
            <strong>Food Eaten:</strong> {game.food_eaten}<br>
            <strong>Snake Length:</strong> {len(game.snake)}<br>
            <strong>Moves Made:</strong> {game.moves_made}<br>
            <strong>Time:</strong> {game.get_game_time():.1f}s
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="game-stats">
            <h3>🏆 All Time Stats</h3>
            <strong>High Score:</strong> {stats.high_score}<br>
            <strong>Games Played:</strong> {stats.games_played}<br>
            <strong>Total Food:</strong> {stats.food_eaten}<br>
            <strong>Total Moves:</strong> {stats.moves_made}<br>
            <strong>Total Time:</strong> {stats.time_played:.1f}s
        </div>
        """, unsafe_allow_html=True)
        
        show_achievements(stats)
    
    # Auto-refresh only when game is playing
    refresh_interval = None
    if game.game_state == GameState.PLAYING:
        refresh_interval = speed_ms
        st.markdown(f"""
        <div class="moving-indicator">
            🐍 Snake is Moving! (Next move in {speed_ms}ms)
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-refresh component
    if refresh_interval:
        count = st_autorefresh(interval=refresh_interval, key="snake_refresh")
        
        # Move snake automatically
        if game.game_state == GameState.PLAYING:
            current_time = time.time()
            time_since_last_move = (current_time - st.session_state.last_move_time) * 1000
            
            if time_since_last_move >= speed_ms * 0.8:  # 80% of interval for smoother movement
                if not game.move_snake():
                    # Game over
                    game.game_state = GameState.GAME_OVER
                    
                    # Update statistics
                    if game.score > stats.high_score:
                        stats.high_score = game.score
                    stats.games_played += 1
                    stats.food_eaten += game.food_eaten
                    stats.moves_made += game.moves_made
                    stats.time_played += game.get_game_time()
                    save_stats(stats)
                
                st.session_state.last_move_time = current_time
    
    # Main game area
    if game.game_state == GameState.GAME_OVER:
        st.markdown(f"""
        <div class="game-over">
            <h2>🎮 Game Over!</h2>
            <h3>Final Score: {game.score}</h3>
            <p>Snake Length: {len(game.snake)} | Food Eaten: {game.food_eaten}</p>
            <p>Time Played: {game.get_game_time():.1f} seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        if game.score > stats.high_score:
            st.balloons()
            st.success("🎉 New High Score! 🎉")
    
    elif game.game_state == GameState.PAUSED:
        st.info("⏸️ Game Paused - Click Resume to continue")
    
    # Render game board
    board_html = render_game_board(game)
    st.markdown(board_html, unsafe_allow_html=True)
    
    # Direction Controls
    st.markdown("### 🕹️ Direction Controls")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Left (A)", key="left_btn"):
            if game.game_state == GameState.PLAYING:
                game.change_direction(Direction.LEFT)
    
    with col2:
        if st.button("⬆️ Up (W)", key="up_btn"):
            if game.game_state == GameState.PLAYING:
                game.change_direction(Direction.UP)
    
    with col3:
        if st.button("⬇️ Down (S)", key="down_btn"):
            if game.game_state == GameState.PLAYING:
                game.change_direction(Direction.DOWN)
    
    with col4:
        if st.button("➡️ Right (D)", key="right_btn"):
            if game.game_state == GameState.PLAYING:
                game.change_direction(Direction.RIGHT)
    
    # Game status indicator
    if game.game_state == GameState.PLAYING:
        direction_emoji = {"UP": "⬆️", "DOWN": "⬇️", "LEFT": "⬅️", "RIGHT": "➡️"}
        st.info(f"🐍 Moving {direction_emoji[game.direction.name]} | Next food at ({game.food.x}, {game.food.y})")
    
    # Instructions
    with st.expander("📖 How to Play", expanded=False):
        st.markdown("""
        **Objective:** Control the snake to eat food and grow as long as possible!
        
        **Rules:**
        - The snake moves automatically in the chosen direction
        - Use the direction buttons to change direction
        - Eat the red food (🍎) to grow and increase your score
        - Avoid hitting the walls or your own body
        - The game gets more challenging as the snake grows longer
        
        **Scoring:**
        - Each food eaten: +10 points
        - Try to beat your high score!
        
        **Tips:**
        - Plan your moves ahead to avoid trapping yourself
        - Use the corners wisely to navigate tight spaces
        - Higher difficulty levels increase the snake's speed
        
        **Installation Note:**
        To run this locally, install: `pip install streamlit streamlit-autorefresh`
        """)

if __name__ == "__main__":
    main()