from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User,Permission
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.db.models import F,Sum,Count
from django.db.models.functions import TruncDate

from .decorators import group_required


# Create your views here.
def login_page(request):
    
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        

        if not User.objects.filter(username=username).exists():
           # messages.info(request,'Invalid username')
            return JsonResponse({'message':'Invalid username'},safe=False)
        
        user=authenticate(username=username,password=password)

        if user is None:
            #messages.error("Invalid password")
            return JsonResponse({'message':'Invalid password'},safe=False)
        else:
            login(request,user)
            
            return JsonResponse({'message':'Login Success'},safe=False)

    return render(request,"login.html")

def register(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        firstname=request.POST.get('firstname')
        last_name=request.POST.get('last_name')
        mobile=request.POST.get('mobile')

        user=User.objects.filter(username=username)
        if user.exists():
            return JsonResponse({'message':'user already exists'},safe=False)
            
        user=User.objects.create(
                username=username,
                email=email
                    )
        user.set_password(password)
        user.save()
        
        employee=Employee.objects.create(
             username=user,
             email=email,
             firstname=firstname,
             last_name=last_name,
             mobile=mobile

        )
        employee.save()
     
        return JsonResponse({'message':'ok'},safe=False)

    return render(request,"register.html") 

def logoutusr(request):
    logout(request)
    return redirect('/')
 
@login_required
def guest_Login_page(request):
    if request.method=="POST":
        username=request.POST.get('username')
        userid=User.objects.filter(username=username).values('id')
        userid=userid[0]['id']
        alreadygusetlogin=Employee.objects.filter(isguestlogin=True).count()
        if alreadygusetlogin > 0:
           return JsonResponse({'message':'only one guest can login at a time'})
            
        else:
            Employee.objects.filter(username=userid).update(isguestlogin=True)
            queryset=User.objects.all().values(
                'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance','employee__isguestlogin'
                )
            context={'users':queryset}

            return render(request,'users.html',context)

def guest_Logout_page(request):
    if request.method=="POST":
        username=request.POST.get('username')
        userid=User.objects.filter(username=username).values('id')
        userid=userid[0]['id']
        Employee.objects.filter(username=userid).update(isguestlogin=False)
        queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance','employee__isguestlogin'
            )
    context={'users':queryset}

    return render(request,'users.html',context)
 
def updateUserDetailsEmployee(request):
    queryset=User.objects.get(id=id)
    context={'user':queryset}
    return redirect(request,"editemployee.html",context)

def userdashboard(request):
    
    
    return render(request,"Employeehome.html")
    
@login_required
def profile(request):
    
    userid=request.user.id
    queryset=User.objects.filter(id=userid).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile',
            'payment__balance','addresstable__street','addresstable__district','addresstable__state'
            )
    context={'employee':queryset}
    return render(request,"userprofile.html",context)
    
def address(request):
    if request.method=="POST":
        street=request.POST.get('street')
        district=request.POST.get('district')
        state=request.POST.get('state')
        userid=request.user.id
        user=User.objects.get(id=userid)
        address=AddressTable.objects.create(
            username=user,
            street=street,
            district=district,
            state=state
            )
        address.save()
        queryset=User.objects.filter(id=userid).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
            )
        context={'employee':queryset}
        return redirect('/userdashboard/')
    return render(request,"address.html")

@group_required('CMSAdmin')
def adminpanel(request):
    
    revenue_by_date = EmployeeOrderHistory.objects.annotate(purchasedate=TruncDate('transactiondate')).values('username__username','itemname__itemName','purchasedate').annotate(revenue=Sum(F('price') * F('Quantity'))).order_by('purchasedate')
    
    #total users in user Table
    usercount=User.objects.all().count()

    #ordercount per user how many orders are placed by user
    ordercountperuser=EmployeeOrderHistory.objects.annotate(purchasedate=TruncDate('transactiondate')).values('username__username','purchasedate').annotate(ordercount=Count('username'))

    ''' revenue = [
        {'purchasedate': item['purchasedate'].strftime('%Y-%m-%d'), 'revenue': item['revenue']}
        for item in revenue_by_date
    ]'''
    salesrevenue=[]
    salesdate=[]
    usrs=[]
    recepname=[]
    ordercount=[]
    orderuser=[]

    for r in revenue_by_date:
        salesdate.append(r['purchasedate'].strftime('%Y-%m-%d'))
        salesrevenue.append(r['revenue'])
        usrs.append(r['username__username'])
        recepname.append(r['itemname__itemName'])
   
    for ords in ordercountperuser:
        ordercount.append(ords['ordercount'])
        orderuser.append(ords['username__username'])


    context={'usrs':usrs,'salesdate':salesdate,'salesrevenue':salesrevenue,'recepname':recepname,
             'usercount':usercount,'ordercount':ordercount,'orderuser':orderuser}
    return render(request,"admindashboard.html",context)

@group_required('CMSAdmin')
def displayallusers(request):

    queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance','employee__isguestlogin'
            )
    context={'users':queryset}

    return render(request,'users.html',context)

