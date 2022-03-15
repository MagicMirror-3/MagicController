#!/bin/bash
cd /
mkdir logs
cd /MagicMirror || exit
python /MagicController/Configuration/load_default_config.py
python /MagicController/MagicController.py > /logs/controller_log.txt &
npm run server > /logs/mirror_log.txt &
