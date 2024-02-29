from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User,Permission
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.db.models import F,Sum
from django.db.models.functions import TruncDate


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
 
def guest_Login_page(request):
    if request.method=="POST":
        username=request.POST.get('username')
        userid=User.objects.filter(username=username).values('id')
        userid=userid[0]['id']
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

def profile(request,id):
   
    queryset=User.objects.filter(id=id).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
            )
    context={'employee':queryset}
    return render(request,"userprofile.html",context)
    
def address(request,id):
    if request.method=="POST":
        street=request.POST.get('street')
        district=request.POST.get('district')
        state=request.POST.get('state')
        user=User.objects.get(id=id)
        address=AddressTable.objects.create(
            username=user,
            street=street,
            district=district,
            state=state
            )
        address.save()
        queryset=User.objects.filter(id=id).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
            )
        context={'employee':queryset}
        return render(request,'profile.html',context)
    return render(request,"address.html")


def adminpanel(request):
    revenue_by_date = EmployeeOrderHistory.objects.annotate(purchasedate=TruncDate('transactiondate')).values('purchasedate').annotate(revenue=Sum(F('price') * F('Quantity'))).order_by('purchasedate')
    ''' revenue = [
        {'purchasedate': item['purchasedate'].strftime('%Y-%m-%d'), 'revenue': item['revenue']}
        for item in revenue_by_date
    ]'''
    salesrevenue=[]
    salesdate=[]

    for r in revenue_by_date:
        salesdate.append(r['purchasedate'].strftime('%Y-%m-%d'))
        salesrevenue.append(r['revenue'])

    context={'salesdate':salesdate,'salesrevenue':salesrevenue}
    return render(request,"admindashboard.html",context)


def displayallusers(request):

    queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance','employee__isguestlogin'
            )
    context={'users':queryset}

    return render(request,'users.html',context)

def payment(request):
    if request.method=="POST":
        username=request.POST.get('username')
        balance=request.POST.get('balance')
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

def editUseradmin(request):
    username=username=request.GET.get('username')
    queryset=User.objects.filter(username=username).values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile'
            )
    
    if request.method=='POST':
        username=request.POST.get('username')
        firstname=request.POST.get('firstname')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        id=User.objects.filter(username=username).values('id')
        Employee.objects.filter(username=id[0]['id']).update(firstname=firstname,last_name=last_name,email=email)
        User.objects.filter(username=username).update(email=email)
        
        queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
            )
        context={'users':queryset}

        return render(request,'users.html',context)
    
    context={'users':queryset}
    return render (request,"edituser.html",context)

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
