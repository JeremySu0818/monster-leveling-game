import os
import sys
import random
import enum
import json
import pygame
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Callable

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]  # PyInstaller 打包後執行目錄
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))  # 一般執行
    return os.path.join(base_path, relative_path)



# --- Gemini Boss Generation Stub (for demonstration) ---
def call_gemini_boss_generation_api(boss_name: str, current_boss_level: int, player_max_hp: int, player_attack: int) -> dict:
    """
    Generates a specific boss based on its name and current level.
    Stats scale with boss_level rather than directly with player_level.
    """
    base_hp = 500
    base_attack = 20 
    
    boss_hp = int(base_hp * (1 + 0.15 * (current_boss_level - 1))) 
    boss_attack = int(base_attack * (1 + 0.08 * (current_boss_level - 1))) 
    
    if boss_attack < 5: boss_attack = 5 
    if boss_hp < 100: boss_hp = 100 

    elements = ["FIRE", "WATER", "WIND", "ROCK", "ICE", "ELECTRO", "GRASS"]
    fixed_element = random.choice(elements)

    boss_skills = [
        {"name": f"{fixed_element.capitalize()} Strike", "damage": int(boss_attack * 1.0), "desc": f"Deals {fixed_element.lower()} damage to a single target."}, 
        {"name": f"Area {fixed_element.capitalize()} Burst", "damage": int(boss_attack * 0.6), "desc": f"Deals {fixed_element.lower()} damage to all players."} 
    ]

    boss_intro_texts = [
        f"The {boss_name} at Level {current_boss_level} appears!",
        f"A fearsome {boss_name} (Lv.{current_boss_level}) blocks your path.",
        f"Prepare to face the {boss_name} (Lv.{current_boss_level})!"
    ]

    boss_passive_hp_recovery_rate = 0.02 
    boss_passive = f"Recovers {int(boss_hp * boss_passive_hp_recovery_rate)} HP each turn."


    return {
        "name": boss_name,
        "element": fixed_element,
        "level": current_boss_level,
        "hp": boss_hp,
        "attack": boss_attack,
        "skills": boss_skills,
        "passive": boss_passive,
        "battle_intro": random.choice(boss_intro_texts)
    }

# --- Pygame Initialization ---
pygame.init()

# --- Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

FONT_SIZE = 24
LARGE_FONT_SIZE = 48

# --- Asset Loading ---
BACKGROUND_IMAGE_PATH = resource_path(os.path.join('assets', 'images', 'background.jpg'))

try:
    background = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except FileNotFoundError:
    background = None
    print(f"⚠️ Background image not found at {BACKGROUND_IMAGE_PATH}. Using black background.")

FONT_PATH = resource_path(os.path.join('assets', 'fonts', 'NotoSansMonoCJKtc-Regular.otf'))

try:
    font = pygame.font.Font(FONT_PATH, FONT_SIZE)
    large_font = pygame.font.Font(FONT_PATH, LARGE_FONT_SIZE)
except FileNotFoundError:
    print("⚠️ 找不到外部字型，改用系統字型")
    font = pygame.font.SysFont("arial", FONT_SIZE)
    large_font = pygame.font.SysFont("arial", LARGE_FONT_SIZE)

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 215, 0)
PURPLE = (128, 0, 128) 
BOSS_COLOR = (139, 0, 0) 
DARK_BLUE = (0, 0, 100) 
HEALTH_BAR_COLOR = (30, 200, 30) # Green for HP bar
BOSS_INFO_BG = (30, 30, 30, 180) # Semi-transparent dark background for boss info
SHOP_BG_COLOR = (40, 40, 60, 200) # Semi-transparent dark blue for shop background

# --- Game Mechanics Constants ---
MONSTER_DEFEAT_EXP = 50 
NORMAL_MONSTER_ATTACK_DAMAGE = 3 
SWEET_CHICKEN_DROP_RATE = 0.4 
MAX_PLAYERS = 5
MAX_SKILLS_PER_PLAYER = 5
MAX_SLIMES_ON_SCREEN = 7 

# --- Enums ---
class Element(enum.Enum):
    FIRE = 1 
    WATER = 2 
    WIND = 3 
    ROCK = 4 
    ICE = 5 
    ELECTRO = 6 
    GRASS = 7 

# --- Element Icons (assuming you have these image files) ---
element_icons = {}

def safe_load_image(path: str):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (32, 32))
    except pygame.error:
        print(f"⚠️ Could not load image at {path}. Using default icon (or None).")
        return None

# Uncomment and adjust paths if you have actual element icon images
# element_icons.update({
#     Element.FIRE: safe_load_image(os.path.join('assets', 'elements', 'fire.png')),
#     Element.WATER: safe_load_image(os.path.join('assets', 'elements', 'water.png')),
#     Element.WIND: safe_load_image(os.path.join('assets', 'elements', 'wind.png')),
#     Element.ROCK: safe_load_image(os.path.join('assets', 'elements', 'rock.png')),
#     Element.ICE: safe_load_image(os.path.join('assets', 'elements', 'ice.png')),
#     Element.ELECTRO: safe_load_image(os.path.join('assets', 'elements', 'electro.png')),
#     Element.GRASS: safe_load_image(os.path.join('assets', 'elements', 'grass.png'))
# })


# --- Dataclasses ---
@dataclass
class Skill:
    name: str
    damage: int # 技能基礎傷害，會再乘以 skill_mastery
    element: Element

@dataclass
class Player:
    name: str
    level: int = 1
    experience: int = 0
    hp: int = 100
    max_hp: int = 100
    base_attack: int = 10 # 玩家的普通攻擊基礎值
    skill_mastery: float = 1.0 # 技能和元素反應的精通倍率
    sweet_chickens: int = 0
    skills: List[Skill] = field(default_factory=list)
    armor: int = 0  # 新增護甲屬性
    gold: int = 0  # 新增金幣屬性
    items: List[str] = field(default_factory=list) # 記錄已購買商品
    skill_bonus_percent: float = 0.0 # 元素強化徽章效果，百分比

    @property
    def attack(self): # 讓原有的 player.attack 屬性返回 base_attack
        return self.base_attack

@dataclass
class Monster:
    name: str
    hp: int
    element: Element
    level: int = 1 
    attack: int = 0 
    skills: List[dict] = field(default_factory=list) 
    passive: str = "" 
    battle_intro: str = ""
    element_aura: Optional[Element] = None 
    max_hp: int = 0 

    def __post_init__(self):
        if self.max_hp == 0:
            self.max_hp = self.hp

