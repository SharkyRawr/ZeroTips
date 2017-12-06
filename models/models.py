from django.db import models

class TipState(object):
	Handled = 'handled'
	Pending = 'pending'
	Invalid = 'invalid'

class AutoTimestampModel(models.Model):
	class Meta:
		abstract = True

	created = models.DateTimeField(auto_now_add=True, blank=True)
	edited = models.DateTimeField(auto_now=True, blank=True)

class User(AutoTimestampModel, models.Model):
	name = models.CharField(max_length=64, unique=True)
	tipaddress = models.CharField(max_length=128, null=True)
	
	@staticmethod
	def find_by_user_addr(name, address):
		u = User.objects.filter(name=name, tipaddress=address).first()
		if u is None:
			u = User(name=name, tipaddress=address)
		return u

class TipAction(AutoTimestampModel, models.Model):
	reddit_id = models.CharField(max_length=32)
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tips_sent")
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tips_received")
	amount = models.DecimalField(max_digits=16, decimal_places=8)
	currency = models.CharField(max_length=8)
	created = models.DateTimeField(auto_now_add=True, blank=True)
	edited = models.DateTimeField(auto_now=True, blank=True)

	STATE_CHOICES = (
		(TipState.Handled, 'handled'),
		(TipState.Invalid, 'invalid'),
		(TipState.Pending, 'pending')
	)
	state = models.CharField(max_length=16, choices=STATE_CHOICES, default=TipState.Pending)

	def __str__(self):
		return "[%s/%s] tip from '%s' to '%s' amount %f %s" % ( 
			self.reddit_id, self.state, self.sender.name, self.recipient.name,
			self.amount, self.currency
		)
