menu = """
┌────────────────────────────────────────────┐
│         CHOOSE YOUR BATTLE STAT            │
├────────────────────────────────────────────┤
│  1. Matches      │ 10. Balls Bowled        │
│  2. Not Outs     │ 11. Runs Given          │
│  3. Runs         │ 12. Catches             │
│  4. High Score   │ 13. Wickets             │
│  5. Bat Avg      │ 14. Bowl Avg            │
│  6. Balls Faced  │ 15. Economy             │
│  7. Strike Rate  │ 16. Bowl SR             │
│  8. Hundreds     │ 17. Best Figures        │
│  9. Fifties      │ 18. 5WI                 │
└────────────────────────────────────────────┘
👉 Choose a stat (1-18): """

def printing(curr_player1):
    labels = {
        "matches": "Matches", "not_outs": "Not Outs", "runs_scored": "Runs", 
        "highest": "Highest Score", "bat_avg": "Batting Avg", "balls_faced": "Balls Faced", 
        "bat_sr": "Batting SR", "hundreds": "100s", "fifties": "50s", 
        "balls_bowled": "Balls Bowled", "runs_given": "Runs Given", "catches": "Catches", 
        "wickets": "Wickets", "ball_avg": "Bowling Avg", "economy": "Economy", 
        "ball_sr": "Bowling SR", "best_figures": "Best Figures", "five_w": "5 Wickets"
    }

    left_keys = ["matches", "not_outs", "runs_scored", "highest", "bat_avg", "balls_faced", "bat_sr", "hundreds", "fifties"]
    right_keys = ["balls_bowled", "runs_given", "catches", "wickets", "ball_avg", "economy", "ball_sr", "best_figures", "five_w"]

    print("=" * 68)
    print(f" {curr_player1['name'].upper()}")
    print("=" * 68)

    for l_key, r_key in zip(left_keys, right_keys):
        l_label = labels[l_key]
        l_val = curr_player1.get(l_key, "-")
        left_side = f"{l_label}: {l_val}"

        r_label = labels[r_key]
        if r_key == "best_figures":
            w = curr_player1.get("best_w", 0)
            r = curr_player1.get("best_r", 0)
            right_side = f"{r_label}: {w}/{r}"
        else:
            r_val = curr_player1.get(r_key, "-")
            right_side = f"{r_label}: {r_val}"

        print(f" {left_side:<34} | {right_side}")
        
    print("=" * 68)

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
