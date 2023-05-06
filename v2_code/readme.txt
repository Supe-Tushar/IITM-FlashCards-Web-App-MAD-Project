---------- Start whole app steps
start redis server in wsl ubuntu 
start mailhog.exe (download first)

d:
cd <dir path to code>

open anaconda: go to project folder of app.py and run 'python app.py'
open anaconda: go to project folder of app.py and run 'celery -A application.workers.celery worker --pool=solo -l info'

for scheduled jobs
open anaconda: go to project folder of app.py and run 'celery -A application.workers.celery beat -l info'


=============================================================================
