menu = """
┌────────────────────────────────────────┐
│        CHOOSE YOUR BATTLE STAT         │
├────────────────────────────────────────┤
│  1. Rank        │   6. Hundreds        │
│  2. Matches     │   7. Strike Rate     │
│  3. Runs        │   8. Wickets         │
│  4. Balls       │   9. Economy         │
│  5. Fifties     │  10. Best Figures    │
└────────────────────────────────────────┘
👉 Choose a stat (1-10): """

def printing(curr_player1):
	print("=" * 40)
	print(f" CARD NO. {curr_player1["id"]} | {curr_player1["name"]}")
	print("=" * 40)
	print(f" Matches Played : {curr_player1["matches"]}")
	print(f" Runs Scored   : {curr_player1["runs"]}")
	print(f" Balls Faced   : {curr_player1["balls"]}")
	print(f" 50s / 100s    : {curr_player1["fifties"]} / {curr_player1["hundreds"]}")
	print(f" Strike Rate   : {curr_player1["sr"]}")
	print(f" Wickets       : {curr_player1["wickets"]}")
	print(f" Economy Rate  : {curr_player1["econ"]}")
	print(f" Best Figures  : {curr_player1["best_w"]} Wkts for {curr_player1["best_r"]} Runs")

def print_menu():
	print(menu)

def print_victory():
	print("\n┌────────────────────────────────────────┐")
	print("│  ********** VICTORY **********  │")
	print("├────────────────────────────────────────┤")
	print("│                                        │")
	print("│         CONGRATULATIONS!               │")
	print("│             YOU WON!                   │")
	print("│                                        │")
	print("└────────────────────────────────────────┘\n")
def print_defeat():
	print("\n┌────────────────────────────────────────┐")
	print("│  XXXXXXXXXX GAME OVER XXXXXXXXXX  │")
	print("├────────────────────────────────────────┤")
	print("│                                        │")
	print("│             DEFEAT!                    │")
	print("│       BETTER LUCK NEXT TIME!           │")
	print("│                                        │")
	print("└────────────────────────────────────────┘\n")
