import random
QSTAT_CHOICES = {
    1: "rank", 2: "matches", 3: "runs", 4: "balls", 5: "fifties", 
    6: "hundreds", 7: "sr", 8: "wickets", 9: "econ", 10: "best_figures"
}
STAT_CHOICES = {
    1 : "matches" , 2 : "not_outs" , 3: "runs_scored", 4: "highest", 5: "bat_avg",
    6: "balls_faced", 7: "bat_sr", 8: "hundreds", 9: "fifties", 10: "balls_bowled",
    11: "runs_given", 12: "catches", 13: "wickets", 14: "ball_avg",15: "economy",
    16: "ball_sr", 17: "best_figures",18: "five_w"
}

def evaluate(choice,player1,player2):
	if(choice == 11 or choice == 14 or choice == 15):
		stat = STAT_CHOICES[choice]		#if choice is runs_given or bowling economy or bowling avg  it should be low for the player to win 
		stat1 = player1[stat]
		stat2 = player2[stat]
		if(stat1==0):
			return 0
		elif(stat2==0):
			return 1
		elif(stat1<=stat2):
			return 1
		else:
			return 0
	elif(choice==17):
		stat_w = "best_w"			# for best_figures its a bit complicated so this 
		stat_r = "best_r"
		
		stat1_w = player1[stat_w]
		stat2_w = player2[stat_w]
		
		if(stat1_w>stat2_w):
			return 1	
		elif(stat1_w==stat2_w):
			stat1_r = player1[stat_r]
			stat2_r = player2[stat_r]
			if(stat1_r<=stat2_r):
				return 1
			else:
				return 0
		else:
			return 0
	else:
		stat = STAT_CHOICES[choice]			# if choice is remaining anything it should be greater to be won
		stat1 = player1[stat]
		stat2 = player2[stat]
		if(stat1==0):
			return 0
		elif(stat2==0):
			return 1
		elif(stat1>=stat2):
			return 1
		else:
			return 0


#Note: for now the game engine gives advatage for playing who got turn if the both stats are equal. Later need to update such that it goes into buffer untill a winner is decided

