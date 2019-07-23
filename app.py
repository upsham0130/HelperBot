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
    fromVar = request.values.get("From")
    sendNum = int(fromVar[11:21])
    getMedia = int(request.values.get("NumMedia"))
    for idx in range(getMedia):
        getUrl = request.values.get(f'MediaUrl{idx}')
    getMessage = request.values.get("Body")
    resp = MessagingResponse()

    # Create Reponse Dictionary
    respDict =	{
        0: "Jay Swaminarayan! Welcome to the Prasang Bot. Please start by telling me the name of the karyakar involved in the prasang:",
        1: "And where did the prasang take place?",
        2: "Great! Now tell me the prasang",
        3: "Amazing! Do you have any pictures of this karyakar? If no type \"no\"",
        4: "Thank you for submitting your prasang! To send another type \"/start\""
    }

    # Search DB for Number
    numberQuery = NumberTable.query.filter_by(usernumber=sendNum).first()

    # Add Info If Record Does Not Exist
    if numberQuery == None and getMessage == '/start':
        newNumb = NumberTable(usernumber=sendNum, location=0)
        db.session.add(newNumb)
        db.session.commit()
        numberQuery = NumberTable.query.filter_by(usernumber=sendNum).first()
        Id = numberQuery.index
        newRow = ["","","","",Id]
        sheet.insert_row(newRow, len(data)+2)
        resp.message(respDict[0])
    elif numberQuery != None:
        Id = numberQuery.index
        loc = numberQuery.location

        if loc == 0: 
            sheet.update_cell(Id+1, 1, getMessage)
            resp.message(respDict[loc+1])
            numberQuery.location = 1
            db.session.commit()
        elif loc == 1: 
            sheet.update_cell(Id+1, 2, getMessage)
            resp.message(respDict[loc+1])
            numberQuery.location = 2
            db.session.commit()
        elif loc == 2: 
            sheet.update_cell(Id+1, 3, getMessage)
            resp.message(respDict[loc+1])
            numberQuery.location = 3
            db.session.commit()
        elif loc == 3: 
            if getMedia != 0:
                resp.message(respDict[loc+1])
                sheet.update_cell(Id+1, 4, f'=IMAGE(\"{getUrl}\")')
                numberQuery.usernumber = 0
                db.session.commit()
            elif getMessage.lower() == "no":
                resp.message(respDict[loc+1])
                sheet.update_cell(Id+1, 4, 'None Provided')
                numberQuery.usernumber = 0
                db.session.commit()
            else:
                resp.message("Sorry, I didn't get that. Please try again")
    else:
        resp.message("To start a new prasanf type \"/start\"")

    
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)