@login_required
def payment(request):
    if request.method=="POST":
        username=request.user.username
        customername=request.POST.get('username')
        balance=request.POST.get('balance')
        if customername!='':
            username=customername

        user=User.objects.get(username=username)
        queryset=User.objects.filter(username=username).values(
            'id','username','payment__balance'
            )
        alreadybalance= queryset[0]['payment__balance']
        id=queryset[0]['id']
        
        if(alreadybalance):
            balance=float(balance)+float(alreadybalance)
            Payment.objects.filter(username=id).update(balance=balance)
            
        
        elif(alreadybalance==None):
            payment=Payment.objects.create(
            username=user,
            balance=float(balance)
            )
            payment.save()
            
        return JsonResponse({'message':'Payment done successfully'},safe=False)

    return render(request,"payment.html")

@group_required('CMSAdmin')
def deleteuser(request):
    if request.method=='POST':
        username=request.POST.get('username')
        user=User.objects.filter(username=username).values('id')
        userid=user[0]['id']
        Employee.objects.filter(username=userid).delete()
        User.objects.filter(username=username).delete()
        queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
            )
        context={'users':queryset}
        #json_response=JsonResponse({'message':'user deleted'})
        return render(request,"users.html",context)
        #return JsonResponse({'message':'user deleted'},safe=False)
    
    return redirect (request,"/adminpanel")

@group_required('CMSAdmin')
def editUseradmin(request):
    username=username=request.GET.get('username')
    queryset=User.objects.filter(username=username).values(
            'username', 'employee__firstname','employee__last_name','employee__email',
            'employee__mobile','addresstable__street','addresstable__district','addresstable__state'
            )
    
    if request.method=='POST':
        username=request.POST.get('username')
        firstname=request.POST.get('firstname')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        street=request.POST.get('street')
        district=request.POST.get('district')
        state=request.POST.get('state')
        id=User.objects.filter(username=username).values('id')
        Employee.objects.filter(username=id[0]['id']).update(firstname=firstname,last_name=last_name,email=email)
        AddressTable.objects.filter(username=id[0]['id']).update(street=street,district=district,state=state)
        User.objects.filter(username=username).update(email=email)
        
        queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','payment__balance',
            'addresstable__street','addresstable__district','addresstable__state'
            )
        context={'users':queryset}

        return render(request,'users.html',context)
    
    context={'users':queryset}
    return render (request,"edituser.html",context)


def editUser(request):
    username=username=request.user.username
    userid=request.user.id
    queryset=User.objects.filter(username=username).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile',
            'addresstable__street','addresstable__district','addresstable__state'
            )
    
    if request.method=='POST':
        username=request.POST.get('username')
        firstname=request.POST.get('firstname')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        street=request.POST.get('street')
        district=request.POST.get('district')
        state=request.POST.get('state')

        id=User.objects.filter(username=username).values('id')
        Employee.objects.filter(username=id[0]['id']).update(firstname=firstname,last_name=last_name,email=email)
        User.objects.filter(username=username).update(email=email)
        AddressTable.objects.filter(username=id[0]['id']).update(street=street,district=district,state=state)
        
        queryset=User.objects.filter(id=userid).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile',
            'payment__balance','addresstable__street','addresstable__district','addresstable__state'
            )
        context={'employee':queryset}

        return render(request,'userprofile.html',context)
    
    context={'users':queryset}
    return render (request,"editemployee.html",context)

@group_required('CMSAdmin')
def assignroles(request):
    if request.method=='POST':
        username=request.POST.get('username')
        isEmploye=request.POST.get('isEmployee')
        isAdmin=request.POST.get('isAdmin')

        if(isEmploye=='true'):
            addusertoroles(username,"CMSEmployee")
           
        if (isAdmin=='true'):
            addusertoroles(username,"CMSAdmin")
                
    usersa=[]
    usersa=  getuserRoles()
    context={'users':usersa}
    return render(request,"userroles.html",context)

@group_required('CMSAdmin')
def removeroles(request):
    if request.method=='POST':
        username=request.POST.get('username')
        isEmployee=request.POST.get('isEmployee')
        isAdmin=request.POST.get('isAdmin')
        if(isEmployee=='true'):
            removeuser(username,'CMSEmployee')
        if(isAdmin=='true'):
            removeuser(username,'CMSAdmin')
    
    usersa=[]
    usersa=  getuserRoles()
       
    context={'users':usersa}
    return render(request,"userroles.html",context)

def userorderHistory(request):
    userid=request.user.id
    queryset=EmployeeOrderHistory.objects.filter(username=userid).values(
            'username__username', 'itemname__itemName','Quantity','price','transactiondate'
            )
    context={'orders':queryset}

    return render(request,'userorderhistory.html',context)

def addusertoroles(username,rolename):
    user = User.objects.get(username=username)
    group = Group.objects.get(name=rolename)
    group.user_set.add(user)
    group.save()

def removeuser(username,rolename):
    # Assuming you already have a group and user defined
            group = Group.objects.get(name=rolename)
            user = User.objects.get(username=username)
            # Remove the user from the group
            group.user_set.remove(user)

def getuserRoles():
    user_groups={}
    usersa=[]
    users = User.objects.all()

     # Loop through each user
    for user in users:

        # Get the group names associated with the user
        group_names = [group.name for group in user.groups.all()]
        user_groups={'username':user,'group':group_names}
        usersa.append(user_groups)
    return usersa

