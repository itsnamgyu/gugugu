# Update DB
source venv/bin/activate;
sudo chown `whoami` db.sqlite3
python manage.py makemigrations;
python manage.py migrate;
sudo chown www-data db.sqlite3
