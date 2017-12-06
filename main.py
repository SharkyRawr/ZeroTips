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

def handle_comment(comment):
    cid = comment.fullname

    # Check if we need to handle this comment
    ta = TipAction.objects.filter(reddit_id=cid).first()
    if ta is not None:
        logger.info("%s already handled", cid)
        return
    
    parts = re.split(r'\s+', comment.body)
    # for example: ['/u/ZeroTips', '/u/vmp32k', '1337', 'nyan']
    
    tipfrom = normname(str(comment.author))
    tipto = normname(parts[1])
    amount = parts[2] 
    currency = parts[3]

    sender = User.objects.filter(name=tipfrom).first()
    if sender is None:
        sender = User(name=tipfrom)
    sender.save()

    recipient = User.objects.filter(name=tipto).first()
    if recipient is None:
        recipient = User(name=tipto)
    recipient.save()

    ta = TipAction(reddit_id=cid, sender=sender, recipient=recipient, amount=amount, currency=currency)

    if sender == recipient:
        ta.state = TipState.Invalid

    ta.save()
    logger.info(str(ta))
    return True

def handle_message(message):
    body = message.body
    
    if body == "help":
        message.reply("Hey there, this bot is still under development. Give me a few days to hammer out the details (like this help message). <3");
        return True

    words = re.split(r'\s+', comment.body)
    
    if words[0] == 'address':
        addr = words[1]
        user = User.find_by_user_addr(message.author.name, addr)

        try:
            if user is None:
                user = User(name=message.author.name)
            user.tipaddress = addr
            user.save()
        except Exception as ex:
            logger.error("UserCreate exception! %s", ex)
            return False

        message.reply("Your tip-address has been set to: " + addr)
        return True


    return False

def main():
    handled_items = []

    for item in reddit.inbox.unread():
        #print(comment.author, comment.body)

        success = False

        try:
            if isinstance(item, praw.models.Comment):
                success = handle_comment(item)
            elif isinstance(item, praw.models.Message):
                success = handle_message(item)
            else:
                logger.error("No case for unread item of type %s", type(item))
                continue
        except Exception as ex:
            logger.error("Error handling item (%s): %s:%s", item, type(ex), str(ex))

        if success:
            handled_items.append(item)
        else:
            logger.warning("Item not handled! %s", item)

    logger.info("Sucessfully handled %d items.", len(handled_items))
    reddit.inbox.mark_read(handled_items)
        

if __name__ == '__main__':
    main()
