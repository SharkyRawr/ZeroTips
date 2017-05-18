import settings
import praw
reddit = praw.Reddit(client_id=settings.REDDIT_ID, client_secret=settings.REDDIT_SECRET, user_agent="ZeroTipsPy",
                     username=settings.REDDIT_USERNAME, password=settings.REDDIT_PASSWORD)

import re
# Groups: recipient, amount, currency
re_tip = re.compile(r'\/u\/ZeroTips\s+\/u\/(.+?)\s+(\d+)\s+(.+)')

def main():
    for comment in reddit.inbox.mentions():
        body = comment.body
        m = re_tip.match(body)
        recipient, amount, currency = m.groups()
        print(recipient, amount, currency)

if __name__ == '__main__':
    main()
