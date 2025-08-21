# 🚀 Space Game

A 2-player local spaceship battle built with Pygame.
Blast your friend with lasers, dodge incoming fire, and claim victory in this fast-paced retro-style duel.

## 🎮 Gameplay

Two spaceships face off, separated by a border.

Each player can move within their half of the screen and fire bullets.

Health starts at 100, and every hit reduces it by 8.

The first spaceship to reach 0 health loses.

## 🕹️ Controls

Player 1 (Yellow Spaceship)

W → Move Up

S → Move Down

A → Move Left

D → Move Right

F → Shoot

## Player 2 (Red Spaceship)

Arrow Keys → Move

Right Ctrl → Shoot

## 📦 Installation

Clone this repository:
```bash
git clone https://github.com/kann4n/Pygames.git
cd Pygames/StarFight
```

Install dependencies:
```python
pip install pygame
```

Run the game:
```bash
python main.py
```
## 🎵 Assets

Spaceships and background images stored in assets/images/

Sounds stored in assets/sounds/

Icon stored in assets/icons/

Make sure your assets folder is structured like this:
```markdown
assets/
│── images/
│   ├── spaceship_yellow.png
│   ├── spaceship_red.png
│   └── space.png
│── sounds/
│   ├── Grenade+1.mp3
│   └── Gun+Silencer.mp3
└── icons/
    └── icon.png
```