# --- Game Data (Simplified Slime Information based on your provided table) ---
element_slime_data = {
    "Pyro Slime": {
        "element": Element.FIRE, "hp_range": (30, 45), "attack": 3, "display_icon": "🔥"
    },
    "Hydro Slime": {
        "element": Element.WATER, "hp_range": (25, 40), "attack": 2, "display_icon": "💧"
    },
    "Electro Slime": {
        "element": Element.ELECTRO, "hp_range": (25, 40), "attack": 4, "display_icon": "⚡"
    },
    "Cryo Slime": {
        "element": Element.ICE, "hp_range": (28, 42), "attack": 3, "display_icon": "❄️"
    },
    "Anemo Slime": {
        "element": Element.WIND, "hp_range": (22, 38), "attack": 2, "display_icon": "🌪️"
    },
    "Geo Slime": {
        "element": Element.ROCK, "hp_range": (35, 50), "attack": 4, "display_icon": "🪨"
    },
    "Dendro Slime": {
        "element": Element.GRASS, "hp_range": (25, 40), "attack": 3, "display_icon": "🌿"
    }
}

# 輔助函數：判斷是否為 Boss 
def is_boss_monster(monster_name: str) -> bool:
    return monster_name in BossManager.BOSS_NAMES

# --- Boss Management Class ---
@dataclass
class BossState:
    name: str
    level: int = 1
    unlocked: bool = False 

