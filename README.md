# MessagingService

Installation 

pip install Flask
pip install autobahn
pip install twisted
pip install uwsgi flask

# Start as WSGI

wsgi --socket 127.0.0.1:3031 --wsgi-file MessagingService.py --callable reactor
