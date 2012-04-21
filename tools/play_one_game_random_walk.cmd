@echo off
python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose -e --log_dir game_logs --turns 600 --map_file "%~dp0maps\random_walk\random_walk_02p_01.map" %* "python ""\users\Kevin\Desktop\AI Challenge\MyBot.py""" "python ""%~dp0sample_bots\python\GreedyBot.py"""

