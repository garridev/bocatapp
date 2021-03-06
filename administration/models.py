from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from bocatapp.models import User
from administration.services import CreditCardService
from django.utils.translation import ugettext_lazy as _

alphanumeric = RegexValidator(r'^[\sa-zA-Z]*$', _('Holder name field must be contains letters'))
cvvValidator = RegexValidator(r'^[0-9]{3,4}$', _('CVV must have 3 or 4 digits'))
# Create your models here.

class CreditCard(models.Model):
    holderName = models.CharField(max_length=32, validators=[alphanumeric])
    brandName = models.CharField(max_length=32)
    expireMonth = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    expireYear = models.IntegerField(validators=[MinValueValidator(2017)])
    cvv = models.CharField(validators=[cvvValidator], max_length=4)
    number = models.CharField(max_length=32,validators=[CreditCardService.luhn])
    user = models.ForeignKey(User)
    isDeleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.holderName

class Allergen(models.Model):
    name = models.CharField(max_length=32)
    icon = models.URLField(default="#")
    description = models.CharField(max_length=140)

    def __unicode__(self):
        return self.name
