from log import logger

# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.conf import settings

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from models.models import User, TipAction, TipState


logger.debug("Logging in to reddit user %s ...", settings.REDDIT_USERNAME)
import praw
reddit = praw.Reddit(client_id=settings.REDDIT_ID, client_secret=settings.REDDIT_SECRET, user_agent="ZeroTipsPy",
                     username=settings.REDDIT_USERNAME, password=settings.REDDIT_PASSWORD)

import re
# Groups: recipient, amount, currency
#re_tip = re.compile(r'\/u\/ZeroTips\s+\/u\/(.+?)\s+(\d+)\s+(.+)')
re_mention = re.compile(r'\+\/u\/ZeroTips.*')

def normname(name):
    return re.sub(r'(\/u\/|\s+)', '', name)

def main():
    for comment in reddit.inbox.mentions():
        #print(comment.author, comment.body)

        cid = comment.fullname

        # Check if we need to handle this comment
        ta = TipAction.objects.filter(reddit_id=cid).first()
        if ta is not None:
            logger.info("%s already handled", cid)
            return

        tipfrom = normname(str(comment.author))
        
        parts = re.split(r'\s+', comment.body)
        #print(parts)
        # for example: ['/u/ZeroTips', '/u/vmp32k', '1337', 'nyan']
        
        tipto = normname(parts[1])
        amount = parts[2] 
        currency = parts[3]

        sender = User.objects.filter(name=tipfrom).first()
        if sender is None:
            sender = User(name=tipfrom)
        #print(sender)
        sender.save()

        recipient = User.objects.filter(name=tipto).first()
        if recipient is None:
            recipient = User(name=tipto)
        #print(recipient)
        recipient.save()

        ta = TipAction(reddit_id=cid, sender=sender, recipient=recipient, amount=amount, currency=currency)

        if sender == recipient:
            ta.state = TipState.Invalid

        ta.save()

        logger.info(str(ta))
        

if __name__ == '__main__':
    main()
