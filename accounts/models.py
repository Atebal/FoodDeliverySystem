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
    isguestlogin=models.BooleanField(default=False)
    

class Item(models.Model):
    itemName=models.CharField(max_length=100)
    receipe=models.CharField(max_length=200,default='',null=True,blank=True)
    price=models.FloatField(default=0)
    image=models.ImageField(upload_to="Images")
    totalquantities=models.IntegerField(default=0,null=True,blank=True)



class EmployeeOrderHistory(models.Model):
    username=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    itemname=models.ForeignKey(Item,on_delete=models.SET_NULL,null=True,blank=True)
    Quantity=models.IntegerField(default=0)
    price=models.FloatField(default=0)
    transactiondate=models.DateTimeField(auto_now_add=True, null=True,blank=True)

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
    isplacedbyadmin=models.BooleanField(default=False)

class TodaysMenu(models.Model):
    itemName=models.CharField(max_length=100)
    receipe=models.CharField(max_length=200,default='',null=True,blank=True)
    price=models.FloatField(default=0)
    image=models.ImageField(upload_to="Images")
    totalquantities=models.IntegerField(default=0,null=True,blank=True)




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
   

def assignpermission():
    tblobj=[Employee,Item,EmployeeOrderHistory,Payment,AddressTable,Transactions,orders,User]
    notEmployeepermissions=['delete_employee','delete_item','add_item','delete_employeeorderhistory','delete_payment','delete_transactions','delete_user','delete_addresstable',
                            'change_item','change_employeeorderhistory','change_payment','change_transactions','change_user']
    
    admins_group= Group.objects.get(name='CMSAdmin')
    employee_group=Group.objects.get(name='CMSEmployee')
    isEmployee=True
    if(isEmployee):
        for obj in tblobj:
            content_type=ContentType.objects.get_for_model(obj)
            obj_permission=Permission.objects.filter(content_type=content_type)
            for perm in obj_permission:
                if perm.codename not in notEmployeepermissions:
                    print("adding permission Employee"+ perm.codename)
                    employee_group.permissions.add(perm)
                    employee_group.save()
    else:
        for obj in tblobj:
            content_type=ContentType.objects.get_for_model(obj)
            obj_permission=Permission.objects.filter(content_type=content_type)
            for perm in obj_permission:
                    print("Admin adding permission"+ perm.codename)
                    admins_group.permissions.add(perm)
                    admins_group.save() 
                      
                    
    

def assignGroups(username,isEmployee):
    user = User.objects.get(username=username)
    CMSAdmin = Group.objects.get(name="CMSAdmin")
    CMSEmployee=Group.objects.get(name="CMSEmployee")
    if(isEmployee==True):
        CMSEmployee.user_set.add(user)
        CMSEmployee.save()
    else:
        CMSAdmin.user_set.add(user)
        CMSAdmin.save()

#check if user in group
#user = User.objects.get(username="admin")
#group = Group.objects.get(name="CMSAdmin")
#is_member = group in user.groups.all()
# Group.objects.get(name="CMSEmployee").permissions.all()
# permissions=Permission.objects.get(codename="add_item")
# grp.permissions.remove(permissions)
 #grp=Group.objects.get(name="CMSEmployee")  

'''
--Add user to the group
user = User.objects.get(username="username")
group = Group.objects.get(name="group_name")
group.user_set.add(user)
group.save()

--get permissions of the user
user = User.objects.get(username="username")
permissions = user.user_permissions.all()
for permission in permissions:
    print(permission)
    
'''

def getusergroups():
    users = User.objects.all()

# Loop through each user
    for user in users:

    # Get the group names associated with the user
        group_names = [group.name for group in user.groups.all()]

        # Print the group names
        print(user,group_names)

def deleteGroups():
    groupname=["CMSAdmin","CMSEmployee"]
    for grp in groupname:
        Group.objects.get(name=grp).delete()



