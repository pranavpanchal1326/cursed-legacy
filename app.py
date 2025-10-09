from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import json
import os
from datetime import datetime
import secrets
import random
import sqlite3
from dotenv import load_dotenv
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API - NOW READS FROM .ENV FILE
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Add error handling
if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY not found!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
# ========== DATABASE SETUP ==========
def init_db():
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    
    # Player progression table
    c.execute('''CREATE TABLE IF NOT EXISTS player_progress
                 (id INTEGER PRIMARY KEY,
                  total_kills INTEGER DEFAULT 0,
                  total_runs INTEGER DEFAULT 0,
                  best_turn INTEGER DEFAULT 0,
                  unlocked_classes TEXT DEFAULT '[]',
                  unlocked_stories TEXT DEFAULT '[]',
                  achievements TEXT DEFAULT '[]',
                  total_playtime INTEGER DEFAULT 0)''')
    
    # Saved games table
    c.execute('''CREATE TABLE IF NOT EXISTS saved_games
                 (session_id TEXT PRIMARY KEY,
                  save_data TEXT,
                  save_date TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# Game state storage
games = {}

# ========== EXPANDED GAME CONFIG ==========
MAX_TURNS = 30  # Tripled!
WORDS_PER_TURN = (80, 120)  # Much more immersive

GENRE_CONTEXTS = {
    'Cursed King': {
        'theme': 'Immense cursed power like Sukuna from JJK. Domain expansion, malevolent shrine, overwhelming presence.',
        'combat_style': 'Cleave and Dismantle techniques, cursed energy manipulation',
        'special_abilities': ['Domain Expansion: Malevolent Shrine', 'Cleave', 'Dismantle', 'Fire Arrow'],
        'weakness': 'holy',
        'strength': 'dark'
    },
    'Demon Blood': {
        'theme': 'Demon transformation like Demon Slayer. Blood demon art, regeneration, slayer corps hunting.',
        'combat_style': 'Blood arts, regeneration, enhanced physical abilities',
        'special_abilities': ['Blood Demon Art', 'Ultra Regeneration', 'Blood Explosion', 'Moon Breathing'],
        'weakness': 'sunlight',
        'strength': 'darkness'
    },
    'Special Grade': {
        'theme': 'Special grade cursed spirit. Cursed techniques, domain expansion, overwhelming power.',
        'combat_style': 'Cursed technique mastery, domain expansion',
        'special_abilities': ['Domain Expansion', 'Cursed Speech', 'Limitless', 'Six Eyes'],
        'weakness': 'exorcism',
        'strength': 'cursed_energy'
    },
    'Rogue Shinobi': {
        'theme': 'Rogue ninja with forbidden jutsu. Tailed beasts, shinobi world conflict.',
        'combat_style': 'Ninjutsu, forbidden techniques, tailed beast power',
        'special_abilities': ['Rasengan', 'Shadow Clone Jutsu', 'Tailed Beast Mode', 'Sage Mode'],
        'weakness': 'chakra_seal',
        'strength': 'ninja_arts'
    },
    'Vampire King': {
        'theme': 'Immortal vampire with blood magic. Daywalker potential, vampire hunters.',
        'combat_style': 'Blood magic, immortality, enhanced speed',
        'special_abilities': ['Blood Manipulation', 'Immortality', 'Hypnosis', 'Bat Swarm'],
        'weakness': 'sunlight',
        'strength': 'blood'
    },
    'One-Eyed Ghoul': {
        'theme': 'Half-human, half-ghoul like Tokyo Ghoul. Kagune powers, kakuja transformation.',
        'combat_style': 'Kagune manifestation, regeneration',
        'special_abilities': ['Kagune Release', 'Kakuja Form', 'RC Cell Burst', 'Ghoul Eyes'],
        'weakness': 'quinque',
        'strength': 'rc_cells'
    },
    'Chainsaw Devil': {
        'theme': 'Devil contract holder. Violence incarnate, devil hunters.',
        'combat_style': 'Chainsaw attacks, devil contracts, brutal violence',
        'special_abilities': ['Chainsaw Transformation', 'Devil Contract', 'Blood Chainsaw', 'Consume'],
        'weakness': 'fear',
        'strength': 'violence'
    },
    'Hollow King': {
        'theme': 'Hollow evolution like Bleach Espada. Cero, arrancar transformation.',
        'combat_style': 'Cero attacks, hierro defense, sonido speed',
        'special_abilities': ['Cero Oscuras', 'Resurrection', 'Hierro', 'Sonido'],
        'weakness': 'spiritual',
        'strength': 'hollow_power'
    },
    'Nen Master': {
        'theme': 'Nen user like Hunter x Hunter. Hatsu abilities, restrictions.',
        'combat_style': 'Nen manipulation, enhancement, emission',
        'special_abilities': ['Hatsu Ability', 'Zetsu', 'En', 'Post-Mortem Nen'],
        'weakness': 'nen_restriction',
        'strength': 'aura'
    },
    'Black Swordsman': {
        'theme': 'Cursed warrior like Berserk. Apostles, brand of sacrifice.',
        'combat_style': 'Dragonslayer combat, berserker armor',
        'special_abilities': ['Berserker Rage', 'Dragon Slayer', 'Beast of Darkness', 'Iron Cleave'],
        'weakness': 'apostle_curse',
        'strength': 'physical'
    }
}

# ========== EQUIPMENT SYSTEM ==========
EQUIPMENT = {
    'weapons': {
        'Cursed Blade': {'damage': 15, 'type': 'dark', 'special': 'Lifesteal 10%'},
        'Dragon Slayer': {'damage': 25, 'type': 'physical', 'special': 'Cleave enemies'},
        'Blood Scythe': {'damage': 20, 'type': 'blood', 'special': 'Heal on kill'},
        'Chakra Blade': {'damage': 18, 'type': 'ninja_arts', 'special': 'Chakra regen'},
        'Holy Sword': {'damage': 22, 'type': 'holy', 'special': 'Bonus vs dark'},
        'Quinque': {'damage': 20, 'type': 'quinque', 'special': 'Bonus vs ghouls'},
    },
    'armor': {
        'Berserker Armor': {'defense': 20, 'special': 'Prevent lethal damage once'},
        'Blood Cloak': {'defense': 15, 'special': '+15% regeneration'},
        'Hollow Mask': {'defense': 18, 'special': '+20% hollow power'},
        'Shinobi Vest': {'defense': 12, 'special': '+30% dodge chance'},
        'Cursed Shroud': {'defense': 25, 'special': 'Immune to curse'},
    },
    'accessories': {
        'Ring of Power': {'special': '+25% damage'},
        'Amulet of Life': {'special': '+50 max HP'},
        'Speed Boots': {'special': 'Always attack first'},
        'Lucky Charm': {'special': '+20% crit chance'},
    }
}

# ========== ENEMY TYPES WITH WEAKNESSES ==========
ENEMY_TYPES = {
    'Shadow Beast': {'hp': 80, 'damage': 15, 'weakness': 'holy', 'resistance': 'dark'},
    'Holy Crusader': {'hp': 100, 'damage': 20, 'weakness': 'dark', 'resistance': 'holy'},
    'Demon Hunter': {'hp': 90, 'damage': 18, 'weakness': 'blood', 'resistance': 'sunlight'},
    'Cursed Spirit': {'hp': 85, 'damage': 16, 'weakness': 'exorcism', 'resistance': 'cursed_energy'},
    'Apostle': {'hp': 120, 'damage': 25, 'weakness': 'physical', 'resistance': 'apostle_curse'},
    'CCG Investigator': {'hp': 95, 'damage': 22, 'weakness': 'rc_cells', 'resistance': 'quinque'},
    'Soul Reaper': {'hp': 110, 'damage': 23, 'weakness': 'hollow_power', 'resistance': 'spiritual'},
    'Ninja Squad': {'hp': 75, 'damage': 14, 'weakness': 'chakra_seal', 'resistance': 'ninja_arts'},
}

# ========== ACHIEVEMENTS ==========
ACHIEVEMENTS = {
    'first_blood': {'name': 'First Blood', 'desc': 'Kill your first enemy', 'icon': '⚔️'},
    'mass_murderer': {'name': 'Mass Murderer', 'desc': 'Kill 10 enemies', 'icon': '💀'},
    'genocide': {'name': 'Genocide', 'desc': 'Kill 25 enemies', 'icon': '☠️'},
    'pure_evil': {'name': 'Pure Evil', 'desc': 'Reach 0 morality', 'icon': '😈'},
    'saint': {'name': 'Saint', 'desc': 'Reach 100 morality', 'icon': '😇'},
    'survivor': {'name': 'Survivor', 'desc': 'Reach turn 15', 'icon': '🛡️'},
    'legend': {'name': 'Legend', 'desc': 'Reach turn 25', 'icon': '👑'},
    'power_hungry': {'name': 'Power Hungry', 'desc': 'Reach God Threat power level', 'icon': '⚡'},
    'fully_equipped': {'name': 'Fully Equipped', 'desc': 'Have weapon, armor, and accessory', 'icon': '🎖️'},
    'plot_twist': {'name': 'Plot Twist', 'desc': 'Experience a mid-game twist', 'icon': '🌀'},
}

# ========== ENHANCED GAME STATE ==========
class GameState:
    def __init__(self, genre, setting, character_name, character_class):
        self.genre = genre
        self.setting = setting
        self.character_name = character_name
        self.character_class = character_class
        self.story_history = []
        self.choices_made = []
        self.health = 200  # Increased
        self.max_health = 200
        self.inventory = []
        self.equipment = {'weapon': None, 'armor': None, 'accessory': None}
        
        # Enhanced stats
        class_stats = {
            'warrior': {'strength': 18, 'intelligence': 8, 'charisma': 10, 'luck': 10, 'defense': 15},
            'mage': {'strength': 8, 'intelligence': 20, 'charisma': 12, 'luck': 10, 'defense': 8},
            'rogue': {'strength': 12, 'intelligence': 10, 'charisma': 8, 'luck': 18, 'defense': 10},
            'healer': {'strength': 8, 'intelligence': 15, 'charisma': 18, 'luck': 12, 'defense': 12}
        }
        
        self.stats = class_stats.get(character_class, {
            'strength': 10, 'intelligence': 10, 'charisma': 10, 'luck': 10, 'defense': 10
        })
        
        self.turn_count = 1
        self.created_at = datetime.now().isoformat()
        self.morality = 50
        self.kill_count = 0
        self.achievements = []
        self.plot_twists_seen = []
        self.special_abilities_unlocked = []
        
    def to_dict(self):
        return {
            'genre': self.genre,
            'setting': self.setting,
            'character_name': self.character_name,
            'character_class': self.character_class,
            'story_history': self.story_history,
            'choices_made': self.choices_made,
            'health': self.health,
            'max_health': self.max_health,
            'inventory': self.inventory,
            'equipment': self.equipment,
            'stats': self.stats,
            'turn_count': self.turn_count,
            'morality': self.morality,
            'kill_count': self.kill_count,
            'achievements': self.achievements,
            'plot_twists_seen': self.plot_twists_seen,
            'special_abilities_unlocked': self.special_abilities_unlocked
        }

# ========== AI STORY GENERATION (ENHANCED) ==========
def generate_story_with_ai(character_name, genre, setting, turn_count, choices_made, current_morality, kill_count, character_class, equipment):
    """Generate LONGER, more immersive story"""
    
    context = GENRE_CONTEXTS.get(genre, GENRE_CONTEXTS['Cursed King'])
    
    # Morality analysis
    if current_morality <= 20:
        moral_state = "consumed by darkness, ruthless killer, feared by all"
    elif current_morality <= 40:
        moral_state = "walking dark path, cruel and merciless"
    elif current_morality <= 60:
        moral_state = "morally gray, pragmatic survivor"
    elif current_morality <= 80:
        moral_state = "trying to do good despite dark power"
    else:
        moral_state = "beacon of hope, hero fighting inner darkness"
    
    # Power progression (10 tiers across 30 turns)
    power_tiers = [
        "weak mortal trembling with newfound power",
        "awakening cursed abilities, barely controlled",
        "dangerous threat, locals flee in terror",
        "formidable warrior, bounty on head",
        "special grade threat, armies mobilize",
        "legendary entity, nations take notice",
        "calamity-class being, reality bends around you",
        "world-ending force, gods themselves worry",
        "transcendent power, reshaping existence",
        "absolute dominion, beyond mortal comprehension"
    ]
    power_index = min(turn_count // 3, 9)
    power_state = power_tiers[power_index]
    
    # Story phase with PLOT TWISTS
    if turn_count == 1:
        phase = "awakening"
        instruction = "Describe their cursed power awakening in vivid detail. Show the moment everything changes. People's reactions. The weight of newfound power. Make it atmospheric and gripping. 80-120 words."
    elif turn_count <= 5:
        phase = "discovery"
        instruction = f"Show them learning their abilities. {kill_count} enemies defeated. Power growing. But at what cost? Explore consequences. Describe the setting vividly. 80-120 words."
    elif turn_count == 10:
        phase = "PLOT TWIST"
        instruction = f"MAJOR PLOT TWIST! Reveal something shocking: a betrayal, hidden truth about their power, or unexpected ally/enemy. Change everything. Make it dramatic! {moral_state}. 80-120 words."
    elif turn_count <= 15:
        phase = "escalation"
        instruction = f"Stakes rise dramatically. Their {power_state} reputation spreads. Powerful factions take interest. Personal relationships affected. Show the burden of power. 80-120 words."
    elif turn_count == 20:
        phase = "SECOND TWIST"
        instruction = f"ANOTHER TWIST! Their past catches up, or future revealed, or ultimate enemy appears. Make it intense! {moral_state} path consequences shown. 80-120 words."
    elif turn_count <= 28:
        phase = "climax_building"
        instruction = f"Final confrontation approaching. {kill_count} lives taken weigh heavily. {moral_state}. Everything builds to this. Describe the tension, the power, the cost. 80-120 words."
    else:
        phase = "final_battle"
        instruction = f"EPIC FINALE! Ultimate enemy revealed. All choices matter now. {power_state} unleashed. Fate of everything at stake. Make it LEGENDARY! 100-120 words."
    
    # Equipment mentions
    equip_text = ""
    if equipment['weapon']:
        equip_text += f"Wielding {equipment['weapon']}. "
    
    prompt = f"""
Write an immersive dark fantasy story segment.

CHARACTER: {character_name} (class: {character_class})
GENRE: {genre} - {context['theme']}
SETTING: {setting}
TURN: {turn_count}/{MAX_TURNS}
PHASE: {phase}
POWER STATE: {power_state}
MORALITY: {current_morality}/100 - {moral_state}
KILLS: {kill_count}
{equip_text}

CRITICAL INSTRUCTION: {instruction}

STYLE REQUIREMENTS:
- Write EXACTLY 80-120 words (this is CRITICAL!)
- Use {character_name}'s name at least twice
- Create vivid, sensory descriptions (sights, sounds, feelings)
- Show don't tell - make it cinematic
- Include dialogue if appropriate
- Build tension and atmosphere
- Match the {context['theme']} tone perfectly
- Reference their {moral_state} nature
- Make it feel EPIC and immersive

Write the story NOW:"""

    try:
        response = model.generate_content(prompt)
        story = response.text.strip()
        
        # Ensure word count
        words = story.split()
        if len(words) < 80:
            # Too short, request regeneration
            story += " The power within surged, demanding more."
        elif len(words) > 120:
            story = ' '.join(words[:120]) + '...'
        
        return story
    except Exception as e:
        print(f"AI Error: {e}")
        return f"{character_name} feels the cursed power surging through every fiber of being. The air crackles with dark energy. Choices made have led to this moment. There is no turning back now. The path of {moral_state} continues forward into darkness and destiny."

# ========== ENHANCED CHOICE GENERATION ==========
def generate_choices_with_ai(story, character_name, genre, current_morality, turn_count, kill_count, special_abilities):
    """Generate meaningful choices with clear consequences"""
    
    context = GENRE_CONTEXTS.get(genre, GENRE_CONTEXTS['Cursed King'])
    
    if current_morality <= 30:
        alignment = "villainous, ruthless"
    elif current_morality >= 70:
        alignment = "heroic, compassionate"
    else:
        alignment = "morally gray, pragmatic"
    
    prompt = f"""
Based on this story: "{story}"

CHARACTER: {character_name} (currently {alignment})
GENRE: {context['theme']}
TURN: {turn_count}/{MAX_TURNS}
KILLS: {kill_count}
ABILITIES: {special_abilities[:2] if special_abilities else 'None yet'}

Generate EXACTLY 3 choices with CLEAR consequences:

CHOICE 1 (AGGRESSIVE/EVIL):
- Would decrease morality by 15-20 points
- Violent, selfish, or power-hungry
- High risk, high reward
- 6-8 words maximum
- Starts with strong action verb

CHOICE 2 (TACTICAL/NEUTRAL):
- No morality change
- Strategic, calculated approach
- Balanced risk/reward
- 6-8 words maximum
- Shows intelligence

CHOICE 3 (COMPASSIONATE/GOOD):
- Would increase morality by 10-15 points
- Selfless, protective, merciful
- Lower immediate gain, long-term benefit
- 6-8 words maximum
- Shows heroism

{"SPECIAL: Turn " + str(turn_count) + " - Include path-defining choices" if turn_count in [10, 20] else ""}

Format: Return ONLY 3 choices, one per line, no labels."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        choices = []
        
        for line in lines:
            clean = line.lstrip('123456789.-•*> ')
            clean = clean.replace('**', '')
            if clean and len(clean.split()) <= 10:
                choices.append(clean)
        
        if len(choices) < 3:
            fallback = [
                "Unleash full power, destroy everything",
                "Assess situation, plan carefully",
                "Protect innocents, show mercy"
            ]
            choices.extend(fallback[len(choices):3])
        
        return choices[:3]
        
    except Exception as e:
        print(f"AI Choices Error: {e}")
        return [
            "Attack with overwhelming force",
            "Use strategy and tactics",
            "Prioritize saving lives"
        ]

# ========== ADVANCED COMBAT SYSTEM ==========
def generate_combat_enemy(character_name, genre, turn_count, kill_count, morality):
    """Generate enemy with weaknesses and resistances"""
    
    # Select appropriate enemy
    if turn_count <= 10:
        enemy_pool = ['Shadow Beast', 'Demon Hunter', 'Ninja Squad']
    elif turn_count <= 20:
        enemy_pool = ['Holy Crusader', 'Cursed Spirit', 'CCG Investigator']
    else:
        enemy_pool = ['Apostle', 'Soul Reaper']
    
    enemy_name = random.choice(enemy_pool)
    enemy_data = ENEMY_TYPES[enemy_name].copy()
    
    # Scale with turn count
    scale = 1 + (turn_count / MAX_TURNS)
    enemy_data['hp'] = int(enemy_data['hp'] * scale)
    enemy_data['damage'] = int(enemy_data['damage'] * scale)
    
    # Add emoji
    emojis = {'Shadow Beast': '👹', 'Holy Crusader': '⚔️', 'Demon Hunter': '🗡️', 
              'Cursed Spirit': '👻', 'Apostle': '😈', 'CCG Investigator': '🔫',
              'Soul Reaper': '💀', 'Ninja Squad': '🥷'}
    enemy_data['emoji'] = emojis.get(enemy_name, '⚔️')
    enemy_data['name'] = enemy_name
    
    return enemy_data

def calculate_combat_damage(player_stats, player_equipment, enemy_data, action, genre):
    """Calculate damage considering weaknesses and equipment"""
    
    context = GENRE_CONTEXTS.get(genre, GENRE_CONTEXTS['Cursed King'])
    base_damage = player_stats['strength'] * 2
    
    # Equipment bonus
    if player_equipment['weapon']:
        weapon = player_equipment['weapon']
        weapon_data = next((w for w in EQUIPMENT['weapons'].values() if weapon in str(w)), None)
        if weapon_data:
            base_damage += weapon_data['damage']
            
            # Type advantage
            if weapon_data['type'] == enemy_data['weakness']:
                base_damage *= 1.5  # 50% bonus against weakness
            elif weapon_data['type'] == enemy_data['resistance']:
                base_damage *= 0.7  # 30% penalty
    
    # Action modifiers
    if action == 'attack':
        damage = base_damage * random.uniform(0.8, 1.2)
    elif action == 'skill':
        # Special abilities do more damage
        damage = base_damage * random.uniform(1.2, 1.8)
    elif action == 'defend':
        damage = 0
    else:
        damage = 0
    
    # Crit chance
    crit_chance = player_stats.get('luck', 10) / 100
    if random.random() < crit_chance:
        damage *= 2
        return int(damage), True
    
    return int(damage), False

# ========== EQUIPMENT DROP SYSTEM ==========
def generate_item_drop(genre, character_class, turn_count):
    """Generate equipment drop based on progression"""
    
    drop_chance = 0.3 + (turn_count / MAX_TURNS * 0.2)  # Increases with turns
    
    if random.random() > drop_chance:
        return None
    
    # What type to drop
    roll = random.random()
    if roll < 0.5:
        category = 'weapons'
    elif roll < 0.8:
        category = 'armor'
    else:
        category = 'accessories'
    
    item_name = random.choice(list(EQUIPMENT[category].keys()))
    return {'name': item_name, 'category': category, 'data': EQUIPMENT[category][item_name]}

# ========== ACHIEVEMENT SYSTEM ==========
def check_achievements(game_state):
    """Check and unlock achievements"""
    new_achievements = []
    
    if game_state.kill_count >= 1 and 'first_blood' not in game_state.achievements:
        new_achievements.append('first_blood')
    
    if game_state.kill_count >= 10 and 'mass_murderer' not in game_state.achievements:
        new_achievements.append('mass_murderer')
    
    if game_state.kill_count >= 25 and 'genocide' not in game_state.achievements:
        new_achievements.append('genocide')
    
    if game_state.morality <= 0 and 'pure_evil' not in game_state.achievements:
        new_achievements.append('pure_evil')
    
    if game_state.morality >= 100 and 'saint' not in game_state.achievements:
        new_achievements.append('saint')
    
    if game_state.turn_count >= 15 and 'survivor' not in game_state.achievements:
        new_achievements.append('survivor')
    
    if game_state.turn_count >= 25 and 'legend' not in game_state.achievements:
        new_achievements.append('legend')
    
    if game_state.turn_count >= 27 and 'power_hungry' not in game_state.achievements:
        new_achievements.append('power_hungry')
    
    if (game_state.equipment['weapon'] and game_state.equipment['armor'] and 
        game_state.equipment['accessory'] and 'fully_equipped' not in game_state.achievements):
        new_achievements.append('fully_equipped')
    
    if game_state.turn_count in [10, 20] and 'plot_twist' not in game_state.achievements:
        new_achievements.append('plot_twist')
    
    game_state.achievements.extend(new_achievements)
    return new_achievements

# ========== SAVE/LOAD SYSTEM ==========
def save_game(session_id, game_state):
    """Save game to database"""
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    
    save_data = json.dumps(game_state.to_dict())
    save_date = datetime.now().isoformat()
    
    c.execute("INSERT OR REPLACE INTO saved_games VALUES (?, ?, ?)",
              (session_id, save_data, save_date))
    
    conn.commit()
    conn.close()

def load_game(session_id):
    """Load game from database"""
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    
    c.execute("SELECT save_data FROM saved_games WHERE session_id = ?", (session_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def update_player_progress(kills, turns, achievements):
    """Update persistent player progression"""
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    
    # Get or create player
    c.execute("SELECT * FROM player_progress WHERE id = 1")
    player = c.fetchone()
    
    if player:
        total_kills = player[1] + kills
        total_runs = player[2] + 1
        best_turn = max(player[3], turns)
        
        c.execute("""UPDATE player_progress 
                     SET total_kills = ?, total_runs = ?, best_turn = ?
                     WHERE id = 1""",
                  (total_kills, total_runs, best_turn))
    else:
        c.execute("""INSERT INTO player_progress 
                     (id, total_kills, total_runs, best_turn)
                     VALUES (1, ?, 1, ?)""", (kills, turns))
    
    conn.commit()
    conn.close()

# ========== API ROUTES ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/api/start-game', methods=['POST'])
def start_game():
    data = request.json
    session_id = secrets.token_hex(8)
    
    game_state = GameState(
        data['genre'],
        data['setting'],
        data['characterName'],
        data.get('characterClass', 'warrior')
    )
    
    # 🔥 AI GENERATES IMMERSIVE OPENING!
    story_text = generate_story_with_ai(
        character_name=game_state.character_name,
        genre=game_state.genre,
        setting=game_state.setting,
        turn_count=1,
        choices_made=[],
        current_morality=50,
        kill_count=0,
        character_class=game_state.character_class,
        equipment=game_state.equipment
    )
    
    choices = generate_choices_with_ai(
        story=story_text,
        character_name=game_state.character_name,
        genre=game_state.genre,
        current_morality=50,
        turn_count=1,
        kill_count=0,
        special_abilities=[]
    )
    
    game_state.story_history.append(story_text)
    games[session_id] = game_state
    
    power_levels = ["Weak Human", "Awakened", "Threat: Wolf", "Threat: Tiger", "Threat: Demon", 
                   "Special Grade", "Calamity Class", "World Ender", "God Threat", "ABSOLUTE POWER"]
    
    return jsonify({
        'success': True,
        'sessionId': session_id,
        'story': {
            'story': story_text,
            'choices': choices
        },
        'gameState': {
            'health': game_state.health,
            'maxHealth': game_state.max_health,
            'inventory': game_state.inventory,
            'equipment': game_state.equipment,
            'stats': game_state.stats,
            'turnCount': game_state.turn_count,
            'maxTurns': MAX_TURNS,
            'characterClass': game_state.character_class,
            'morality': game_state.morality,
            'killCount': game_state.kill_count,
            'powerLevel': power_levels[0],
            'achievements': game_state.achievements,
            'specialAbilities': game_state.special_abilities_unlocked
        }
    })

@app.route('/api/make-choice', methods=['POST'])
def make_choice():
    data = request.json
    session_id = data['sessionId']
    choice_num = data['choice']
    
    if session_id not in games:
        return jsonify({'success': False, 'error': 'Game session not found'})
    
    game_state = games[session_id]
    game_state.turn_count += 1
    
    # Update morality with bigger impact
    morality_changes = [-18, 0, +12]
    game_state.morality = max(0, min(100, game_state.morality + morality_changes[choice_num - 1]))
    
    choice_types = ['aggressive', 'tactical', 'compassionate']
    game_state.choices_made.append(choice_types[choice_num - 1])
    
    # Unlock abilities at milestones
    if game_state.turn_count in [5, 10, 15, 20, 25]:
        context = GENRE_CONTEXTS.get(game_state.genre, GENRE_CONTEXTS['Cursed King'])
        ability = context['special_abilities'][len(game_state.special_abilities_unlocked)]
        game_state.special_abilities_unlocked.append(ability)
    
    # 🔥 AI GENERATES NEXT IMMERSIVE STORY!
    story_text = generate_story_with_ai(
        character_name=game_state.character_name,
        genre=game_state.genre,
        setting=game_state.setting,
        turn_count=game_state.turn_count,
        choices_made=game_state.choices_made,
        current_morality=game_state.morality,
        kill_count=game_state.kill_count,
        character_class=game_state.character_class,
        equipment=game_state.equipment
    )
    
    choices = generate_choices_with_ai(
        story=story_text,
        character_name=game_state.character_name,
        genre=game_state.genre,
        current_morality=game_state.morality,
        turn_count=game_state.turn_count,
        kill_count=game_state.kill_count,
        special_abilities=game_state.special_abilities_unlocked
    )
    
    # Enhanced health system
    stat_used = ['strength', 'intelligence', 'charisma'][choice_num - 1]
    stat_value = game_state.stats.get(stat_used, 10)
    
    # Equipment defense bonus
    defense_bonus = 0
    if game_state.equipment['armor']:
        defense_bonus = 10
    
    if stat_value >= 18:
        health_change = random.randint(5, 15)
    elif stat_value >= 15:
        health_change = random.randint(-5, 10)
    elif stat_value >= 12:
        health_change = random.randint(-15, 5)
    else:
        health_change = random.randint(-25, 0)
    
    health_change += defense_bonus
    game_state.health = max(50, min(game_state.max_health, game_state.health + health_change))
    
    # 🎁 EQUIPMENT DROPS!
    item_dropped = generate_item_drop(game_state.genre, game_state.character_class, game_state.turn_count)
    new_item = None
    
    if item_dropped:
        new_item = item_dropped['name']
        game_state.inventory.append(new_item)
    
    # ⚔️ ENHANCED COMBAT!
    combat_data = None
    if choice_num == 1 and random.random() < 0.4:  # Higher combat chance
        combat_data = generate_combat_enemy(
            character_name=game_state.character_name,
            genre=game_state.genre,
            turn_count=game_state.turn_count,
            kill_count=game_state.kill_count,
            morality=game_state.morality
        )
        game_state.kill_count += 1
    
    # 🏆 CHECK ACHIEVEMENTS!
    new_achievements = check_achievements(game_state)
    
    game_state.story_history.append(story_text)
    
    # Auto-save every 5 turns
    if game_state.turn_count % 5 == 0:
        save_game(session_id, game_state)
    
    power_levels = ["Weak Human", "Awakened", "Threat: Wolf", "Threat: Tiger", "Threat: Demon", 
                   "Special Grade", "Calamity Class", "World Ender", "God Threat", "ABSOLUTE POWER"]
    power_index = min((game_state.turn_count - 1) // 3, 9)
    
    return jsonify({
        'success': True,
        'story': {
            'story': story_text,
            'choices': choices if game_state.turn_count < MAX_TURNS else [],
            'newItem': new_item,
            'newAbility': game_state.special_abilities_unlocked[-1] if len(game_state.special_abilities_unlocked) > 0 and game_state.turn_count in [5,10,15,20,25] else None
        },
        'gameState': {
            'health': game_state.health,
            'maxHealth': game_state.max_health,
            'inventory': game_state.inventory,
            'equipment': game_state.equipment,
            'stats': game_state.stats,
            'turnCount': game_state.turn_count,
            'maxTurns': MAX_TURNS,
            'characterClass': game_state.character_class,
            'morality': game_state.morality,
            'killCount': game_state.kill_count,
            'powerLevel': power_levels[power_index],
            'achievements': game_state.achievements,
            'specialAbilities': game_state.special_abilities_unlocked
        },
        'combat': combat_data,
        'newAchievements': [ACHIEVEMENTS[a] for a in new_achievements]
    })

# Continue in next message...
# ========== EQUIPMENT MANAGEMENT ==========
@app.route('/api/equip-item', methods=['POST'])
def equip_item():
    data = request.json
    session_id = data['sessionId']
    item_name = data['itemName']
    
    if session_id not in games:
        return jsonify({'success': False, 'error': 'Game session not found'})
    
    game_state = games[session_id]
    
    # Find item category
    for category, items in EQUIPMENT.items():
        if item_name in items:
            # Unequip old item
            old_item = game_state.equipment.get(category.rstrip('s'))
            if old_item:
                game_state.inventory.append(old_item)
            
            # Equip new item
            game_state.equipment[category.rstrip('s')] = item_name
            game_state.inventory.remove(item_name)
            
            return jsonify({
                'success': True,
                'equipment': game_state.equipment,
                'inventory': game_state.inventory
            })
    
    return jsonify({'success': False, 'error': 'Item not found'})

# ========== END GAME ==========
@app.route('/api/end-game', methods=['POST'])
def end_game():
    data = request.json
    session_id = data['sessionId']
    ending_type = data.get('endingType', 'heroic')
    
    if session_id not in games:
        return jsonify({'success': False, 'error': 'Game session not found'})
    
    game_state = games[session_id]
    
    # Determine ending based on morality and choices
    if game_state.morality <= 20:
        moral_result = "DEMON LORD ENDING - consumed by darkness, ruled through terror"
        ending_tone = "dark and tragic"
    elif game_state.morality <= 40:
        moral_result = "VILLAIN ENDING - power corrupted completely"
        ending_tone = "dark but triumphant"
    elif game_state.morality <= 60:
        moral_result = "NEUTRAL ENDING - walked alone, neither hero nor villain"
        ending_tone = "bittersweet and mysterious"
    elif game_state.morality <= 80:
        moral_result = "HEROIC ENDING - struggled against darkness, chose light"
        ending_tone = "hopeful with sacrifice"
    else:
        moral_result = "TRUE HERO ENDING - redeemed through compassion"
        ending_tone = "triumphant and inspiring"
    
    # Generate epic ending
    ending_prompt = f"""
Write an EPIC 150-word finale for {game_state.character_name}'s story.

CONTEXT:
- Genre: {game_state.genre}
- Morality: {game_state.morality}/100 - {moral_result}
- Total Kills: {game_state.kill_count}
- Turns Survived: {game_state.turn_count}/{MAX_TURNS}
- Equipment: {game_state.equipment}
- Abilities: {game_state.special_abilities_unlocked}
- Path: {game_state.choices_made[-5:] if game_state.choices_made else 'varied'}

Write a {ending_tone} ending that:
- Shows their final fate
- Reflects all choices made
- References specific kills and consequences
- Mentions their legendary status
- Makes it MEMORABLE and EPIC
- 150 words exactly

Make readers FEEL the weight of their journey!"""

    try:
        response = model.generate_content(ending_prompt)
        ending_text = response.text.strip()
    except:
        ending_text = f"{game_state.character_name}'s legend ends here. {moral_result}. Their power echoes through eternity. {game_state.kill_count} souls fell to their might. The world will remember."
    
    power_levels = ["Weak Human", "Awakened", "Threat: Wolf", "Threat: Tiger", "Threat: Demon", 
                   "Special Grade", "Calamity Class", "World Ender", "God Threat", "ABSOLUTE POWER"]
    final_power_index = min((game_state.turn_count - 1) // 3, 9)
    
    return jsonify({
        'success': True,
        'ending': ending_text,
        'finalStats': {
            'health': game_state.health,
            'inventory': game_state.inventory,
            'equipment': game_state.equipment,
            'turns': game_state.turn_count,
            'maxTurns': MAX_TURNS,
            'killCount': game_state.kill_count,
            'morality': game_state.morality,
            'finalPower': power_levels[final_power_index],
            'achievements': [ACHIEVEMENTS[a] for a in game_state.achievements],
            'specialAbilities': game_state.special_abilities_unlocked
        }
    })

@app.route('/api/combat-victory', methods=['POST'])
def combat_victory():
    data = request.json
    session_id = data['sessionId']
    
    if session_id not in games:
        return jsonify({'success': False})
    
    game_state = games[session_id]
    game_state.kill_count += 1
    game_state.morality = max(0, game_state.morality - 12)
    
    return jsonify({
        'success': True,
        'killCount': game_state.kill_count,
        'morality': game_state.morality
    })
# ========== ANALYTICS PAGE ==========
@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)



