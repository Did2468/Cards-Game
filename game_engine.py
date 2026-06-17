import random
STAT_CHOICES = {
    1: "rank", 2: "matches", 3: "runs", 4: "balls", 5: "fifties", 
    6: "hundreds", 7: "sr", 8: "wickets", 9: "econ", 10: "best_figures"
}

def evaluate(choice,player1,player2):
	if(choice == 1 or choice == 9):
		stat = STAT_CHOICES[choice]		#if choice is rank or bowling economy it should be low for the player to win 
		stat1 = player1[stat]
		stat2 = player2[stat]
		if(stat1<=stat2):
			return 1
		else:
			return 0
	elif(choice==10):
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
		if(stat1>=stat2):
			return 1
		else:
			return 0


#Note: for now the game engine gives advatage for playing who got turn if the both stats are equal. Later need to update such that it goes into buffer untill a winner is decided

