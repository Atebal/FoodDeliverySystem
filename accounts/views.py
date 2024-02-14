from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User,Permission
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def login_page(request):
    
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        

        if not User.objects.filter(username=username).exists():
            messages.info(request,'Invalid username')
            return redirect('/register/')
        
        user=authenticate(username=username,password=password)

        if user is None:
            messages.error("Invalid password")
            #return redirect('/login/')
        else:
            login(request,user)
            return redirect('/')

    return render(request,"login.html")

def register(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        firstname=request.POST.get('firstname')
        last_name=request.POST.get('last_name')
        mobile=request.POST.get('mobile')

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

       
        messages.info(request,'Account created Successfully')
        return redirect('/')

    return render(request,"register.html")
    
def dipslayUsers(request):
    return render(request,"users.html")

def logoutusr(request):
    logout(request)
    return redirect('/')
    

def assign_userRoleadmin(request):
    cmstables=[User,Employee,Item,EmployeeOrderHistory,Payment,AddressTable]
    for tbls in cmstables:
        content_type=ContentType.objects.get_for_model(tbls)
        employee_permission=Permission.objects.filter(content_type=content_type)
        print([perm.codename for perm in employee_permission])
    
   

def displayEmployeeInfo(request):
    content_type=ContentType.objects.get_for_model(Employee)
    employee_permission=Permission.objects.filter(content_type=content_type)
    print([perm.codename for perm in employee_permission])

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
    if request.method=="POST":
        pass

    return render(request,"admindashboard.html")


def displayallusers(request):

    queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
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
        User.objects.filter(username=username).delete()
        queryset=User.objects.all().values(
            'username', 'employee__firstname','employee__last_name','employee__email','employee__mobile','addresstable__state','payment__balance'
            )
        context={'users':queryset}
        return render(request,"users.html",context)
        #return JsonResponse({'message':'user deleted successfully'},safe=False)
    
    return redirect (request,"/adminpanel")

def editUseradmin(request):
    if request.method=='POST':
        username=request.POST.get('username')
        firstname=request.POST.get('firstname')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        id=User.objects.filter(usernam=username).values('id')
        Employee.objects.filter(username=id).update(firstname=firstname,last_name=last_name,email=email)
        User.objects.filter(username=username).update(email=email)
        users=User.objects.all()
        context={'users':users}
        return render(request,"users.html",context)
    return redirect (request,"/adminpanel")


