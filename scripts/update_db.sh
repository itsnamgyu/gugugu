# Update DB
source venv/bin/activate;
sudo chmod g+w db.sqlite3
python manage.py makemigrations;
python manage.py migrate;
sudo chmod g-w db.sqlite3