class BossManager:
    BOSS_NAMES = [ 
        "Giant Slime King", "Ancient Earth Elemental", "Storm Herald", 
        "Frozen Lord", "Thunder Tyrant", "Forest Spirit", "Abyssal Horror"
    ]
    BOSS_DATA_FILE = 'boss_data.json'
    
    _boss_states: Dict[str, BossState] = field(default_factory=dict)

    @classmethod
    def initialize_boss_states(cls):
        """初始化或載入所有 Boss 的狀態。"""
        if not os.path.exists(cls.BOSS_DATA_FILE):
            cls._boss_states = {name: BossState(name=name, level=1, unlocked=False) for name in cls.BOSS_NAMES}
            if cls.BOSS_NAMES:
                cls._boss_states[cls.BOSS_NAMES[0]].unlocked = True 
            cls.save_boss_states()
        else:
            cls.load_boss_states()

    @classmethod
    def save_boss_states(cls):
        """保存所有 Boss 的狀態到 JSON 文件。"""
        data = {name: state.__dict__ for name, state in cls._boss_states.items()}
        try:
            with open(cls.BOSS_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("Boss data saved successfully.")
        except Exception as e:
            print(f"Error saving boss data: {e}")

    @classmethod
    def load_boss_states(cls):
        """從 JSON 文件載入所有 Boss 的狀態。"""
        if not os.path.exists(cls.BOSS_DATA_FILE):
            cls.initialize_boss_states() 
            return

        try:
            with open(cls.BOSS_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"Warning: {cls.BOSS_DATA_FILE} is empty. Initializing boss data.")
                    cls.initialize_boss_states()
                    return
                data = json.loads(content)
            
            loaded_states = {}
            for name, state_data in data.items():
                if name in cls.BOSS_NAMES: 
                    loaded_states[name] = BossState(
                        name=state_data.get('name', name),
                        level=int(state_data.get('level', 1)),
                        unlocked=bool(state_data.get('unlocked', False))
                    )
            for name in cls.BOSS_NAMES:
                if name not in loaded_states:
                    loaded_states[name] = BossState(name=name, level=1, unlocked=False)
            
            if cls.BOSS_NAMES and not loaded_states[cls.BOSS_NAMES[0]].unlocked:
                 loaded_states[cls.BOSS_NAMES[0]].unlocked = True

            cls._boss_states = loaded_states
            print(f"Loaded {len(cls._boss_states)} boss states.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {cls.BOSS_DATA_FILE}: {e}. File might be corrupted. Reinitializing.")
            cls.initialize_boss_states() 
        except Exception as e:
            print(f"An unexpected error occurred during boss data loading: {e}. Reinitializing.")
            cls.initialize_boss_states() 

    @classmethod
    def get_boss_state(cls, name: str) -> Optional[BossState]:
        return cls._boss_states.get(name)

    @classmethod
    def get_all_boss_states(cls) -> List[BossState]:
        return list(cls._boss_states.values())

    @classmethod
    def level_up_boss(cls, name: str):
        """提升指定 Boss 的等級。"""
        if name in cls._boss_states:
            cls._boss_states[name].level += 1
            cls.save_boss_states()
            print(f"Boss {name} leveled up to {cls._boss_states[name].level}.")

    @classmethod
    def unlock_next_boss(cls, defeated_boss_name: str):
        """解鎖下一個 Boss。"""
        try:
            defeated_index = cls.BOSS_NAMES.index(defeated_boss_name)
            if defeated_index + 1 < len(cls.BOSS_NAMES):
                next_boss_name = cls.BOSS_NAMES[defeated_index + 1]
                if not cls._boss_states[next_boss_name].unlocked:
                    cls._boss_states[next_boss_name].unlocked = True
                    cls.save_boss_states()
                    print(f"Unlocked next boss: {next_boss_name}.")
                    return next_boss_name
        except ValueError:
            pass 
        return None

# 初始化 BossManager
BossManager.initialize_boss_states()


# --- Game Logic Functions ---
def generate_all_seven_slimes() -> List[Monster]:
    """
    Generates a fixed list of all seven types of slime monsters.
    Their stats are based on the simplified Genshin-style slime data.
    """
    slimes = []
    for slime_name, slime_info in element_slime_data.items():
        element = slime_info["element"]
        min_hp, max_hp = slime_info["hp_range"]
        hp = random.randint(min_hp, max_hp)
        attack = slime_info["attack"] 
        level = 1 

        slimes.append(
            Monster(
                name=slime_name, 
                hp=hp, 
                max_hp=hp, 
                element=element, 
                level=level, 
                attack=attack, 
                skills=[], 
                passive="", 
                battle_intro="",
                element_aura=element 
            )
        )
    random.shuffle(slimes) 
    return slimes


def generate_boss_from_json(data: dict) -> Monster:
    name = data.get('name', 'Unknown Boss')
    hp = int(data.get('hp', 1000))
    element_str = data.get('element', 'FIRE').upper()
    try:
        element = Element[element_str]
    except KeyError:
        element = Element.FIRE  # fallback

    boss_level = int(data.get('level', 1))
    boss_attack = int(data.get('attack', 100))
    boss_skills = data.get('skills', [])
    boss_passive = data.get('passive', '')
    boss_intro = data.get('battle_intro', 'A powerful foe appears!')

    return Monster(name=name, hp=hp, max_hp=hp, element=element, 
                   level=boss_level, attack=boss_attack, 
                   skills=boss_skills, passive=boss_passive, 
                   battle_intro=boss_intro, element_aura=None)

def show_boss_intro(boss_intro: str):
    print(f"BOSS 登場：{boss_intro}")

class Button:
    def __init__(self, rect, color, hover_color, text, text_color=BLACK, font=font, padding=10):
        self.font = font
        self.text = text
        self.text_color = text_color
        self.padding = padding
        self.text_surface = self.font.render(self.text, True, self.text_color)
        text_width, text_height = self.text_surface.get_size()
        
        x, y, width, height = rect
        width = max(width, text_width + 2 * padding)
        height = max(height, text_height + 2 * padding)
        self.rect = pygame.Rect(x, y, width, height)
        
        self.color = color
        self.hover_color = hover_color
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect, border_radius=12)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=12) 
        self.text_rect = self.text_surface.get_rect(center=self.rect.center) 
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 新增元素反應計算函數
def calculate_elemental_reaction(
    player: Player, 
    skill_element: Element, 
    target_monster: Monster, 
    base_skill_damage: int, # 現在傳入的是技能的基礎傷害
    all_monsters: List[Monster] 
) -> Tuple[int, str]:
    """
    根據玩家技能元素和怪物元素附著狀態計算元素反應。
    返回額外傷害和反應描述。
    元素反應現在會與 player.skill_mastery 掛鉤，且倍率更高。
    """
    reaction_damage_bonus = 0.0 
    reaction_message = ""
    target_aura = target_monster.element_aura

    # 確保 skill_mastery 至少為 1.0 以避免負面影響
    effective_skill_mastery = max(1.0, player.skill_mastery)

    # 技能額外傷害百分比
    skill_bonus_multiplier = 1 + (player.skill_bonus_percent / 100.0)

    if target_aura is None:
        target_monster.element_aura = skill_element
        reaction_message = f"Applied {skill_element.name.capitalize()} Aura."
        return 0, reaction_message 

    # === 增幅反應 (Vaporize/Melt) - 倍率傷害，現在受到 skill_mastery 影響 ===
    if (skill_element == Element.FIRE and target_aura == Element.WATER):
        reaction_damage_bonus = base_skill_damage * (1.5 + effective_skill_mastery * 0.1) * skill_bonus_multiplier # 提高倍率
        reaction_message = f"Vaporize! (+{int(reaction_damage_bonus)} damage)"
        target_monster.element_aura = None 
    elif (skill_element == Element.WATER and target_aura == Element.FIRE):
        reaction_damage_bonus = base_skill_damage * (2.0 + effective_skill_mastery * 0.15) * skill_bonus_multiplier # 提高倍率
        reaction_message = f"Vaporize! (+{int(reaction_damage_bonus)} damage)"
        target_monster.element_aura = None 
    elif (skill_element == Element.FIRE and target_aura == Element.ICE):
        reaction_damage_bonus = base_skill_damage * (2.0 + effective_skill_mastery * 0.15) * skill_bonus_multiplier # 提高倍率
        reaction_message = f"Melt! (+{int(reaction_damage_bonus)} damage)"
        target_monster.element_aura = None 
    elif (skill_element == Element.ICE and target_aura == Element.FIRE):
        reaction_damage_bonus = base_skill_damage * (1.5 + effective_skill_mastery * 0.1) * skill_bonus_multiplier # 提高倍率
        reaction_message = f"Melt! (+{int(reaction_damage_bonus)} damage)"
        target_monster.element_aura = None 

    # === 劇變反應 (固定額外傷害或效果) - 現在與 skill_mastery 掛鉤，更顯著 ===
    elif (skill_element == Element.ELECTRO and target_aura == Element.WATER) or \
         (skill_element == Element.WATER and target_aura == Element.ELECTRO):
        reaction_damage_bonus = float(player.level * 10 + effective_skill_mastery * 20) * skill_bonus_multiplier # 顯著提升
        reaction_message = f"Electro-Charged! Deals {int(reaction_damage_bonus)} extra damage!"
        target_monster.element_aura = None 
    elif (skill_element == Element.ELECTRO and target_aura == Element.ICE) or \
         (skill_element == Element.ICE and target_aura == Element.ELECTRO):
        reaction_damage_bonus = float(player.level * 9 + effective_skill_mastery * 18) * skill_bonus_multiplier # 顯著提升
        reaction_message = f"Superconduct! Deals {int(reaction_damage_bonus)} extra damage!"
        target_monster.element_aura = None 
    elif (skill_element == Element.FIRE and target_aura == Element.GRASS) or \
         (skill_element == Element.GRASS and target_aura == Element.FIRE):
        reaction_damage_bonus = float(player.level * 8 + effective_skill_mastery * 15) * skill_bonus_multiplier # 顯著提升
        reaction_message = f"Burning! Deals {int(reaction_damage_bonus)} extra damage!"
        target_monster.element_aura = None 
    elif skill_element == Element.ROCK and target_aura in [Element.FIRE, Element.WATER, Element.ELECTRO, Element.ICE]:
        # 晶化反應回血量也會受到 skill_mastery 影響
        heal_amount = int(player.level * 5 + effective_skill_mastery * 10) 
        player.hp = min(player.hp + heal_amount, player.max_hp) 
        reaction_message = f"Crystallize! Recovered {heal_amount} HP!"
        reaction_damage_bonus = 0.0 
        target_monster.element_aura = None 
    elif skill_element == Element.WIND and target_aura in [Element.FIRE, Element.WATER, Element.ELECTRO, Element.ICE, Element.GRASS]:
        # 擴散反應的傷害也會受到 skill_mastery 影響
        spread_damage = float(player.level * 6 + effective_skill_mastery * 12) * skill_bonus_multiplier 
        for monster in all_monsters:
            if monster.hp > 0 and monster is not target_monster: 
                monster.hp -= int(spread_damage) 
                if monster.hp < 0: monster.hp = 0
        reaction_damage_bonus = spread_damage 
        reaction_message = f"Swirl! Deals {int(spread_damage)} area damage!"
        target_monster.element_aura = None 
    elif (skill_element == Element.GRASS and target_aura == Element.WATER) or \
         (skill_element == Element.WATER and target_aura == Element.GRASS):
        reaction_damage_bonus = float(player.level * 12 + effective_skill_mastery * 25) * skill_bonus_multiplier # 顯著提升
        reaction_message = f"Bloom! Deals {int(reaction_damage_bonus)} extra damage!"
        target_monster.element_aura = None 
    
    elif target_aura != skill_element:
        # 如果是同元素或沒有反應，就附著新元素
        target_monster.element_aura = skill_element
        reaction_message = f"Applied {skill_element.name.capitalize()} Aura."

    return int(reaction_damage_bonus), reaction_message 


