#!/usr/bin/env bash

export RUI_ENV=prod

eval "$(conda shell.bash hook)"
conda activate rui

# do not use uwsgi for now!
# global application state
# uwsgi --yaml conf/ramlimit.uwsgi.yml
rui-be
