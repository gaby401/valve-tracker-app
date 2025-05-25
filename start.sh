#!/bin/bash
source /opt/render/project/src/venv/bin/activate
gunicorn app:app
