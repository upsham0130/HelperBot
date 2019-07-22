from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("WhatsappBot Data").sheet1
data = sheet.get_all_records()
row = sheet.col_values(1)
pprint(row)

app = Flask(__name__)

@app.route("/")
def default():
    return ""

@app.route("/sms", methods=['POST'])
def sms_reply():
    # Fetch message
    getImage = request.form.get('NumMedia')
    getUrl = request.form.get('MediaUrl{idx}')

    # Create reply
    resp = MessagingResponse()
   # urlresp = MessagingResponse()
    
    if getImage != "0":
        resp.message(getUrl)
        #urlresp.message(getUrl)
    else:
        resp.message("I got a text")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
