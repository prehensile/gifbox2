source .venv/bin/activate
#pip install -r requirements.txt
export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_RUN_PORT=5000
export FLASK_RUN_HOST=0.0.0.0
flask run