from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from flask_sqlalchemy import SQLAlchemy

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("WhatsappBot Data").sheet1
data = sheet.get_all_records()
row = sheet.col_values(1)
pprint(row)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///numbers.db'
db = SQLAlchemy(app)

class NumberTable(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    usernumber = db.Column(db.Integer)
    location = db.Column('location', db.Integer)


@app.route("/")
def default():
    return ""

@app.route("/sms", methods=['POST'])
def sms_reply():
    # Fetch Info
    info = NumberTable.query.all()
    sendNumber = request.values.get("From")

    # Fetch message
    getMedia = int(request.values.get("NumMedia"))
    for idx in range(getMedia):
        getUrl = request.values.get(f'MediaUrl{idx}')
    getMessage = request.values.get("From")

    # Create reply
    resp = MessagingResponse()
    urlresp = MessagingResponse()
    
    if getMedia != 0:
        resp.message(getMessage)

        sheet.update_cell(2, 3, f'=IMAGE(\"{getUrl}\")')
    else:
        resp.message("I got a text")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)