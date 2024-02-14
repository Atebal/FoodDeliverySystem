from django.db import models
from django.contrib.auth.models import Group,User,Permission,AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import uuid
 
# Create your models here.


class Employee(models.Model):
    firstname=models.CharField(max_length=100,null=True,blank=True,default='')
    last_name=models.CharField(max_length=100,null=True,blank=True,default='')
    username=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True)
    email=models.EmailField(default='',null=True,blank=True)
    mobile=models.CharField(max_length=10,default='',null=True,blank=True)
    rating=models.FloatField(default=5)
    coupon=models.CharField(max_length=50,null=True,blank=True,default='')
    discount=models.FloatField(default=0.0)
    

class Item(models.Model):
    itemName=models.CharField(max_length=100)
    receipe=models.CharField(max_length=200,default='',null=True,blank=True)
    price=models.FloatField(default=0)
    image=models.ImageField(upload_to="Images")

class EmployeeOrderHistory(models.Model):
    username=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    itemname=models.ForeignKey(Item,on_delete=models.SET_NULL,null=True,blank=True)
    Quantity=models.IntegerField(default=0)
    price=models.FloatField(default=0)

class Payment(models.Model):
    username=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True)
    balance=models.FloatField(default=0)
    transactiondate=models.DateTimeField(auto_now_add=True, blank=True)

class AddressTable(models.Model):
    username=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    street=models.CharField(max_length=100,null=True,blank=True,default='')
    district=models.CharField(max_length=100,null=True,blank=True,default='')
    state=models.CharField(max_length=100,null=True,blank=True,default='')

class Transactions(models.Model):
    username=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    amount=models.FloatField(default=0.0)
    transactype=models.CharField(max_length=20, default='',null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True, blank=True)



choices = [
        ('initiated','initiated'),
        ('inprogress','inprogress'),
        ('completed','completed')
        ]


class orders(models.Model):
    username=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    orderid=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    receipeid=models.ForeignKey(Item,on_delete=models.SET_NULL,default=0,null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True, blank=True)
    incart=models.BooleanField(default=False)
    paymentstatus=models.CharField(choices=choices,max_length=20,default='initiated')
    itemquantity=models.IntegerField(default=0)






def displayEmployeeInfo():
    content_type=ContentType.objects.get_for_model(Employee)
    employee_permission=Permission.objects.filter(content_type=content_type)
    print([perm.codename for perm in employee_permission])
    emp=Employee.objects.all()
    for e in emp:
         print(e.username)
       
           


def createGroups():
    admins_group=Group(name="CMSAdmin")
    admins_group.save()  
    employee_group=Group(name="CMSEmployee")
    employee_group.save()  
    
    content_type=ContentType.objects.get_for_model(Employee)
    employee_permission=Permission.objects.filter(content_type=content_type)
    
    for perm in employee_permission:
        admins_group.permissions.add(perm)
        if perm.codename=="view_employee":
            employee_group.permissions.add(perm)
    admins_group.save() 
    employee_group.save()  
    
def assignGroups():
    pass

def deleteGroups():
    groupname=["CMSAdmin","CMSEmployee"]
    for grp in groupname:
        Group.objects.get(name=grp).delete()



