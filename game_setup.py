import random

def toss():
	choice = int(input("Enter the choice heads(0) or tails(1): "))
	t = random.randint(0,1)
	if choice == t:
		print("You won the toss")
		return 1
	else:
		print("you loss the toss")
		return 0

def distribute(len_cards):
	CARD_NUM = int(input(f"Enter how many cards to play with max is {len_cards}: "))
	
	cards = random.sample(range(1,(len_cards)+1),CARD_NUM)

	random.shuffle(cards)
	
	player1 = cards[:(CARD_NUM//2)]
	player2 = cards[(CARD_NUM//2):]
	
	return player1,player2

def toss_logic(user_choice):
	t = random.randint(0,1)
	if(user_choice==t):
		return 1
	else:
		return 0

def distribute_logic(len_cards,card_num):
	cards = random.sample(range(1,len_cards+1),card_num)
	random.shuffle(cards)
	player1 = cards[:(card_num//2)]
	player2 = cards[(card_num//2):]
	
	return player1,player2
	
