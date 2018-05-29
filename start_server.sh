#!/bin/bash
gunicorn notifications:app --bind 127.0.0.1:8888 --daemon --access-logfile gunicorn.log --error-logfile gunicorn.log
