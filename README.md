python -m venv .venv

.\.venv\Scripts\activate

pip install --upgrade pip

pip install -r requirements.txt

python punkt.py

train.py

python app.py