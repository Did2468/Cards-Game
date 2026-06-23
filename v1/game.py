import random

# data section
# name, ranking, matches, runs scored,balls faced,fifties,centuries,strike rate,wickets taken,economy,best bowling figures

data = {
    1: ["Virat Kohli", 1, 125, 4188, 3030, 38, 1, 138.2, 4, 8.1, [1, 13]],
    2: ["Babar Azam", 2, 119, 4110, 3160, 36, 3, 130.1, 0, 0.0, [0, 0]],
    3: ["Rohit Sharma", 3, 159, 4231, 3005, 32, 5, 140.8, 1, 9.3, [1, 22]],
    4: ["Rashid Khan", 4, 85, 450, 340, 0, 0, 132.3, 138, 6.07, [5, 3]],
    5: ["Jasprit Bumrah", 5, 62, 70, 110, 0, 0, 63.6, 74, 6.55, [3, 11]],
    6: ["Hardik Pandya", 6, 92, 1348, 965, 3, 0, 139.7, 73, 8.15, [4, 16]],
    7: ["Glenn Maxwell", 7, 106, 2468, 1600, 10, 5, 154.2, 40, 7.50, [3, 10]],
    8: ["Shakib Al Hasan", 8, 117, 2382, 1950, 12, 0, 122.1, 140, 6.78, [5, 20]],
    9: ["Suryakumar Yadav", 9, 60, 2141, 1247, 17, 4, 171.7, 0, 0.0, [0, 0]],
    10: ["Mitchell Starc", 10, 60, 95, 105, 0, 0, 90.4, 76, 7.63, [4, 20]]
}
CARDS_NUM = int(input("Enter how many card To have in the match(Max is 100): "))
cards = random.sample(range(1,11),CARDS_NUM)
print(cards)
#giving players cards (card distribution)
random.shuffle(cards)

