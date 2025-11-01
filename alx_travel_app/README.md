# ALX Travel App (Celery + RabbitMQ + Email Notifications)

## Setup Steps

1. **Install dependencies**
   ```bash
   pip install celery django
Install RabbitMQ

Ubuntu: sudo apt install rabbitmq-server

Windows: Download from https://www.rabbitmq.com

Run RabbitMQ

bash
Copy code
rabbitmq-server
Start Celery worker

bash
Copy code
celery -A alx_travel_app worker -l info
Run Django server

bash
Copy code
python manage.py runserver
Trigger booking

Create a booking via API or admin.

Check email logs to confirm async email delivery.

✅ Background email tasks are now handled asynchronously using Celery + RabbitMQ.