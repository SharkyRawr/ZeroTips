from django.db import models

TIPSTATE_HANDLED = 'handled'
TIPSTATE_PENDING = 'pending'
TIPSTATE_INVALID = 'invalid'

class User(models.Model):
	name = models.CharField(max_length=64, unique=True)
	tipaddress = models.CharField(max_length=128, null=True)

class TipAction(models.Model):
	reddit_id = models.CharField(max_length=32)
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tips_sent")
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tips_received")
	amount = models.DecimalField(max_digits=16, decimal_places=8)
	currency = models.CharField(max_length=8)

	STATE_CHOICES = (
		(TIPSTATE_HANDLED, 'handled'),
		(TIPSTATE_INVALID, 'invalid'),
		(TIPSTATE_PENDING, 'pending')
	)
	state = models.CharField(max_length=16, choices=STATE_CHOICES, default=TIPSTATE_PENDING)
