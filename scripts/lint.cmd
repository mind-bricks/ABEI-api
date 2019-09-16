autopep8 -r --in-place --aggressive --aggressive --max-line-length=79 --exclude .env . && ^
flake8 --exclude=*/migrations/*.py,env/*,.env/*
