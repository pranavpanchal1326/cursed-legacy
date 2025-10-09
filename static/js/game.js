// ============================================
// CURSED LEGACY - ENHANCED GAME LOGIC
// ============================================

let sessionId = null;
let currentGameState = null;
let isProcessing = false;
let maxTurns = 30;

const POWER_LEVELS = [
    'Weak Human', 'Awakened', 'Threat: Wolf',
    'Threat: Tiger', 'Threat: Demon',
    'Special Grade', 'Calamity Class', 'World Ender',
    'God Threat', 'ABSOLUTE POWER'
];

// Enemy type data for client-side reference
const ENEMY_TYPES = {
    'Shadow Beast': {hp: 80, damage: 15, weakness: 'holy', resistance: 'dark'},
    'Holy Crusader': {hp: 100, damage: 20, weakness: 'dark', resistance: 'holy'},
    'Demon Hunter': {hp: 90, damage: 18, weakness: 'blood', resistance: 'sunlight'},
    'Cursed Spirit': {hp: 85, damage: 16, weakness: 'exorcism', resistance: 'cursed_energy'},
    'Apostle': {hp: 120, damage: 25, weakness: 'physical', resistance: 'apostle_curse'},
    'CCG Investigator': {hp: 95, damage: 22, weakness: 'rc_cells', resistance: 'quinque'},
    'Soul Reaper': {hp: 110, damage: 23, weakness: 'hollow_power', resistance: 'spiritual'},
    'Ninja Squad': {hp: 75, damage: 14, weakness: 'chakra_seal', resistance: 'ninja_arts'}
};

// ========== INITIALIZE GAME ==========
document.addEventListener('DOMContentLoaded', function() {
    loadGameData();
    setupEventListeners();
});

function loadGameData() {
    sessionId = sessionStorage.getItem('gameSessionId');
    const characterName = sessionStorage.getItem('characterName');
    const storyData = JSON.parse(sessionStorage.getItem('currentStory'));
    const gameState = JSON.parse(sessionStorage.getItem('gameState'));

    if (!sessionId || !storyData) {
        alert('⚠️ No game session found!');
        window.location.href = '/';
        return;
    }

    document.getElementById('characterDisplay').textContent = characterName;
    displayStory(storyData);
    updateGameState(gameState);
}

// ========== TYPING ANIMATION ==========
function typeWriter(element, text, speed = 15) {
    element.innerHTML = '';
    let i = 0;
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// ========== DISPLAY STORY ==========
function displayStory(storyData) {
    const storyText = document.getElementById('storyText');
    storyText.innerHTML = '';
    
    const paragraph = document.createElement('p');
    storyText.appendChild(paragraph);
    typeWriter(paragraph, storyData.story, 15);

    // Show new item notification
    if (storyData.newItem) {
        setTimeout(() => {
            showNotification('🎁 ITEM ACQUIRED!', storyData.newItem, 'success');
        }, 500);
    }

    // Show new ability notification
    if (storyData.newAbility) {
        setTimeout(() => {
            showNotification('⚡ ABILITY UNLOCKED!', storyData.newAbility, 'success');
        }, 1000);
    }

    if (storyData.choices && storyData.choices.length > 0) {
        setTimeout(() => {
            displayChoices(storyData.choices);
        }, storyData.story.length * 15 + 500);
    }
}

function displayChoices(choices) {
    const container = document.getElementById('choicesContainer');
    container.innerHTML = '';
    
    const moralityImpact = ['😈 -18', '😐 0', '😇 +12'];
    
    choices.forEach((choice, index) => {
        setTimeout(() => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.innerHTML = `
                <span class="choice-num">${index + 1}</span>
                <span>${choice}</span>
                <span style="float: right; font-size: 0.85rem; color: var(--text-secondary);">
                    ${moralityImpact[index]}
                </span>
            `;
            btn.style.opacity = '0';
            btn.style.transform = 'translateX(-20px)';
            btn.onclick = () => makeChoice(index + 1);
            container.appendChild(btn);
            
            setTimeout(() => {
                btn.style.transition = 'all 0.5s ease';
                btn.style.opacity = '1';
                btn.style.transform = 'translateX(0)';
            }, 10);
        }, index * 150);
    });
}

