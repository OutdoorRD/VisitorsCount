
# Vic
#
# Listens for incoming SMS messages with a webhook
#  from a service such Twilio that handle the text messaging
#  using flask for the WSGI app, on specified port
# 
# This app writes three .json files with incoming out outgoing sms data
#
# see https://github.com/OutdoorRD/VisitorsCount for more information
#

from flask import Flask, request, redirect, session
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from collections import OrderedDict
import csv
import json

dddd = datetime.today().strftime('%Y%m%d')

# The session object makes use of a secret key.
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
app = Flask(__name__)
app.config.from_object(__name__)

# Potential questions
# imported from accompanying questions file
from vic_questions import qtrip
from vic_questions import qcond
from vic_questions import qonce
from vic_questions import qrest

# create a single dict of all potential responses
qalls = qtrip.copy();  qalls.update(qcond);  qalls.update(qonce);  qalls.update(qrest);

# Cache data and respond to sms...
@app.route("/", methods=['GET', 'POST'])
def sms():
  # for debugging in python outside of flask session:
  #with app.test_request_context():

  # Dump incoming sms into a file...
  # Build data object
  draw = {}
  draw["messageid"] = request.values.get('MessageSid')
  draw['from'] = request.values.get('From')
  draw['to'] = request.values.get('To')
  draw['body'] = request.values.get('Body')
  draw['nummed'] = request.values.get('NumMedia')
  draw['fromzip'] = request.values.get('FromZip')
  draw['accountid'] = request.values.get('AccountSid')
  # plus current datetime
  now = datetime.now()
  draw['datetime'] = now.strftime("%Y-%m-%d %H:%M:%S")

  # Touch .json data caches in case they don't already exist
  rawinfile = 'vic_raw_' + draw['to'][1:] + '.json'              # raw incoming SMSs
  incomingfile = 'vic_incoming_' + draw['to'][1:] + '.json'      # incoming SMSs
  outgoingfile = 'vic_outgoing_' + draw['to'][1:] + '.json'      # outgoing SMSs
  jnk = open(rawinfile, 'a')
  jnk = open(incomingfile, 'a')
  jnk = open(outgoingfile, 'a')

  # Write raw data
  with open(rawinfile, 'a') as f:
    json.dump(draw, f)
    f.write('\n')

  # Then it's question and answer time...
  # Has this person texted us before (from this site)?  and when?  and what?
  repeater = "false"        # have we seen this person before?
  prevanswer = []           # a set of IDs all previously ANSWERED questions
  todayanswer = []          # a set of IDs all ANSWERED questions TODAY
  lastanswer = "na"         # ID of the LAST (most recently) ANSWERED question
  lastsmsdt = "na"          # datetime of last answered question
  lastsmsmns = "na"         # minutes bp of last answered question
  lastquestion = "na"       # ID of the LAST (most recently) ASKED question
  sendresponse = "true"     # an optional flag to not send a response
  lastsmscutoff = 60        # set the threshold minutes before giving up on calling it the same convo

  # Comb INCOMING texts for this person's last, prev, and today's answers
  file = open(incomingfile, 'r')
  for line in file:
    jsline = json.loads(line)
    # if sms is from the right user...
    if jsline['from'] == draw['from']:
      repeater = "true"
      prevanswer.append(jsline['lastquestion'])
      # if sms was most recent found so far...
      if lastsmsdt == "na" or datetime.strptime(jsline['datetime'], "%Y-%m-%d %H:%M:%S") > lastsmsdt:
        lastsmsdt = datetime.strptime(jsline['datetime'], "%Y-%m-%d %H:%M:%S")
        lastsmsmns = (datetime.now() - lastsmsdt).seconds/60
        lastanswer = jsline['lastquestion']
      # if sms was today...
      if lastsmsdt.date()==datetime.now().date():
        todayanswer.append(jsline['lastquestion'])

  # Comb OUTGOING texts for the last question sent to this person (the one they might be answering now)
  if repeater == "true":
    mostrecentdate = datetime.strptime("1900-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")  # initialize with an old date
    file = open(outgoingfile, 'r')
    for line in file:
      jsline = json.loads(line)
      # if sms is from the right user and most recent text we've seen so far...
      if jsline['to'] == draw['from'] and datetime.strptime(jsline['datetime'], "%Y-%m-%d %H:%M:%S") > mostrecentdate:
        mostrecentdate = datetime.strptime(jsline['datetime'], "%Y-%m-%d %H:%M:%S")
        lastquestion = jsline['askquestionID']

  # Decide questions to ask (based on any earlier conversations)...
  # Scenario X: never seen this person before
  # assume its responding to the hook question
  # send them all Qs, and prepend the hello message
  if repeater == "false":
    lastquestion = "HookQuest"
    qs = qtrip.keys() + qonce.keys()
    qs = ['Hello'] + qs

  # Scenario X: we know this person, but this is their first message today
  # assume its an answer to the hook question
  # send them all tripQs and unanswered onceQs, and prepend the hello message
  elif repeater == 'true' and len(todayanswer) == 0:
    lastquestion = 'HookQuest'
    qs = qtrip.keys() + [x for x in qonce.keys() if x not in prevanswer]
    qs = ['Hello'] + qs

  # Scenario X: we know this person, last question was TQ3, they answered xxxxx
  # they should receive conditional question CQ1
  elif repeater == 'true' and len(todayanswer) > 0 and lastquestion == 'TQ3' and 'xxxxx' in draw['body'].lower():
    qs = qcond.keys() + qtrip.keys() + [x for x in qonce.keys() if x not in prevanswer]

  # Scenario X: we know this person, last question was TQ4, and they answered xxxxx
  # they should receive conditional question CQ2
  elif repeater == 'true' and len(todayanswer) > 0 and lastquestion == 'TQ4' and 'xxxxx' in draw['body'].lower():
    qs = qcond.keys() + qtrip.keys() + [x for x in qonce.keys() if x not in prevanswer]

  # Scenario X: we know this person, they answered all Qs today, received bubye message
  # store their data but do not respond
  elif repeater == 'true' and len(todayanswer) > 0 and lastquestion == 'Goodbye':
    qs = []
    sendresponse = 'false'

  # Scenario X: we know this person, they answered some Qs today, within last XX mins
  # assume this is response to last Q, send them all unanswered tripQs and onceQs
  # qs adds lastquestion bc we assume they're responding to it
  # (and it's not in today nor prevanswer from incoming file)
  elif repeater == 'true' and len(todayanswer) > 0 and lastsmsmns <= lastsmscutoff:
    qs = [x for x in qtrip.keys() if x not in todayanswer + [lastquestion]] + [x for x in qonce.keys() if x not in prevanswer + [lastquestion]]

  # Scenario X: we know this person, they answered some Qs today, but not within last XX mins
  # dont assume to know why they're texting, send them any unanswered onceQs (but not unanswered tripQs)
  # don't add lastquestion bc we don't know that's the topic; be conservative and re-ask the question.
  elif repeater == 'true' and len(todayanswer) > 0 and lastsmsmns >= lastsmscutoff:
    qs = [x for x in qonce.keys() if x not in prevanswer]

  # yes, the qs= lines would be cleaner as diffs of sets, but sets don't preserve the question order

  # if they've exhausted all our questions, then respond politely
  if len(qs) == 0:
    qs = ['Goodbye']
  
  # Create response(s)...
  # get the response id and text of first response question
  # if it's the hello message, concat with question 2 (the first actual q)
  # and identify it with the question 2 ID
  if qs[0] == "Hello":
    respid = qs[1]
    resptx = qalls.get(qs[0]) + " " + qalls.get(qs[1])
  else:
    respid = qs[0]
    resptx = qalls.get(qs[0])

  # Dump incoming sms with additional metadata...
  # Build obect of data to store
  dinc = draw
  # plus 
  dinc['repeater'] = repeater
  dinc['lastanswer'] = lastanswer
  dinc['lastsmsmns'] = lastsmsmns
  dinc['lastquestion'] = lastquestion
  dinc['sendresponse'] = sendresponse
  dinc['lastsmscutoff'] = lastsmscutoff
  if lastsmsdt != 'na':
    dinc['lastsmsdatetime'] = datetime.strftime(lastsmsdt, "%Y-%m-%d %H:%M:%S")
  else:
    dinc['lastsmsdatetime'] = lastsmsdt
  # Write data
  with open('countrespond2visitorsurvey_incoming_' + request.values.get('To')[1:] + '.json', 'a') as f:
    json.dump(dinc, f)
    f.write('\n')

  # Dump outgoing response in data file...
  # Build obect of outgoing sms to store
  dres = {}
  # grab data from sender
  # yes, from and to are crossed here because it's an outgoing message using incoming from and to vars
  dres['from'] = request.values.get('To')
  dres['to'] = request.values.get('From')
  dres['askquestionID'] = respid
  dres['askquestionLong'] = resptx
  # plus current datetime
  now = datetime.now()
  dres['datetime'] = now.strftime("%Y-%m-%d %H:%M:%S")
  # Write data
  if sendresponse == 'true':
    with open('countrespond2visitorsurvey_outgoing_' + request.values.get('To')[1:] + '.json', 'a') as f:
      json.dump(dres, f)
      f.write('\n')

  # Send response...
  resp = MessagingResponse()
  if sendresponse == 'true':
    resp.message(body=resptx)
  return str(resp)


# Do it
if __name__ == "__main__":
  app.run(port=5000, debug=True)


