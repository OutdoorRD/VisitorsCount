
# This file specifies text messages to be sent by the vic.py app
# containing four dictionaries named qtrip, qcond, qonce, and qrest
# all four dictionaries are required

from collections import OrderedDict

# Within each dictionary, questions are listed in the order to be delivered
# 
# This file does not include the "hook question" that is posted
# on the sign that invites volunteers to partcipate
# 
# "Trip" questions are asked to every user every time they message the bot
# "Once" questions are only asked if users have never answered previously
# "Conditional" questions are asked dependent on answers to a previous question
# The "Rest" dictionary contains two entries:
# the first and last messages to be sent
#
qtrip = OrderedDict([
         ('TQ1','Question text'),
         ('TQ2','Question text'),
         ('TQ3','Question text'),
         ('TQ4','Question text')
         ])

qcond = OrderedDict([
         # vic.py accepts two question here
         # note that actions in vic.py are definted by question ID keys
         # so this feature requires some customization in vic.py
         ('CQ1','Question text'),   # conditional on TQ3
         ('CQ1','Question text')    # conditional on TQ4
         ])

qonce = OrderedDict([
         ('OQ1','Question text'),
         ('OQ2','Question text')
         ])

qrest = OrderedDict([
         ('Hello','A hello message, including information about the study, consent to participate, etc'),
         ('Goodbye','A goodbye message, including thanks for participating, where to find more information, etc')
         ])
