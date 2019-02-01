# Pull from git, update stuff, deploy Apache!
git pull;
source venv/bin/activate;
python manage.py makemigrations;
python manage.py migrate;
python manage.py collectstatic --noinput;
sudo apachectl restart;