player1 = cards[:(CARDS_NUM//2)]	#the player
player2= cards[(CARDS_NUM//2):]		#the ai


turn  = 0	# 0 for player and 1 for the computer 

# toss section 
toss_choice = int(input("Select your Toss option. 0 for heads and 1 for tails: "))

toss_value = random.randint(0,1)

if(toss_value == toss_choice):
	print("You won the toss and u go first")
	turn = 0
else:
	print("You lost the toss and ai will go first")
	turn  = 1


# game simulation

while(len(player1)!=0 and len(player2)!=0):
	curr_player1 = data[player1[0]]
	curr_player2 = data[player2[0]]
	print("\n"*3)
	print("="*40,end="")
	print("New round starting",end="")
	print("="*40)
	print("\n"*3)
	if(turn==0):
		print("=" * 40)
		print(f" CARD NO. {curr_player1[1]} | {curr_player1[0]}")
		print("=" * 40)
		print(f" Matches Played : {curr_player1[2]}")
		print(f" Runs Scored   : {curr_player1[3]}")
		print(f" Balls Faced   : {curr_player1[4]}")
		print(f" 50s / 100s    : {curr_player1[5]} / {curr_player1[6]}")
		print(f" Strike Rate   : {curr_player1[7]}")
		print(f" Wickets       : {curr_player1[8]}")
		print(f" Economy Rate  : {curr_player1[9]}")
		print(f" Best Figures  : {curr_player1[10][0]} Wkts for {curr_player1[10][1]} Runs")
		print("=" * 40)
		
		curr_choice = int(input("Enter your choice: "))			#taking the input from the user on what stat he wanna keep
		
		print("\n"*4)
		print("The opponents card is following")
		print("=" * 40)
		print(f" CARD NO. {curr_player2[1]} | {curr_player2[0]}")
		print("=" * 40)
		print(f" Matches Played : {curr_player2[2]}")
		print(f" Runs Scored   : {curr_player2[3]}")
		print(f" Balls Faced   : {curr_player2[4]}")
		print(f" 50s / 100s    : {curr_player2[5]} / {curr_player2[6]}")
		print(f" Strike Rate   : {curr_player2[7]}")
		print(f" Wickets       : {curr_player2[8]}")
		print(f" Economy Rate  : {curr_player2[9]}")
		print(f" Best Figures  : {curr_player2[10][0]} Wkts for {curr_player2[10][1]} Runs")
		print("=" * 40)


		#comparing the card stat
		
		# if the stat is rank of the card
		if(curr_choice == 1 or curr_choice == 9):
			if(curr_player1[curr_choice]<curr_player2[curr_choice]):
				print("You won!!")
				temp = player2.pop(0)
				temp1 = player1.pop(0)
				player1.append(temp)
				player1.append(temp1)
			else:
				print("You lose!!")
				turn  = 1
				temp = player2.pop(0)
				temp1 = player1.pop(0)
				player2.append(temp1)
				player2.append(temp)

		# if the stat is bowling figures
		elif(curr_choice== 10):
			if(curr_player1[10][0]>curr_player2[10][0]):
				print("You won")
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player1.append(temp)
				player1.append(temp1)

			elif(curr_player1[10][0]<curr_player2[10][0]):
				print("You lose")
				turn = 1
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player2.append(temp)
				player2.append(temp1)
			else:
				if(curr_player1[10][1]<curr_player2[10][1]):
					print("You won!!")
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player1.append(temp1)
					player1.append(temp)
				elif(curr_player1[10][1]>curr_player2[10][1]):
					print("You lose!!")
					turn = 1
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player2.append(temp)
					player2.append(temp1)
				else:
					print("Its a tie breaker!!")
					if(curr_player1[1]<curr_player2[1]):
						print("You won on basis of rank")
						temp = player1.pop(0)
						temp1 = player2.pop(0)
						player1.append(temp)
						player1.append(temp1)
					else:
						print("You lose on basis of rank")
						turn = 1
						temp = player1.pop(0)
						temp1 = player2.pop(0)
						player2.append(temp)
						player2.append(temp1)
		# for every other stat 
		else:
			if(curr_player1[curr_choice]>curr_player2[curr_choice]):
				print("You won!!")
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player1.append(temp)
				player1.append(temp1)

			elif(curr_player1[curr_choice]<curr_player2[curr_choice]):
				print("You lose!!")
				turn = 1
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player2.append(temp)
				player2.append(temp1)
			else:
				print("Its a tie breaker!!")
				if(curr_player1[1]>curr_player2[1]):
					print("You won")
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player1.append(temp)
					player1.append(temp1)
				else:
					print("You lose")
					turn = 1
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player2.append(temp)
					player2.append(temp1)
	
	elif(turn==1):
		print("The opponents card is: \n")
		print("=" * 40)
		print(f" CARD NO. {curr_player2[1]} | {curr_player2[0]}")
		print("=" * 40)
		print(f" Matches Played : {curr_player2[2]}")
		print(f" Runs Scored   : {curr_player2[3]}")
		print(f" Balls Faced   : {curr_player2[4]}")
		print(f" 50s / 100s    : {curr_player2[5]} / {curr_player2[6]}")
		print(f" Strike Rate   : {curr_player2[7]}")
		print(f" Wickets       : {curr_player2[8]}")
		print(f" Economy Rate  : {curr_player2[9]}")
		print(f" Best Figures  : {curr_player2[10][0]} Wkts for {curr_player2[10][1]} Runs")
		print("=" * 40)	
		

		print("\n"*3)
		print("Your card is : \n")
		print("=" * 40)
		print(f" CARD NO. {curr_player1[1]} | {curr_player1[0]}")
		print("=" * 40)
		print(f" Matches Played : {curr_player1[2]}")
		print(f" Runs Scored   : {curr_player1[3]}")
		print(f" Balls Faced   : {curr_player1[4]}")
		print(f" 50s / 100s    : {curr_player1[5]} / {curr_player1[6]}")
		print(f" Strike Rate   : {curr_player1[7]}")
		print(f" Wickets       : {curr_player1[8]}")
		print(f" Economy Rate  : {curr_player1[9]}")
		print(f" Best Figures  : {curr_player1[10][0]} Wkts for {curr_player1[10][1]} Runs")
		print("=" * 40)
		
		continue_choice = input("If done seeing your card continue press any alphabet: ")
		if(continue_choice == 'a'<='z'):
			x = 1+0

		curr_choice = random.randint(1,10)	# ai's choice which is random
	
		print(f"The opponent chose {curr_choice}")
		
		# if the stat is rank of the card
		if(curr_choice == 1 or curr_choice == 9):
			if(curr_player1[curr_choice]<curr_player2[curr_choice]):
				print("You won!!")
				temp = player2.pop(0)
				temp1 = player1.pop(0)
				player1.append(temp)
				player1.append(temp1)
				turn = 0
			else:
				print("You lose!!")
				temp = player2.pop(0)
				temp1 = player1.pop(0)
				player2.append(temp1)
				player2.append(temp)

		# if the stat is bowling figures
		elif(curr_choice== 10):
			if(curr_player1[10][0]>curr_player2[10][0]):
				print("You won")
				turn = 0
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player1.append(temp)
				player1.append(temp1)

			elif(curr_player1[10][0]<curr_player2[10][0]):
				print("You lose")
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player2.append(temp)
				player2.append(temp1)
			else:
				if(curr_player1[10][1]<curr_player2[10][1]):
					print("You won!!")
					turn = 0
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player1.append(temp1)
					player1.append(temp)
				elif(curr_player1[10][1]>curr_player2[10][1]):
					print("You lose!!")
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player2.append(temp)
					player2.append(temp1)
				else:
					print("Its a tie breaker!!")
					if(curr_player1[1]<curr_player2[1]):
						print("You won on basis of rank")
						turn = 0
						temp = player1.pop(0)
						temp1 = player2.pop(0)
						player1.append(temp)
						player1.append(temp1)
					else:
						print("You lose on basis of rank")
						temp = player1.pop(0)
						temp1 = player2.pop(0)
						player2.append(temp)
						player2.append(temp1)
		# for every other stat 
		else:
			if(curr_player1[curr_choice]>curr_player2[curr_choice]):
				print("You won!!")
				turn = 0
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player1.append(temp)
				player1.append(temp1)

			elif(curr_player1[curr_choice]<curr_player2[curr_choice]):
				print("You lose!!")
				temp = player1.pop(0)
				temp1 = player2.pop(0)
				player2.append(temp)
				player2.append(temp1)
			else:
				print("Its a tie breaker!!")
				if(curr_player1[1]>curr_player2[1]):
					print("You won")
					turn = 0
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player1.append(temp)
					player1.append(temp1)
				else:
					print("You lose")
					temp = player1.pop(0)
					temp1 = player2.pop(0)
					player2.append(temp)
					player2.append(temp1)
		
		option = input("Continue next round (y/n): ")
		if(option=='n'):
			print("Leaving the game!!")
			break

if(len(player2)==0):
	print("Congratulation You won the match!!!")
else:
	print("The opponent won the match!!!")
	
