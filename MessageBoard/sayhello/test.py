from sayhello import app, db
from sayhello.models import Message


message = Message(name="re", body="111111111111")
db.session.add(message)
db.session.commit()
