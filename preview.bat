@echo off
start "Peru site preview" http://localhost:8000
py -3 -m http.server 8000 --directory dist