def attack_monster(player: Player, monster: Monster, damage_type: str, skill_data: Optional[Skill], all_monsters: List[Monster]) -> Optional[str]:
    """
    修改了攻擊函數，區分普通攻擊和技能攻擊。
    damage_type: 'NORMAL' 或 'SKILL'
    skill_data: 如果是技能攻擊，則為 Skill 物件
    """
    if monster.hp <= 0:
        return None 

    total_damage = 0
    skill_element_used: Optional[Element] = None
    reaction_message = ""

    if damage_type == 'NORMAL':
        total_damage = player.base_attack 
    elif damage_type == 'SKILL' and skill_data:
        # 技能傷害 = 玩家攻擊力 + 技能基礎傷害 * 技能精通倍率
        # 再加上元素強化徽章的百分比加成
        skill_damage = skill_data.damage * player.skill_mastery
        total_damage = player.base_attack + int(skill_damage * (1 + player.skill_bonus_percent / 100.0))
        skill_element_used = skill_data.element
    
    if skill_element_used: # 只有技能攻擊才觸發元素反應
        reaction_damage, reaction_message_part = calculate_elemental_reaction(
            player, skill_element_used, monster, skill_data.damage if skill_data else 0, all_monsters
        )
        total_damage += reaction_damage 
        if reaction_message_part:
            reaction_message = reaction_message_part 

    monster.hp -= total_damage
    
    if monster.hp < 0: 
        monster.hp = 0
    
    player_damage_taken_raw = NORMAL_MONSTER_ATTACK_DAMAGE 
    if is_boss_monster(monster.name):
        player_damage_taken_raw = monster.attack 
    
    # 計算護甲減傷
    player_damage_taken = max(0, player_damage_taken_raw - player.armor)

    player.hp -= player_damage_taken
    if player.hp < 0:
        player.hp = 0

    message_parts = []
    message_parts.append(f"{monster.name} hit for {total_damage}!")
    if reaction_message:
        message_parts.append(f"({reaction_message})")
    
    # 擊敗怪物掉落金幣
    gold_earned = 0
    if monster.hp <= 0:
        monster.hp = 0
        if is_boss_monster(monster.name):
            gain_experience(player, MONSTER_DEFEAT_EXP * 5)
            gold_earned = random.randint(50, 100) # Boss 掉落金幣
            player.gold += gold_earned
            BossManager.level_up_boss(monster.name)
            next_unlocked_boss = BossManager.unlock_next_boss(monster.name)
            
            message_parts.append(f"{monster.name} defeated!")
            if next_unlocked_boss:
                message_parts.append(f"You unlocked {next_unlocked_boss}!")
        else:
            gain_experience(player, MONSTER_DEFEAT_EXP)
            gold_earned = random.randint(5, 10) # 史萊姆掉落金幣
            player.gold += gold_earned
            message_parts.append(f"{monster.name} defeated!")
        
        message_parts.append(f"You earned {gold_earned} Gold!")

        if random.random() < SWEET_CHICKEN_DROP_RATE: 
            player.sweet_chickens += 1
            message_parts.append('Sweet Chicken Dropped! You gained 1 Sweet Chicken.')
    else:
        message_parts.append(f"You took {player_damage_taken} damage from {monster.name}.")

    return " ".join(message_parts)

def draw_popup(surface, message, font):
    text = font.render(message, True, BLACK)
    text_width, text_height = text.get_size()

    min_w = 400
    h = 100
    
    padding_x = 40 
    w = max(min_w, text_width + 2 * padding_x) 

    if w > SCREEN_WIDTH - 40: 
        w = SCREEN_WIDTH - 40

    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2

    pygame.draw.rect(surface, LIGHT_GRAY, (x, y, w, h), border_radius=15)
    pygame.draw.rect(surface, WHITE, (x, y, w, h), 2, border_radius=15)
    
    surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

def create_new_player_gui(players: List[Player]):
    # 調整初始玩家數據，使其更合理
    p = Player(name=f'Player{len(players) + 1}', sweet_chickens=2, max_hp=100, base_attack=15, skill_mastery=1.0, armor=0, gold=50) # 提升初始 base_attack, 初始金幣
    p.skills = [
        Skill("Pyro Blast", 40, Element.FIRE), # 技能基礎傷害可以更高
        Skill("Hydro Splash", 40, Element.WATER),
        Skill("Wind Shear", 35, Element.WIND),
        Skill("Stone Punch", 50, Element.ROCK),
        Skill("Ice Shard", 45, Element.ICE),
        Skill("Thunderbolt", 40, Element.ELECTRO),
        Skill("Nature's Wrath", 35, Element.GRASS)
    ]
    players.append(p)

def gain_experience(player: Player, exp: int) -> Optional[str]:
    player.experience += exp
    level_up_messages = []

    while True:
        exp_threshold = player.level * 100
        if player.experience >= exp_threshold:
            player.experience -= exp_threshold
            player.level += 1
            player.max_hp += 20 # 更高的 HP 成長
            player.hp = player.max_hp
            player.base_attack += 15 # 普通攻擊成長更高
            player.skill_mastery += 0.05 # 技能精通成長，影響技能傷害和元素反應

            level_up_messages.append(f"Level Up! LV {player.level}")
            level_up_messages.append(f"Base Attack +15, Skill Mastery +0.05") # 顯示具體成長
        else:
            break

    if level_up_messages:
        return " ".join(level_up_messages) 
    return None

def save_players_data(players: List[Player]) -> None:
    data = []
    for player in players:
        data.append({
            'name': player.name,
            'level': player.level,
            'experience': player.experience,
            'hp': player.hp,
            'max_hp': player.max_hp,
            'base_attack': player.base_attack,
            'skill_mastery': player.skill_mastery,
            'sweet_chickens': player.sweet_chickens,
            'skills': [{'name': s.name, 'damage': s.damage, 'element': s.element.name} for s in player.skills],
            'armor': player.armor, # 保存護甲
            'gold': player.gold, # 保存金幣
            'items': player.items, # 保存已購買物品
            'skill_bonus_percent': player.skill_bonus_percent # 保存技能額外傷害百分比
        })
    try:
        with open('players.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Player data saved successfully.")
    except Exception as e:
            print(f"Error saving player data: {e}")

def load_players_data(players: List[Player]) -> int:
    if not os.path.exists('players.json'):
        with open('players.json', 'w', encoding='utf-8') as f:
            f.write('[]')
        return 0
    
    try:
        with open('players.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return 0
            data = json.loads(content)
        
        players.clear()
        for p in data:
            # 載入時也需要讀取新的屬性，並提供默認值以兼容舊數據
            new_player = Player(
                name=p.get('name', 'Unknown Player'), 
                level=int(p.get('level', 1)), 
                experience=int(p.get('experience', 0)), 
                hp=int(p.get('hp', 100)), 
                max_hp=int(p.get('max_hp', 100)),
                base_attack=int(p.get('base_attack', 10)), 
                skill_mastery=float(p.get('skill_mastery', 1.0)), 
                sweet_chickens=int(p.get('sweet_chickens', 0)),
                armor=int(p.get('armor', 0)), # 載入護甲
                gold=int(p.get('gold', 0)), # 載入金幣
                items=p.get('items', []), # 載入已購買物品
                skill_bonus_percent=float(p.get('skill_bonus_percent', 0.0)) # 載入技能額外傷害百分比
            )
            for s in p.get('skills', []):
                try:
                    new_player.skills.append(Skill(s.get('name', 'Unknown Skill'), int(s.get('damage', 0)), Element[s.get('element', 'FIRE')]))
                except KeyError:
                    print(f"Warning: Unknown element '{s.get('element')}' for skill '{s.get('name')}'. Skipping skill.")
            players.append(new_player)
        print(f"Loaded {len(players)} players.")
        return len(players)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from players.json: {e}. File might be corrupted.")
        return 0
    except Exception as e:
        print(f"An unexpected error occurred during loading: {e}")
        return 0

# --- Helper function to draw HP bar ---
def draw_health_bar(surface, x, y, width, height, current_hp, max_hp, border_color=WHITE, fill_color=HEALTH_BAR_COLOR, bg_color=RED):
    if max_hp <= 0: 
        max_hp = 1 
    
    pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=5)

    fill_width = int(width * (current_hp / max_hp))
    pygame.draw.rect(surface, fill_color, (x, y, fill_width, height), border_radius=5)

    pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=5)

