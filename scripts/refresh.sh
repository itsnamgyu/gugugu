# Pull from git, update stuff, deploy Apache!
git pull;
source venv/bin/activate;
sudo chmod g+w db.sqlite3
python manage.py makemigrations;
python manage.py migrate;
sudo chmod g-w db.sqlite3
python manage.py collectstatic --noinput;
sudo apachectl restart;
