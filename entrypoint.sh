#!/bin/bash

cd /MagicMirror || exit
npm run server &
python /MagicController/MagicController.py &