# --- Shop System ---

@dataclass
class Item:
    name: str
    price: int
    effect: Callable[[Player], str] # effect 是一個函數，接受 Player 物件並返回一個訊息字串
    description: str

class Shop:
    def __init__(self, player: Player):
        self.player = player
        self.items: List[Item] = self._initialize_items()

    def _initialize_items(self) -> List[Item]:
        # 定義所有可購買的商品
        return [
            Item(
                name="初階鐵盔甲", 
                price=60, 
                effect=lambda p: (setattr(p, 'armor', p.armor + 5), f"你的護甲值增加了 5 點！ (目前: {p.armor})")[1],
                description="增加 5 點護甲"
            ),
            Item(
                name="鋼鐵戰甲", 
                price=150, 
                effect=lambda p: (setattr(p, 'armor', p.armor + 10), f"你的護甲值增加了 10 點！ (目前: {p.armor})")[1],
                description="增加 10 點護甲"
            ),
            Item(
                name="攻擊訓練課程", 
                price=80, 
                effect=lambda p: (setattr(p, 'base_attack', p.base_attack + 5), f"你的攻擊力增加了 5 點！ (目前: {p.base_attack})")[1],
                description="增加 5 點基礎攻擊力"
            ),
            Item(
                name="經驗書", 
                price=40, 
                effect=lambda p: gain_experience(p, 100) or f"你獲得了 100 點經驗值！ (目前: {p.experience})", # gain_experience返回None，所以用or
                description="獲得 100 點經驗值"
            ),
            Item(
                name="元素強化徽章", 
                price=200, 
                effect=lambda p: (setattr(p, 'skill_bonus_percent', p.skill_bonus_percent + 10.0), f"所有技能額外傷害增加 10%！ (目前: {p.skill_bonus_percent:.0f}%)")[1],
                description="所有技能額外傷害 +10%"
            ),
        ]

    def draw(self, surface):
        # 商店背景
        shop_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        s = pygame.Surface((shop_rect.width, shop_rect.height), pygame.SRCALPHA)
        s.fill(SHOP_BG_COLOR)
        surface.blit(s, shop_rect.topleft)
        pygame.draw.rect(surface, WHITE, shop_rect, 2, border_radius=15)

        # 商店標題
        title_text = large_font.render("商店", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)

        # 玩家金幣顯示
        gold_text = font.render(f"金幣: {self.player.gold}", True, YELLOW)
        gold_rect = gold_text.get_rect(topright=(shop_rect.right - 20, 80))
        surface.blit(gold_text, gold_rect)

        # 商品列表
        start_y = 150
        item_buttons = []
        for i, item in enumerate(self.items):
            # 判斷是否已購買
            is_purchased = item.name in self.player.items
            
            button_text = f"{item.name} - ${item.price} ({item.description})"
            btn_color = BLUE
            hover_btn_color = LIGHT_GRAY
            text_color = WHITE

            if is_purchased:
                button_text += " (已購買)"
                btn_color = GRAY
                hover_btn_color = (100, 100, 100)
                text_color = DARK_BLUE

            item_button = Button(
                (100, start_y + i * 60, SCREEN_WIDTH - 200, 50), 
                btn_color, 
                hover_btn_color, 
                button_text, 
                text_color, 
                font
            )
            item_button.draw(surface)
            item_buttons.append((item, item_button, is_purchased))
        
        # 返回按鈕
        back_button = Button((SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 50), PURPLE, LIGHT_GRAY, '返回', WHITE)
        back_button.draw(surface)

        return item_buttons, back_button

    def handle_click(self, mouse_pos: Tuple[int, int], item_buttons_data: List[Tuple[Item, Button, bool]]) -> Optional[str]:
        for item, button, is_purchased in item_buttons_data:
            if button.is_clicked(mouse_pos):
                if is_purchased:
                    return "你已經購買過這個商品了！"
                elif self.player.gold >= item.price:
                    self.player.gold -= item.price
                    self.player.items.append(item.name)
                    effect_message = item.effect(self.player)
                    return f"購買成功: {item.name}! 金幣: {self.player.gold}. {effect_message}"
                else:
                    return "金幣不足！"
        return None

# --- Pygame Main Loop ---
clock = pygame.time.Clock()

