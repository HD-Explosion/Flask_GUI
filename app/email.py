from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path = env_path)
mail_pass = os.getenv('EMAIL_PASS')
def send_ip(app,ipfilename,ip_folder):

    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_SUPPRESS_SEND": False,
        "MAIL_USERNAME": 'darcylabweb@gmail.com',
        "MAIL_PASSWORD": mail_pass
    }



    app.config.update(mail_settings)
    mail = Mail(app)
    with app.app_context():
        msg = Message(subject="HD_eXplosion test",
                        sender=app.config.get("MAIL_USERNAME"),
                        recipients=["darcylabweb@gmail.com"], # replace with your email for testing
                        body="IP list is attached")
        with app.open_resource(ip_folder) as fp:
            msg.attach(
                ipfilename,
                'text/csv',
                fp.read())
        mail.send(msg)