// ========== UPDATE GAME STATE ==========
function updateGameState(gameState) {
    currentGameState = gameState;

    // Update turn progress
    const turnProgress = (gameState.turnCount / maxTurns) * 100;
    document.getElementById('turnDisplay').textContent = `${gameState.turnCount}/${maxTurns}`;
    
    // Add progress bar if not exists
    if (!document.getElementById('turnProgress')) {
        const turnDisplay = document.getElementById('turnDisplay').parentElement;
        turnDisplay.innerHTML += `
            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 0.5rem;">
                <div id="turnProgress" style="width: ${turnProgress}%; height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.5s ease;"></div>
            </div>
        `;
    } else {
        document.getElementById('turnProgress').style.width = turnProgress + '%';
    }

    // Update health
    const percentage = (gameState.health / gameState.maxHealth) * 100;
    const healthFill = document.getElementById('healthFill');
    const healthText = document.getElementById('healthText');
    
    healthFill.style.width = percentage + '%';
    healthText.textContent = `${gameState.health}/${gameState.maxHealth}`;

    if (percentage < 30) {
        healthFill.classList.add('low');
    } else {
        healthFill.classList.remove('low');
    }

    // Update HUD stats
    document.getElementById('powerLevelDisplay').textContent = gameState.powerLevel || 'Weak Human';
    document.getElementById('killCountDisplay').textContent = gameState.killCount || 0;
    
    const moralityDisplay = document.getElementById('moralityDisplay');
    const morality = gameState.morality || 50;
    moralityDisplay.textContent = morality;
    
    if (morality <= 20) {
        moralityDisplay.style.color = 'var(--primary)';
    } else if (morality >= 80) {
        moralityDisplay.style.color = 'var(--success)';
    } else {
        moralityDisplay.style.color = 'var(--text-primary)';
    }

    // Update achievements
    if (gameState.achievements && gameState.achievements.length > 0) {
        document.getElementById('achievementCount').textContent = gameState.achievements.length;
    }

    // Update inventory with equipment
    const inventoryItems = document.getElementById('inventoryItems');
    if (gameState.inventory && gameState.inventory.length > 0) {
        inventoryItems.innerHTML = '';
        gameState.inventory.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'inventory-item';
            itemDiv.innerHTML = `
                ${item}
                <button onclick="equipItem('${item}')" style="float: right; padding: 0.25rem 0.5rem; background: var(--accent); border: none; border-radius: 4px; cursor: pointer; font-size: 0.75rem; color: white;">
                    Equip
                </button>
            `;
            inventoryItems.appendChild(itemDiv);
        });
    } else {
        inventoryItems.innerHTML = '<p class="empty-state">Empty inventory...</p>';
    }

    // Display equipped items
    if (gameState.equipment) {
        let equipText = '';
        if (gameState.equipment.weapon) equipText += `⚔️ ${gameState.equipment.weapon}<br>`;
        if (gameState.equipment.armor) equipText += `🛡️ ${gameState.equipment.armor}<br>`;
        if (gameState.equipment.accessory) equipText += `💍 ${gameState.equipment.accessory}<br>`;
        
        if (!document.getElementById('equipmentDisplay')) {
            const inventoryPanel = document.getElementById('inventoryItems').parentElement;
            const equipDiv = document.createElement('div');
            equipDiv.id = 'equipmentDisplay';
            equipDiv.style.cssText = 'margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); font-size: 0.85rem;';
            equipDiv.innerHTML = '<strong style="color: var(--accent);">EQUIPPED:</strong><br>' + (equipText || 'None');
            inventoryPanel.appendChild(equipDiv);
        } else {
            document.getElementById('equipmentDisplay').innerHTML = '<strong style="color: var(--accent);">EQUIPPED:</strong><br>' + (equipText || 'None');
        }
    }

    // Display special abilities
    if (gameState.specialAbilities && gameState.specialAbilities.length > 0) {
        if (!document.getElementById('abilitiesDisplay')) {
            const statsPanel = document.getElementById('statsPanel');
            const abilDiv = document.createElement('div');
            abilDiv.id = 'abilitiesDisplay';
            abilDiv.style.cssText = 'margin-top: 1.5rem; padding: 1rem; background: rgba(99,102,241,0.1); border-radius: 8px;';
            statsPanel.appendChild(abilDiv);
        }
        
        let abilText = '<strong style="color: var(--accent);">⚡ ABILITIES:</strong><br>';
        gameState.specialAbilities.forEach(ability => {
            abilText += `<div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 4px; font-size: 0.85rem;">${ability}</div>`;
        });
        document.getElementById('abilitiesDisplay').innerHTML = abilText;
    }

    updateStatsDisplay();
}

