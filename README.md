# MessagingService

Installation 

pip install Flask
pip install autobahn
pip install twisted

# Start as WSGI
wsgi --socket 127.0.0.1:3031 --wsgi-file MessagingService.py --callable reactor

# Start as twisted

export PYTHONPATH="$PYTHONPATH:<YourProjectPath>/MobilePayment/MobilePaymentApp/"
twistd -y ServiceMessaging.py
