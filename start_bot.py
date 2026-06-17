from waitress import serve
from config.wsgi import application

print("Starting Nairobi Events Bot on http://0.0.0.0:8002")
serve(application, host='0.0.0.0', port=8002, threads=4)
