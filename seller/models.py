from django.db import models
from bocatapp.models import User


# Create your models here.




class Local(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=256)
    address = models.CharField(max_length=55)
    phone = models.CharField(max_length=12)
    photo = models.URLField()
    isActive = models.BooleanField(default=True)
    seller = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=256)
    local = models.ForeignKey(Local)

    def __unicode__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=48)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    ingredients = models.CharField(max_length=256, default="Ingrediente")
    category = models.ManyToManyField(Category)
    picture = models.URLField(default="#")
    local = models.ForeignKey(Local)

    def __unicode__(self):
        return self.name

