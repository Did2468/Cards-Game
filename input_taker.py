import json
import os

def get_input():
	player_id = int(input("Enter the player ID: "))
	name = input("Enter the player name: ").strip()
	matches = int(input("Enter Matches: "))
	not_outs = int(input("Enter the Not outs: "))
	runs_scored = int(input("Enter the runs scored: "))
	highest = int(input("Enter the Highest score: "))
	bat_avg = float(input("Enter the batting average: "))
	balls_faced = int(input("Enter the balls faced: "))
	bat_sr = float(input("Enter the batting strike rate: "))
	hundreds = int(input("Enter the hundreds: "))
	fifties = int(input("Enter the fifties: "))
	balls_bowled = int(input("Enter the balls bowled: "))
	runs_given = int(input("Enter the runs given: "))
	catches = int(input("Enter the catches taken: "))
	wickets = int(input("Enter the wickets taken: "))
	ball_avg = float(input("Enter the bowling average: "))
	economy = float(input("Enter the economy: "))
	ball_sr = float(input("Enter the bowling strike rate: "))
	best_w = int(input("Enter the best figures wickets: "))
	best_r = int(input("Enter the best figures Runs: "))
	five_w = int(input("Enter the five wicket hauls: "))	
	return {
		"id":player_id,
		"name":name,
		"matches":matches,
		"not_outs":not_outs,
		"runs_scored":runs_scored,
		"highest":highest,
		"bat_avg":bat_avg,
		"balls_faced":balls_faced,
		"bat_sr":bat_sr,
		"hundreds":hundreds,
		"fifties":fifties,
		"balls_bowled":balls_bowled,
		"runs_given":runs_given,
		"catches":catches,
		"wickets":wickets,
		"ball_avg":ball_avg,
		"economy":economy,
		"ball_sr":ball_sr,
		"best_w":best_w,
		"best_r":best_r,
		"five_w":five_w
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
