import json
import os

def get_input():
	player_id = int(input("Enter the player ID: "))
	name = input("Enter the player name: ").strip()
	rank = int(input("Enter Rank: "))
	matches = int(input("Enter Matches: "))
	runs = int(input("Enter Runs: "))
	balls = int(input("Enter balls faced: "))
	fifties = int(input("Enter fifties: "))
	hundreds = int(input("Enter Hundreds: "))
	sr = float(input("Enter Strike Rate: "))
	wickets = int(input("Enter wickets: "))
	econ = float(input("Enter Economy rate: "))
	best_w = int(input("Enter Best Wickets in a match: "))
	best_r = int(input("Enter Runs conceded for best wickets: "))
	
	return {
		"id":player_id,
		"name":name,
		"rank":rank,
		"matches":matches,
		"runs":runs,
		"balls":balls,
		"fifties":fifties,
		"hundreds":hundreds,
		"sr":sr,
		"wickets":wickets,
		"econ":econ,
		"best_w":best_w,
		"best_r":best_r
	}


def update_stats_file(filename,new_player_data):
	if not new_player_data:
		print("Data not enteres invalid input")
		return
	player_list = []
	if os.path.exists(filename) and os.path.getsize(filename)>0:
		try:
			with open(filename,'r') as file:
				player_list = json.load(file)
				if not isinstance(player_list,list):
					player_list = []
		except json.JSONDecodeError:
			print("warning file was corrupted.starting fresh file")
			player_list = []
	player_list.append(new_player_data)
	with open(filename,'w') as file:
		json.dump(player_list,file,indent=4)
	print("Player added successfully!!")

if __name__ == "__main__":
	file_name = "player_stats.json"
	player_dict = get_input()
	update_stats_file(file_name,player_dict)
