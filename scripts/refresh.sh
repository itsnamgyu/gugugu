# Pull from git, update stuff, deploy Apache!
git pull;
source venv/bin/activate;
python manage.py makemigrations;
sudo chown `whoami` db.sqlite3
python manage.py migrate;
sudo chown www-data db.sqlite3
python manage.py collectstatic --noinput;
sudo apachectl restart;