function updateStatsDisplay() {
    if (!currentGameState || !currentGameState.stats) return;
    
    const stats = currentGameState.stats;
    
    document.getElementById('strengthVal').textContent = stats.strength;
    document.getElementById('strengthBar').style.width = Math.min(100, (stats.strength / 25) * 100) + '%';
    
    document.getElementById('intelligenceVal').textContent = stats.intelligence;
    document.getElementById('intelligenceBar').style.width = Math.min(100, (stats.intelligence / 25) * 100) + '%';
    
    document.getElementById('charismaVal').textContent = stats.charisma;
    document.getElementById('charismaBar').style.width = Math.min(100, (stats.charisma / 25) * 100) + '%';
    
    document.getElementById('luckVal').textContent = stats.luck;
    document.getElementById('luckBar').style.width = Math.min(100, (stats.luck / 25) * 100) + '%';
}

// ========== EQUIP ITEM ==========
function equipItem(itemName) {
    fetch('/api/equip-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sessionId: sessionId,
            itemName: itemName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentGameState.equipment = data.equipment;
            currentGameState.inventory = data.inventory;
            updateGameState(currentGameState);
            showNotification('✅ EQUIPPED!', itemName, 'success');
        }
    });
}

// ========== MAKE CHOICE ==========
async function makeChoice(choiceNum) {
    if (isProcessing) return;
    isProcessing = true;

    const choiceBtns = document.querySelectorAll('.choice-btn');
    choiceBtns.forEach(btn => btn.style.opacity = '0.3');

    document.getElementById('loadingOverlay').classList.add('active');

    try {
        const response = await fetch('/api/make-choice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: sessionId,
                choice: choiceNum
            })
        });

        const data = await response.json();

        if (data.success) {
            displayStory(data.story);
            updateGameState(data.gameState);
            
            sessionStorage.setItem('currentStory', JSON.stringify(data.story));
            sessionStorage.setItem('gameState', JSON.stringify(data.gameState));

            // Show new achievements
            if (data.newAchievements && data.newAchievements.length > 0) {
                data.newAchievements.forEach((achievement, index) => {
                    setTimeout(() => {
                        showNotification(`🏆 ${achievement.icon} ACHIEVEMENT!`, achievement.name, 'success');
                    }, (index + 1) * 1000);
                });
            }

            // Combat check
            if (data.combat) {
                setTimeout(() => {
                    initiateCombat(data.combat);
                }, 2000);
            }

            if (data.gameState.health <= 0) {
                setTimeout(() => {
                    showNotification('💀 DEATH', 'Your journey ends here...', 'error');
                    setTimeout(() => document.getElementById('endModal').classList.add('active'), 2000);
                }, 1000);
            }

            // Check if game complete
            if (data.gameState.turnCount >= maxTurns) {
                setTimeout(() => {
                    showNotification('🎉 JOURNEY COMPLETE!', 'Your legend is written!', 'success');
                    setTimeout(() => document.getElementById('endModal').classList.add('active'), 2000);
                }, 1000);
            }
        } else {
            showNotification('❌ Error', data.error, 'error');
        }
    } catch (error) {
        showNotification('❌ Connection Error', error.toString(), 'error');
    } finally {
        document.getElementById('loadingOverlay').classList.remove('active');
        isProcessing = false;
    }
}

// ========== ENHANCED COMBAT SYSTEM ==========
let currentEnemy = null;
let playerTurn = true;

function initiateCombat(enemyData) {
    currentEnemy = enemyData;
    
    const modal = document.getElementById('combatModal');
    document.getElementById('combatEnemy').textContent = enemyData.emoji;
    
    // Display enemy weaknesses
    let weaknessText = '';
    if (enemyData.weakness) {
        weaknessText = `<div style="margin-top: 0.5rem; color: var(--warning); font-size: 0.85rem;">⚠️ Weak to: ${enemyData.weakness}</div>`;
    }
    if (enemyData.resistance) {
        weaknessText += `<div style="color: var(--text-secondary); font-size: 0.85rem;">🛡️ Resists: ${enemyData.resistance}</div>`;
    }
    
    document.getElementById('combatEnemyName').innerHTML = `
        ${enemyData.name}
        ${weaknessText}
    `;
    
    updateEnemyHealth(enemyData.hp, enemyData.hp);
    
    document.getElementById('combatLog').innerHTML = `
        <p style="color: var(--primary); font-weight: bold;">⚔️ ${enemyData.name} appears!</p>
    `;
    
    modal.classList.add('active');
}

