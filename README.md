# Visitors Count

[Visitors Count!](https://www.outdoorrd.org/community/visitorscount/) is a community science program that asks visitors to contribute information about their recreation experiences on public lands.  Participants exchange text messages with a friendly chatbot named Vic that interacts with people while they are visiting parks and public lands.  

This repository contains software for running Vic chatbots, as well as helper scripts for working with resulting data.  Vic was created by the [Outdoor R&D Lab at University of Washington](https://www.outdoorrd.org).

## Overview of VisitorsCount

Community science participants are recruited by posting a sign that encourages visitors to vountarily report information to Vic the chatbot by sending a text message to a specific phone number.  The question that visitors are prompted with on the sign is called the "hook question" within the app.  

See [*A text-messaging chatbot to support outdoor recreation monitoring through community science*](https://doi.org/10.1016/j.diggeo.2023.100059) and the [Deploying Vic](https://www.outdoorrd.org/community/visitorscount/vic_pro/) website for more information about VisitorsCount! and previous projects.  

## Deploying the Vic app

Deploying vic requires some ability to use a computing instance, a webserver (eg, Apache), python, and flask.  There are five steps, as follows.

1. Clone this repository to a cloud instance.  The app requires a web server and Python 2.7 with the packages listed in [requirements.txt](app/requirements.txt).

2. Modify the app to suit your needs, including:
  * insert questions into `app/vic_questions.py`,
  * edit `app/vic.py` to suit your usage of `vic_questions.py`, and
  * configure the app to listen on an unused port (default is 5000).

3. Launch the app.  For example: `nohup python vic.py >> vic.log &`.

4. Create a web-root folder and virtualhost proxy that will pass incoming http requests to the app's local port.  For example, with an apache webserver, proxies might go in `etc/apache2/sites-available/000-default.conf` or `/etc/httpd/conf.d/virtualhosts.conf`.  Then restart the webserver.

5. Use a service such as Twilio to handle text messages.  Purchase phone number(s) and configure the webhook URL from Step 4.

## Vic data

Incoming and outgoing SMS data are stored locally as .json dictionaries.  The app writes to three files:
  * a **raw** dump of incoming data objects
  * **incoming** data objects with additional metadata, such as length of time since a message was exchanged with the same user
  * **outgoing** text messages

## Citation

If you use this software, please cite the journal article provided in the [CITATION.cff](CITATION.cff) file.

```
@article{Lia_2023_DGS,
author = {Lia, Emmi H. and Derrien, Monika M. and Winder, Sama G. and White, Eric M. and Wood, Spencer A.},
title = {{A text-messaging chatbot to support outdoor recreation monitoring through community science}},
journal = {Digital Geography and Society},
year = {2023},
pages = {100059},
volume = {5},
doi = {10.1016/j.diggeo.2023.100059}
}
```
