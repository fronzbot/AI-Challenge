@echo off
C:\Python32\python "%~dp0playgame.py" -So --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 1000 --map_file "%~dp0maps\maze\maze_04p_01.map" %* "C:\Python32\python ""%~dp0sample_bots\python\HunterBot.py""" "C:\Python32\python ""%~dp0sample_bots\python\LeftyBot.py""" "C:\Python32\python ""%~dp0sample_bots\python\GreedyBot.py""" "C:\Python32\python ""C:\Users\Kevin\Coding-Projects\AI-Challenge\Fronzbot.py""" | java -jar visualizer.jar