function updateEnemyHealth(current, max) {
    const percentage = (current / max) * 100;
    document.getElementById('enemyHealthFill').style.width = percentage + '%';
    document.getElementById('enemyHealthText').textContent = `${current}/${max}`;
}

function combatAction(action) {
    if (!playerTurn) return;
    playerTurn = false;
    
    const log = document.getElementById('combatLog');
    let damage = 0;
    let isCrit = false;
    
    // Calculate player damage based on stats and equipment
    const stats = currentGameState.stats;
    const equipment = currentGameState.equipment;
    
    switch(action) {
        case 'attack':
            damage = stats.strength * 2;
            if (equipment.weapon) {
                damage += 15; // Weapon bonus
                
                // Check type advantage
                if (checkTypeAdvantage(equipment.weapon, currentEnemy.weakness)) {
                    damage *= 1.5;
                    log.innerHTML += `<p class="critical">💥 SUPER EFFECTIVE! Critical hit!</p>`;
                    isCrit = true;
                }
            }
            damage *= (0.9 + Math.random() * 0.3);
            log.innerHTML += `<p class="damage">⚔️ You dealt ${Math.floor(damage)} damage!</p>`;
            break;
            
        case 'defend':
            damage = 0;
            const healAmount = Math.floor(currentGameState.maxHealth * 0.1);
            currentGameState.health = Math.min(currentGameState.maxHealth, currentGameState.health + healAmount);
            updateGameState(currentGameState);
            log.innerHTML += `<p class="heal">🛡️ You defended! Recovered ${healAmount} HP!</p>`;
            break;
            
        case 'skill':
            damage = stats.intelligence * 3;
            if (currentGameState.specialAbilities && currentGameState.specialAbilities.length > 0) {
                const ability = currentGameState.specialAbilities[0];
                damage += 25;
                log.innerHTML += `<p class="critical">⚡ ${ability}! ${Math.floor(damage)} damage!</p>`;
            } else {
                log.innerHTML += `<p class="damage">⚡ Special attack! ${Math.floor(damage)} damage!</p>`;
            }
            damage *= (0.9 + Math.random() * 0.4);
            break;
            
        case 'flee':
            if (Math.random() < 0.6) {
                log.innerHTML += `<p style="color: var(--warning);">💨 You fled successfully!</p>`;
                setTimeout(() => {
                    document.getElementById('combatModal').classList.remove('active');
                    playerTurn = true;
                }, 1500);
                return;
            } else {
                log.innerHTML += `<p style="color: var(--primary);">❌ Escape failed!</p>`;
            }
            break;
    }
    
    // Apply damage to enemy
    if (damage > 0) {
        currentEnemy.hp -= Math.floor(damage);
        
        // Get original max HP
        const originalData = ENEMY_TYPES[currentEnemy.name];
        const scale = 1 + (currentGameState.turnCount / maxTurns);
        const maxHp = Math.floor(originalData.hp * scale);
        
        updateEnemyHealth(currentEnemy.hp, maxHp);
    }
    
    // Check if enemy defeated
    if (currentEnemy.hp <= 0) {
        log.innerHTML += `<p style="color: var(--success); font-weight: bold;">🎉 ${currentEnemy.name} defeated!</p>`;
        
        // Notify backend
        fetch('/api/combat-victory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentGameState.killCount = data.killCount;
                currentGameState.morality = data.morality;
                updateGameState(currentGameState);
            }
        });
        
        setTimeout(() => {
            document.getElementById('combatModal').classList.remove('active');
            showNotification('⚔️ VICTORY!', `${currentEnemy.name} defeated!`, 'success');
            playerTurn = true;
        }, 2000);
        return;
    }
    
    // Enemy turn
    setTimeout(() => {
        enemyTurn();
    }, 1500);
}

function enemyTurn() {
    const enemyDamage = currentEnemy.damage * (0.8 + Math.random() * 0.4);
    let finalDamage = enemyDamage;
    
    // Defense bonus
    if (currentGameState.equipment.armor) {
        finalDamage *= 0.75; // 25% damage reduction
    }
    
    currentGameState.health -= Math.floor(finalDamage);
    
    const log = document.getElementById('combatLog');
    log.innerHTML += `<p class="damage">💢 ${currentEnemy.name} attacks! You take ${Math.floor(finalDamage)} damage!</p>`;
    
    // Auto-scroll combat log
    log.scrollTop = log.scrollHeight;
    
    updateGameState(currentGameState);
    
    // Check if player died
    if (currentGameState.health <= 0) {
        log.innerHTML += `<p style="color: var(--primary); font-weight: bold;">💀 You have been defeated...</p>`;
        setTimeout(() => {
            document.getElementById('combatModal').classList.remove('active');
            document.getElementById('endModal').classList.add('active');
        }, 2000);
        return;
    }
    
    playerTurn = true;
}