def main_pygame_loop():
    players = []
    load_players_data(players)

    if not players:
        create_new_player_gui(players)

    current_active_monsters: List[Monster] = [] 
    current_boss_instance: Optional[Monster] = None 

    state = 'MAIN_MENU' 
    current_player_index = 0
    selected_skill_index = None 
    popup_message = None
    popup_end_time = 0

    current_boss_challenge: Optional[BossState] = None 

    shop_instance: Optional[Shop] = None # 商店實例

    running = True
    while running:
        mouse_pos = None
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
                mouse_pos = pygame.mouse.get_pos()

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        # --- State Machine for Game Flow ---
        if state == 'MAIN_MENU': 
            title = large_font.render('Monster Game', True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(title, title_rect)

            start_button = Button((300, 300, 200, 50), BLUE, LIGHT_GRAY, 'Start Game', WHITE)
            shop_button = Button((300, 370, 200, 50), YELLOW, LIGHT_GRAY, 'Shop', BLACK) # 新增商店按鈕
            quit_button_main = Button((300, 440, 200, 50), PURPLE, LIGHT_GRAY, 'Quit', WHITE)

            start_button.draw(screen)
            shop_button.draw(screen) # 繪製商店按鈕
            quit_button_main.draw(screen)

            if mouse_clicked and mouse_pos:
                if start_button.is_clicked(mouse_pos):
                    current_active_monsters.clear()
                    current_active_monsters.extend(generate_all_seven_slimes())
                    current_boss_challenge = None 
                    current_boss_instance = None 
                    state = 'GAMEPLAY' 
                elif shop_button.is_clicked(mouse_pos): # 處理商店按鈕點擊
                    shop_instance = Shop(players[current_player_index])
                    state = 'SHOP'
                elif quit_button_main.is_clicked(mouse_pos):
                    running = False

        elif state == 'SHOP':
            if shop_instance is None: # 確保商店實例存在
                shop_instance = Shop(players[current_player_index])

            item_buttons, back_button = shop_instance.draw(screen)

            if mouse_clicked and mouse_pos:
                if back_button.is_clicked(mouse_pos):
                    state = 'MAIN_MENU'
                    popup_message = None # 清除商店頁面的提示
                else:
                    purchase_result = shop_instance.handle_click(mouse_pos, item_buttons)
                    if purchase_result:
                        popup_message = purchase_result
                        popup_end_time = pygame.time.get_ticks() + 2000

        elif state == 'GAMEPLAY': 
            player = players[current_player_index]

            # 顯示玩家資訊
            for i, text in enumerate([
                f'Name: {player.name}', 
                f'Level: {player.level}', 
                f'HP: {player.hp}/{player.max_hp}',
                f'Base Attack: {player.base_attack}', 
                f'Armor: {player.armor}', # 顯示護甲
                f'Skill Mastery: {player.skill_mastery:.2f}', 
                f'Skill Bonus: {player.skill_bonus_percent:.0f}%', # 顯示技能額外傷害百分比
                f'EXP: {player.experience}/{player.level * 100}', 
                f'Sweet Chicken: {player.sweet_chickens}',
                f'Gold: {player.gold}' # 顯示金幣
            ]):
                screen.blit(font.render(text, True, WHITE), (50, 40 + i * 30))

            # --- 顯示 Boss 資訊和血條 (如果正在進行 Boss 戰，且 Boss 活著) ---
            if current_boss_instance and current_boss_instance.hp > 0: 
                boss = current_boss_instance
                boss_info_text = f'{boss.name} (Lv.{boss.level})'
                boss_hp_text = f'HP: {boss.hp}/{boss.max_hp}'
                boss_attack_text = f'ATK: {boss.attack}'
                boss_element_text = f'Element: {boss.element.name.capitalize()}'
                boss_aura_text = f'Aura: {boss.element_aura.name.capitalize()}' if boss.element_aura else 'Aura: None'

                boss_info_rect = pygame.Rect(SCREEN_WIDTH - 300, 40, 250, 180)
                s = pygame.Surface((boss_info_rect.width, boss_info_rect.height), pygame.SRCALPHA)
                s.fill(BOSS_INFO_BG)
                screen.blit(s, boss_info_rect.topleft)
                pygame.draw.rect(screen, WHITE, boss_info_rect, 2, border_radius=10) 

                screen.blit(font.render(boss_info_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 10))
                screen.blit(font.render(boss_hp_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 40))
                screen.blit(font.render(boss_attack_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 70))
                screen.blit(font.render(boss_element_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 100))
                screen.blit(font.render(boss_aura_text, True, YELLOW), (boss_info_rect.x + 10, boss_info_rect.y + 130))

                hp_bar_x = boss_info_rect.x + 10
                hp_bar_y = boss_info_rect.y + 160
                draw_health_bar(screen, hp_bar_x, hp_bar_y, boss_info_rect.width - 20, 15, boss.hp, boss.max_hp)


            # 根據是否在 Boss 挑戰模式，調整按鈕文本
            attack_button_text = 'Attack Slimes'
            skill_button_text = 'Skill Attack Slimes'
            if current_boss_challenge: 
                attack_button_text = f'Attack {current_boss_challenge.name}'
                skill_button_text = f'Skill {current_boss_challenge.name}'


            attack_button = Button((100, 500, 150, 40), BLUE, LIGHT_GRAY, attack_button_text, WHITE)
            skill_button = Button((300, 500, 150, 40), GREEN, LIGHT_GRAY, skill_button_text, WHITE)
            heal_button = Button((500, 500, 150, 40), YELLOW, LIGHT_GRAY, 'Heal', BLACK)
            quit_button_gameplay = Button((SCREEN_WIDTH - 150, 20, 120, 40), PURPLE, LIGHT_GRAY, 'Quit', WHITE) 
            
            select_boss_button = Button((SCREEN_WIDTH - 150, 80, 120, 40), BOSS_COLOR, RED, 'Select Boss', WHITE)

            attack_button.draw(screen)
            skill_button.draw(screen)
            heal_button.draw(screen)
            quit_button_gameplay.draw(screen)
            select_boss_button.draw(screen) 

            if mouse_clicked and mouse_pos:
                if attack_button.is_clicked(mouse_pos):
                    selected_skill_index = None 
                    if current_boss_challenge:
                        if current_boss_instance and current_boss_instance.hp > 0:
                            current_active_monsters = [current_boss_instance] 
                            state = 'SELECT_MONSTER_FOR_NORMAL_ATTACK' # 新增一個狀態
                        else: 
                            popup_message = "Boss is defeated or not active. Please select another boss."
                            popup_end_time = pygame.time.get_ticks() + 2000
                            current_boss_challenge = None 
                            current_boss_instance = None
                    else: 
                        if not any(m.hp > 0 for m in current_active_monsters if not is_boss_monster(m.name)):
                            current_active_monsters.clear()
                            current_active_monsters.extend(generate_all_seven_slimes())
                        state = 'SELECT_MONSTER_FOR_NORMAL_ATTACK' # 新增一個狀態

                elif skill_button.is_clicked(mouse_pos):
                    if player.skills:
                        selected_skill_index = None 
                        if current_boss_challenge:
                            if current_boss_instance and current_boss_instance.hp > 0:
                                current_active_monsters = [current_boss_instance]
                                state = 'SELECT_SKILL'
                            else:
                                popup_message = "Boss is defeated or not active. Please select another boss."
                                popup_end_time = pygame.time.get_ticks() + 2000
                                current_boss_challenge = None
                                current_boss_instance = None
                        else:
                            if not any(m.hp > 0 for m in current_active_monsters if not is_boss_monster(m.name)):
                                current_active_monsters.clear()
                                current_active_monsters.extend(generate_all_seven_slimes())
                            state = 'SELECT_SKILL'
                    else:
                        popup_message = "No skills available!"
                        popup_end_time = pygame.time.get_ticks() + 2000

                elif heal_button.is_clicked(mouse_pos):
                    if player.sweet_chickens > 0:
                        player.hp = min(player.hp + 20, player.max_hp)
                        player.sweet_chickens -= 1
                        popup_message = 'Healed 20 HP!'
                    else:
                        popup_message = 'No Sweet Chicken!'
                    popup_end_time = pygame.time.get_ticks() + 2000
                elif quit_button_gameplay.is_clicked(mouse_pos):
                    running = False
                elif select_boss_button.is_clicked(mouse_pos): 
                    state = 'SELECT_BOSS'
                    current_active_monsters.clear() 
                    current_boss_instance = None 

        elif state == 'SELECT_BOSS': 
            screen.blit(font.render("Select a Boss to challenge:", True, WHITE), (100, 50))

            boss_states = BossManager.get_all_boss_states()
            boss_buttons = []
            start_y = 50 + FONT_SIZE + 20 

            for i, boss_state in enumerate(boss_states):
                button_text = f'{boss_state.name} (Lv.{boss_state.level})'
                btn_color = BOSS_COLOR
                hover_btn_color = RED
                if not boss_state.unlocked:
                    button_text += " (Locked)"
                    btn_color = GRAY 
                    hover_btn_color = (100, 100, 100) 

                b = Button((100, start_y + i * 50, 600, 40), btn_color, hover_btn_color, button_text, WHITE)
                boss_buttons.append(b)
                b.draw(screen)

            back_button = Button((50, SCREEN_HEIGHT - 60, 100, 40), GRAY, LIGHT_GRAY, 'Back', WHITE)
            back_button.draw(screen)

            if mouse_clicked and mouse_pos:
                if back_button.is_clicked(mouse_pos):
                    state = 'GAMEPLAY' 
                else:
                    for i, b in enumerate(boss_buttons):
                        if b.is_clicked(mouse_pos):
                            selected_boss_state = boss_states[i]
                            if selected_boss_state.unlocked:
                                boss_data_json = call_gemini_boss_generation_api(
                                    selected_boss_state.name, selected_boss_state.level, 
                                    players[current_player_index].max_hp, players[current_player_index].base_attack 
                                )
                                current_boss_instance = generate_boss_from_json(boss_data_json) 
                                current_active_monsters = [current_boss_instance] 
                                current_boss_challenge = selected_boss_state 
                                show_boss_intro(current_boss_instance.battle_intro)
                                popup_message = f"Boss: {current_boss_instance.name} appeared!" 
                                popup_end_time = pygame.time.get_ticks() + 2500
                                state = 'GAMEPLAY' 
                                break
                            else:
                                popup_message = "This Boss is locked!"
                                popup_end_time = pygame.time.get_ticks() + 2000

        elif state == 'SELECT_SKILL':
            player = players[current_player_index]
            skill_buttons = []
            screen.blit(font.render("Select a Skill:", True, WHITE), (100, 50))
            start_y = 50 + FONT_SIZE + 20 
            for i, skill in enumerate(player.skills):
                # 顯示技能的實際傷害預估 (考慮 skill_bonus_percent)
                display_damage = player.base_attack + int(skill.damage * player.skill_mastery * (1 + player.skill_bonus_percent / 100.0))
                b = Button((100, start_y + i * 60, SCREEN_WIDTH - 200, 50), GREEN, LIGHT_GRAY, f'{i + 1}. {skill.name} (Est. Damage: {display_damage})', WHITE)
                skill_buttons.append(b)
                b.draw(screen)

            back_button = Button((50, SCREEN_HEIGHT - 60, 100, 40), GRAY, LIGHT_GRAY, 'Back', WHITE)
            back_button.draw(screen)

            if mouse_clicked and mouse_pos:
                if back_button.is_clicked(mouse_pos):
                    state = 'GAMEPLAY' 
                    selected_skill_index = None 
                else:
                    for i, b in enumerate(skill_buttons):
                        if b.is_clicked(mouse_pos):
                            selected_skill_index = i 
                            state = 'SELECT_MONSTER_FOR_SKILL_ATTACK' 
                            break
        
        elif state == 'SELECT_MONSTER_FOR_NORMAL_ATTACK': 
            monsters_to_display = [m for m in current_active_monsters if m.hp > 0] 
            
            if not monsters_to_display:
                popup_message = "All monsters defeated! Returning to operations menu."
                if current_boss_challenge: 
                    popup_message = f"{current_boss_challenge.name} defeated! Returning to operations menu."
                    current_boss_challenge = None 
                    current_boss_instance = None 

                popup_end_time = pygame.time.get_ticks() + 2000
                current_active_monsters.clear() 
                state = 'GAMEPLAY' 
                continue 

            # 顯示 Boss 資訊和血條 (如果在 SELECT_MONSTER 且是 Boss 戰)
            if current_boss_instance and current_boss_instance.hp > 0 and is_boss_monster(current_boss_instance.name):
                boss = current_boss_instance
                boss_info_text = f'{boss.name} (Lv.{boss.level})'
                boss_hp_text = f'HP: {boss.hp}/{boss.max_hp}'
                boss_attack_text = f'ATK: {boss.attack}'
                boss_element_text = f'Element: {boss.element.name.capitalize()}'
                boss_aura_text = f'Aura: {boss.element_aura.name.capitalize()}' if boss.element_aura else 'Aura: None'

                boss_info_rect = pygame.Rect(SCREEN_WIDTH - 300, 40, 250, 180)
                s = pygame.Surface((boss_info_rect.width, boss_info_rect.height), pygame.SRCALPHA)
                s.fill(BOSS_INFO_BG)
                screen.blit(s, boss_info_rect.topleft)
                pygame.draw.rect(screen, WHITE, boss_info_rect, 2, border_radius=10)

                screen.blit(font.render(boss_info_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 10))
                screen.blit(font.render(boss_hp_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 40))
                screen.blit(font.render(boss_attack_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 70))
                screen.blit(font.render(boss_element_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 100))
                screen.blit(font.render(boss_aura_text, True, YELLOW), (boss_info_rect.x + 10, boss_info_rect.y + 130))

                hp_bar_x = boss_info_rect.x + 10
                hp_bar_y = boss_info_rect.y + 160
                draw_health_bar(screen, hp_bar_x, hp_bar_y, boss_info_rect.width - 20, 15, boss.hp, boss.max_hp)

            monster_buttons = []
            screen.blit(font.render("Select a Monster for Normal Attack:", True, WHITE), (100, 50))

            start_y = 50 + FONT_SIZE + 20 
            for i, monster in enumerate(monsters_to_display):
                btn_color = RED 
                hover_btn_color = LIGHT_GRAY
                
                display_text = ""
                if is_boss_monster(monster.name): 
                    btn_color = BOSS_COLOR 
                    display_text = f'Boss: {monster.name} (Lv.{monster.level} HP:{monster.hp}/{monster.max_hp} ATK:{monster.attack})' 
                else:
                    slime_icon = element_slime_data.get(monster.name, {}).get("display_icon", "")
                    display_text = f'{slime_icon} {monster.name} (HP: {monster.hp}/{monster.max_hp})'
                
                if monster.element_aura:
                    display_text += f' [{monster.element_aura.name.capitalize()} Aura]'
                    
                b = Button((100, start_y + i * 60, SCREEN_WIDTH - 200, 50), btn_color, hover_btn_color, display_text, WHITE)
                monster_buttons.append(b)
                b.draw(screen)

            back_button = Button((50, SCREEN_HEIGHT - 60, 100, 40), GRAY, LIGHT_GRAY, 'Back', WHITE)
            back_button.draw(screen)

            if mouse_clicked and mouse_pos:
                if back_button.is_clicked(mouse_pos):
                    state = 'GAMEPLAY' 
                else:
                    for i, b in enumerate(monster_buttons):
                        if b.is_clicked(mouse_pos):
                            player = players[current_player_index]
                            target_monster = monsters_to_display[i] 

                            attack_result_message = attack_monster(
                                player, target_monster, 'NORMAL', None, current_active_monsters
                            )
                            
                            level_up_popup = gain_experience(player, 0) 

                            if level_up_popup:
                                popup_message = level_up_popup
                            elif attack_result_message:
                                popup_message = attack_result_message
                            else:
                                popup_message = None

                            popup_end_time = pygame.time.get_ticks() + 2000
                            
                            if player.hp <= 0:
                                popup_message = "You have been defeated! Game Over." 
                                popup_end_time = pygame.time.get_ticks() + 3000
                                running = False 
                                break 

                            if not any(m.hp > 0 for m in current_active_monsters):
                                current_active_monsters.clear() 
                                current_boss_challenge = None 
                                current_boss_instance = None
                                state = 'GAMEPLAY'
                            elif current_boss_challenge and target_monster.hp > 0:
                                pass 
                            else: 
                                state = 'SELECT_MONSTER_FOR_NORMAL_ATTACK' 
                                
                            break 

        elif state == 'SELECT_MONSTER_FOR_SKILL_ATTACK': 
            if selected_skill_index is None:
                popup_message = "Please select a skill first!"
                popup_end_time = pygame.time.get_ticks() + 2000
                state = 'SELECT_SKILL' 
                continue 

            monsters_to_display = [m for m in current_active_monsters if m.hp > 0] 
            
            if not monsters_to_display:
                popup_message = "All monsters defeated! Returning to operations menu."
                if current_boss_challenge: 
                    popup_message = f"{current_boss_challenge.name} defeated! Returning to operations menu."
                    current_boss_challenge = None 
                    current_boss_instance = None 

                popup_end_time = pygame.time.get_ticks() + 2000
                current_active_monsters.clear() 
                state = 'GAMEPLAY' 
                continue 

            # 顯示 Boss 資訊和血條 (如果在 SELECT_MONSTER 且是 Boss 戰)
            if current_boss_instance and current_boss_instance.hp > 0 and is_boss_monster(current_boss_instance.name):
                boss = current_boss_instance
                boss_info_text = f'{boss.name} (Lv.{boss.level})'
                boss_hp_text = f'HP: {boss.hp}/{boss.max_hp}'
                boss_attack_text = f'ATK: {boss.attack}'
                boss_element_text = f'Element: {boss.element.name.capitalize()}'
                boss_aura_text = f'Aura: {boss.element_aura.name.capitalize()}' if boss.element_aura else 'Aura: None'

                boss_info_rect = pygame.Rect(SCREEN_WIDTH - 300, 40, 250, 180)
                s = pygame.Surface((boss_info_rect.width, boss_info_rect.height), pygame.SRCALPHA)
                s.fill(BOSS_INFO_BG)
                screen.blit(s, boss_info_rect.topleft)
                pygame.draw.rect(screen, WHITE, boss_info_rect, 2, border_radius=10)

                screen.blit(font.render(boss_info_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 10))
                screen.blit(font.render(boss_hp_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 40))
                screen.blit(font.render(boss_attack_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 70))
                screen.blit(font.render(boss_element_text, True, WHITE), (boss_info_rect.x + 10, boss_info_rect.y + 100))
                screen.blit(font.render(boss_aura_text, True, YELLOW), (boss_info_rect.x + 10, boss_info_rect.y + 130))

                hp_bar_x = boss_info_rect.x + 10
                hp_bar_y = boss_info_rect.y + 160
                draw_health_bar(screen, hp_bar_x, hp_bar_y, boss_info_rect.width - 20, 15, boss.hp, boss.max_hp)

            monster_buttons = []
            screen.blit(font.render("Select a Monster for Skill Attack:", True, WHITE), (100, 50))

            start_y = 50 + FONT_SIZE + 20 
            for i, monster in enumerate(monsters_to_display):
                btn_color = RED 
                hover_btn_color = LIGHT_GRAY
                
                display_text = ""
                if is_boss_monster(monster.name): 
                    btn_color = BOSS_COLOR 
                    display_text = f'Boss: {monster.name} (Lv.{monster.level} HP:{monster.hp}/{monster.max_hp} ATK:{monster.attack})' 
                else:
                    slime_icon = element_slime_data.get(monster.name, {}).get("display_icon", "")
                    display_text = f'{slime_icon} {monster.name} (HP: {monster.hp}/{monster.max_hp})'
                
                if monster.element_aura:
                    display_text += f' [{monster.element_aura.name.capitalize()} Aura]'
                    
                b = Button((100, start_y + i * 60, SCREEN_WIDTH - 200, 50), btn_color, hover_btn_color, display_text, WHITE)
                monster_buttons.append(b)
                b.draw(screen)

            back_button = Button((50, SCREEN_HEIGHT - 60, 100, 40), GRAY, LIGHT_GRAY, 'Back', WHITE)
            back_button.draw(screen)

            if mouse_clicked and mouse_pos:
                if back_button.is_clicked(mouse_pos):
                    state = 'GAMEPLAY' 
                    selected_skill_index = None 
                else:
                    for i, b in enumerate(monster_buttons):
                        if b.is_clicked(mouse_pos):
                            player = players[current_player_index]
                            target_monster = monsters_to_display[i] 

                            skill_data = player.skills[selected_skill_index] 

                            attack_result_message = attack_monster(
                                player, target_monster, 'SKILL', skill_data, current_active_monsters
                            )
                            
                            level_up_popup = gain_experience(player, 0) 

                            if level_up_popup:
                                popup_message = level_up_popup
                            elif attack_result_message:
                                popup_message = attack_result_message
                            else:
                                popup_message = None

                            popup_end_time = pygame.time.get_ticks() + 2000
                            
                            if player.hp <= 0:
                                popup_message = "You have been defeated! Game Over." 
                                popup_end_time = pygame.time.get_ticks() + 3000
                                running = False 
                                break 

                            selected_skill_index = None 
                            
                            if not any(m.hp > 0 for m in current_active_monsters):
                                current_active_monsters.clear() 
                                current_boss_challenge = None 
                                current_boss_instance = None
                                state = 'GAMEPLAY'
                            elif current_boss_challenge and target_monster.hp > 0:
                                pass 
                            else: 
                                state = 'SELECT_MONSTER_FOR_SKILL_ATTACK' 

                            break 

        if popup_message and pygame.time.get_ticks() < popup_end_time:
            draw_popup(screen, popup_message, font)
        else:
            popup_message = None 

        pygame.display.flip()
        clock.tick(60)

    save_players_data(players)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main_pygame_loop()