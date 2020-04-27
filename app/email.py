
from flask_mail import Mail, Message

def send_ip(app,ipfilename,ipfiledata):

    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_SUPPRESS_SEND": True,
        "MAIL_USERNAME": 'darcylabweb@gmail.com',
        "MAIL_PASSWORD": 'darcylab1'
    }



    app.config.update(mail_settings)
    mail = Mail(app)
    with app.app_context():
        msg = Message(subject="HD_eXplosion test",
                        sender=app.config.get("MAIL_USERNAME"),
                        recipients=["xiaohe.yu86@gmail.com"], # replace with your email for testing
                        body="IP list is attached")
        msg.attach(
            ipfilename,
            'text/csv',
            ipfiledata)
        mail.send(msg)
        mail.send(msg)