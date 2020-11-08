#! /bin/bash
ls -la;
python3 src/app.py & firefox -kioski -private-window localhost:3333
