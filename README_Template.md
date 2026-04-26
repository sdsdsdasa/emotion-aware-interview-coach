# Air Combat X
A JavaFX vertical shoot 'em up built in BlueJ — inspired by classic arcade air combat games

Air Combat X is a top-down scrolling shooter developed as a team coursework project (CW4) at King's College London. The player pilots a fighter ship through three story levels — each with escalating enemy waves and a boss fight — before unlocking an endless Infinite Mode with dynamically scaling bosses. The game is built entirely in Java using JavaFX for rendering, input, animation, and audio, and was developed and run using the BlueJ IDE. This public repository is a cleaned portfolio version of the original project, with private materials and credentials removed.


![pic1](assets/pic1.png)

## Project Context

| | |
|---|---|
| **Type** | Coursework project (CW4) |
| **Institution** | King's College London |
| **Original repository** | Private / institution-hosted (GitHub KCL) |
| **This repository** | Public portfolio version |
| **Version** | 2.0 — 25 March 2025 |


## My Contribution

- Led the team, coordinating tasks, reviewing and approving pull requests, and resolving the majority of merge conflicts
- Wrote the base template code that defined how each game element (player, bullets, items) should be structured, along with the initial UI layout
- Built the `Game` class — the core engine driving the 120 FPS game loop, collision detection, enemy spawning, level transitions, item and buff system, boss logic, and score tracking
- Implemented the `Ship` class covering player movement, hitbox, and HP
- Integrated all subsystems (bullets, enemies, items, menus, boss, audio) into a cohesive, working game

This was a collaborative team project. The above reflects the areas where I had primary responsibility.


## Features

- Three story levels with a final boss fight at Level 2, each with unique BGM and increasing difficulty
- Infinite Mode (unlocked after completing the story): endless enemy waves with periodic boss spawns that scale in power over time
- Four collectable power-up items dropped by defeated enemies:
  - **Red** — Damage Buff: fires a 3-way spread shot for 5 seconds
  - **Green** — Penetration Buff: bullets pierce through multiple enemies for 5 seconds
  - **Yellow** — Speed Buff: fires twin parallel shots for 5 seconds
  - **Blue** — Heal: restores 1 HP immediately
- Bullet upgrade system: bullet stats improve automatically as the player's score increases
- Score system: +300 per enemy killed, +1000 for a boss kill, −500 if an enemy escapes off-screen
- Boss fires a 5-way spread of projectiles and moves across the screen
- Pause menu with in-game HP refill option (+3 HP)
- Game Over and Victory screens with Restart and Infinite Mode options
- 120 FPS capped game loop with per-frame collision detection
- Per-level background music and sound effects (explosions, item pickups)


## Controls

| Key | Action |
|---|---|
| `↑` `↓` `←` `→` | Move ship |
| `SPACE` | Fire |
| `SHIFT` | Pause / open pause menu |


## Tech Stack

- **Language:** Java
- **GUI / Rendering:** JavaFX (Canvas, ImageView, AnimationTimer, Timeline)
- **Audio:** JavaFX MediaPlayer (MP3 / WAV)
- **IDE:** BlueJ
- **Build:** BlueJ project (no external build tool)


## Setup

### Prerequisites

- **Java 17+** with JavaFX bundled, or a separate JavaFX SDK (11+)
- **BlueJ 5.x** (recommended) — download from [bluej.org](https://www.bluej.org)
  - BlueJ 5.x includes a bundled JDK with JavaFX; no extra configuration needed
- Alternatively, any IDE with JavaFX configured (VS Code, IntelliJ, etc.)

### Opening in BlueJ

1. Download or clone this repository:

```
git clone <your-repo-url>
```

2. Open BlueJ.

3. Go to **Project → Open Project** and select the `VectorGame-master 2` folder.

4. BlueJ will display all classes in the class diagram. Click **Compile** (the compile button in the toolbar) to compile the project.

5. See [Running the Game](#running-the-game) below.

### JavaFX Note (if not using BlueJ 5.x)

If you are using a JDK without bundled JavaFX, you must add the JavaFX SDK to your module path. In BlueJ, go to **Tools → Preferences → Libraries** and add the `lib` folder of your JavaFX SDK. Then add the following to BlueJ's VM options:

```
--module-path /path/to/javafx-sdk/lib --add-modules javafx.controls,javafx.fxml,javafx.media
```


## Running the Game

### In BlueJ

1. After compiling, right-click the **`Game`** class in the class diagram.
2. Select **`void main(String[] args)`**.
3. Click **OK** on the dialog (no arguments needed).
4. The game window will open at 800×800.

### From the terminal (with JavaFX on the module path)

```bash
javac --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls,javafx.media *.java
java --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls,javafx.media Game
```


## Project Structure

```
VectorGame-master 2/
├── Game.java          — Main entry point; game loop, collision, spawning, level logic
├── GameMenu.java      — Start / pause / game-over / victory menus
├── GameView.java      — Alternate launch view (start screen)
├── Ship.java          — Player ship (movement, HP, hitbox)
├── Character.java     — Abstract base class for all game entities
├── Enemy.java         — Enemy ship logic and movement
├── Boss.java          — Boss enemy with spread-shot attack and HP scaling
├── Bullet.java        — Player bullet with damage/speed/penetration buffs
├── eBullet.java       — Enemy bullet
├── Item.java          — Collectable power-up drops
├── Level.java         — Level configuration (enemies, speed, BGM, spawn rate)
├── SoundPlayer.java   — JavaFX MediaPlayer wrapper
├── planeGame.fxml     — FXML layout file
├── image/             — Game sprites (player, enemy, boss, bullets, background)
├── music/
│   ├── bgm/           — Per-level background music (MP3)
│   └── se/            — Sound effects (explosions, item pickup)
└── .gitignore
```


## Team

Developed as a team coursework project at King's College London. Four members contributed across game logic, UI, audio, and version control.


## Academic Note

This repository is provided for portfolio and demonstration purposes only. It should not be copied, reused, or submitted as academic work.