function checkTypeAdvantage(weaponName, enemyWeakness) {
    const weaponTypes = {
        'Cursed Blade': 'dark',
        'Dragon Slayer': 'physical',
        'Blood Scythe': 'blood',
        'Chakra Blade': 'ninja_arts',
        'Holy Sword': 'holy',
        'Quinque': 'quinque'
    };
    
    return weaponTypes[weaponName] === enemyWeakness;
}

// ========== NOTIFICATION SYSTEM ==========
function showNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 2rem;
        background: var(--bg-secondary);
        border: 2px solid ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--primary)' : 'var(--accent)'};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        min-width: 300px;
        z-index: 10001;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        animation: slideInRight 0.5s ease;
    `;
    
    notification.innerHTML = `
        <div style="font-weight: bold; font-size: 1rem; margin-bottom: 0.5rem; color: ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--primary)' : 'var(--accent)'};">
            ${title}
        </div>
        <div style="font-size: 0.9rem; color: var(--text-secondary);">
            ${message}
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Add animations to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ========== ENDING SYSTEM ==========
function chooseEnding(endingType) {
    document.getElementById('loadingOverlay').classList.add('active');
    
    fetch('/api/end-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sessionId: sessionId,
            endingType: endingType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayEnding(data.ending, data.finalStats);
        }
    })
    .finally(() => {
        document.getElementById('loadingOverlay').classList.remove('active');
    });
}

function displayEnding(endingText, finalStats) {
    const modal = document.getElementById('endModal');
    modal.innerHTML = `
        <div class="modal-box" style="max-width: 800px;">
            <h2 style="text-align: center; font-size: 2rem; margin-bottom: 2rem; color: var(--accent);">
                ⚔️ YOUR LEGEND IS COMPLETE ⚔️
            </h2>
            
            <div style="background: rgba(0,0,0,0.4); padding: 2rem; border-radius: 12px; border-left: 4px solid var(--accent); margin-bottom: 2rem;">
                <p style="font-size: 1.1rem; line-height: 1.8; color: var(--text-primary);">
                    ${endingText}
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 2rem;">
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase;">Turns Survived</div>
                    <div style="font-size: 2rem; font-weight: bold; color: var(--accent);">${finalStats.turns}/${finalStats.maxTurns}</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase;">Total Kills</div>
                    <div style="font-size: 2rem; font-weight: bold; color: var(--primary);">${finalStats.killCount}</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase;">Final Power</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: var(--success);">${finalStats.finalPower}</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase;">Morality</div>
                    <div style="font-size: 2rem; font-weight: bold; color: ${finalStats.morality <= 20 ? 'var(--primary)' : finalStats.morality >= 80 ? 'var(--success)' : 'var(--text-primary)'};">
                        ${finalStats.morality}/100
                    </div>
                </div>
            </div>
            
            ${finalStats.achievements.length > 0 ? `
                <div style="background: rgba(99,102,241,0.1); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                    <h3 style="text-align: center; margin-bottom: 1rem; color: var(--accent);">🏆 ACHIEVEMENTS UNLOCKED</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                        ${finalStats.achievements.map(a => `
                            <div style="background: var(--bg-tertiary); padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.9rem;">
                                ${a.icon} ${a.name}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${finalStats.specialAbilities && finalStats.specialAbilities.length > 0 ? `
                <div style="background: rgba(229,9,20,0.1); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                    <h3 style="text-align: center; margin-bottom: 1rem; color: var(--primary);">⚡ ABILITIES MASTERED</h3>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        ${finalStats.specialAbilities.map(ability => `
                            <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 8px; text-align: center;">
                                ${ability}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <button onclick="window.location.href='/'" class="primary-btn" style="margin-top: 1rem;">
                <span>Play Again</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 12h18M12 5l7 7-7 7"/>
                </svg>
            </button>
        </div>
    `;
}

// ========== EVENT LISTENERS ==========
function setupEventListeners() {
    // Combat actions
    window.combatAction = combatAction;
    
    // Ending choices
    window.chooseEnding = chooseEnding;
    
    // Equipment
    window.equipItem = equipItem;
}
