# Cricket Trump Cards Game

A simple trading card game built around Cricket stats.

Play it live here: **[https://cards-game-ub5v.onrender.com/](https://cards-game-ub5v.onrender.com/)**

The game revolves around a deck of cricket player cards divided equally between the user and the computer. Players battle by comparing various player stats, which now include 18 different categories ranging from batting averages to bowling economy.

## How to play

At the start of the game, a toss decides who goes first. If it's your turn, you choose a stat from your current card to battle against the computer's top card. 

The higher stat wins for most categories (like Runs, Hundreds, Strike Rate, Wickets). However, for certain stats like Bowling Economy, Bowling Average, or Runs Given, a lower number wins!

The winner of the round takes both cards and adds them to the bottom of their deck. The first person to run out of cards loses the game.

## Running locally

To run the game locally on your laptop:

1. Open your terminal and navigate to the project directory:
   ```bash
   cd Cards-Game
   ```
2. Activate the python virtual environment:
   - **Mac/Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your web browser and go to `http://127.0.0.1:5000`

## Adding new players

To add more players to the deck locally, run `input_taker.py`. It will prompt you for the player's 18 stats (batting and bowling) and save them directly to the `player_stats.json` file.
```bash
python input_taker.py
```
