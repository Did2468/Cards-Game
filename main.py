import json
from game_setup import toss
from game_setup import distribute
from printer import printing
from printer import print_menu
from printer import print_victory
from printer import print_defeat
from game_engine import evaluate
import random
import time

if __name__=="__main__":
	with open("player_stats.json","r") as file:
		master_data = json.load(file)
									# Loading the data and converting into a hash set for easy lookups
	cards = {player["id"]:player for player in master_data}
	
	#Distributing the Cards
		
	player1,player2 = distribute(len(cards))

									# player1 is the palyer player2 is the Computer playing

	#Toss to decide who will play
	turn = 1 if toss()==1 else 0
	
	while(len(player1)!=0 and len(player2)!=0):
		if(turn==1):
			print("------Your Current card is------")
			time.sleep(1.5)
			printing(cards[player1[0]])					#printing player 1 card
			print_menu()
			choice = int(input())
			game = evaluate(choice,cards[player1[0]],cards[player2[0]])		#calling the game engine 
			print("------Your opponent card is------")
			printing(cards[player2[0]])					# printing player 2 card
			input("Press Enter to continue: ")
			if(game==1):
				print("You Won")
				temp = player2.pop(0)
				temp1 = player1.pop(0)
				player1.append(temp)					# making sure the card are kept back 
				player1.append(temp1)
			else:
				print("You Lose")
				temp = player2.pop(0)
				temp1 = player1.pop(0)					# making sure the card are kept back
				player2.append(temp1)
				player2.append(temp)
				turn = 0


		else:
			print("------Your Current card is ------")			#printing player 1 card
			printing(cards[player1[0]])
			input("Press Enter to continue: ")
			print("------Your opponent card is ------")
			printing(cards[player2[0]])					#printing player 2 card
			comp_choice = random.randint(1,11)				# for now the computer makes random choice later we can make it intelligent
			game = evaluate(comp_choice,cards[player1[0]],cards[player2[0]])		#calling the game engine
			print(f"The Opponent choose stat {comp_choice}")
			if(game==0):
				print("You Lose")
				temp = player2.pop(0)
				temp1 = player1.pop(0)					#making sure cards are kept back
				player2.append(temp)
				player2.append(temp1)
			else:
				print("You Won")
				temp = player2.pop(0)
				temp1 = player1.pop(0)
				player1.append(temp)					#makingg sure cards are kept back 
				player1.append(temp1)
				turn = 1
		print()
		print()
		print()
		print()	
		print("------Starting New Round------")
		print()
		print()
		print()
		print()
		time.sleep(1.5)
	if(len(player1)==0):
		print_victory()
	else:
		print_defeat()
