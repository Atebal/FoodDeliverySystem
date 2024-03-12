from django.shortcuts import render,redirect
from accounts.models import *
import json
from django.http import HttpResponseBadRequest,JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import DataSerializer


# Create your views here.

def fooditems(request):
    userid=request.user.id
    items=Item.objects.filter(totalquantities__gt=0).all()
    cartcount=0

    user=Employee.objects.filter(isguestlogin=True).values('username')
   
    if user.exists():
         userid=user[0]['username']

    orderscount = orders.objects.filter(Q(username=userid) & Q(paymentstatus='initiated')).values('itemquantity')

    for ordercnt in  orderscount:
           cartcount= ordercnt['itemquantity'] + cartcount  

    context={'items':items,'cartcount':cartcount}
     
    return render(request,"food.html",context)

def searchfood(request):
    queryset=Item.objects.all()
    queryset=queryset.filter(itemName__icontains=request.GET.get('search'))
    context={'items':queryset}
    return render(request,"food.html",context)


def foodmenu(request):
     items=Item.objects.filter(totalquantities__gt=0).all()
     cartcount=0
     userid=request.user.id
     user=Employee.objects.filter(isguestlogin=True).values('username')
   
     if user.exists():
         userid=user[0]['username']

     orderscount=orders.objects.filter(username=userid,paymentstatus='initiated').values('itemquantity')
     for ordercnt in  orderscount:
           cartcount= ordercnt['itemquantity'] + cartcount  

     context={'items':items,'cartcount':cartcount}
     return render(request,"todaysmenu.html",context)

def getitemdetails(request):
    query_string=request.GET
    id=query_string['id']
    #itemid=json.loads(query_string)
    item=Item.objects.get(id=id)
    
    context={'item':item}
    
    return render(request,"clickedfooditem.html",context)

@login_required(login_url='/login/')
def itemcart(request):
    userid=request.user.id
    user=Employee.objects.filter(isguestlogin=True).values('username')
    if user.exists():
          userid=user[0]['username']
          username=User.objects.filter(id=userid)

       
    order_items = orders.objects.filter(username=userid,incart=True).select_related('receipeid').values(
                                    'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                    'itemquantity','receipeid','orderid','receipeid__id')
    address=AddressTable.objects.filter(username=userid).values('street','district','state')
    ordtotal=0
    total=0
    for ord in order_items:
        ordtotal += (ord['itemquantity'] * ord['receipeid__price'])
    
    total=(ordtotal*0.2) + ordtotal    
    context={'items':order_items,'subtotal':ordtotal,'total':total,'address':address}
    
    return render(request,"itemcart.html",context)

@login_required(login_url="/login/")
def checkout(request):
    if request.method=='POST':
     username=request.user
     userid=request.user.id
     data=request.POST
     total=data.get('total')
     receipe=json.loads(data.get('receipe'))
     ordersdata=json.loads(data.get('orders'))
     user=Employee.objects.filter(isguestlogin=True).values('username')
     if user.exists():
          userid=user[0]['username']
          
    ordercheckout(ordersdata)
    updatepbalance(userid,total)
    updatetransactions(userid,total)
    employeehistory(userid,receipe)
    updateitemsquantity(receipe)
    return JsonResponse({'message':'order placed'},safe=False)
   

#helper method for checkout to save the records
def ordercheckout(ordersdata):
      for ord in ordersdata:
         orderid=ord.get('orderid')
         qty=ord.get('itemquantity')
         orders.objects.filter(orderid=orderid).update(itemquantity=qty,incart=False,paymentstatus='completed')
     
   
 #helper function to update item quantity 

#helper method for checkout to update quantity
def updateitemsquantity(receipe):
    totalquantities=0
    for it in receipe:
        totalquantities=int(it.get('quantity'))-totalquantities
        Item.objects.filter(id=it.get('receipeid')).update(totalquantities=totalquantities)
        totalquantities=0
    

#helper function for employee transactios  entry in transations table
def updatetransactions(username,total):
    trans=Transactions.objects.create(
        username=User.objects.get(id=username),
        amount=total,
        transactype='debit'
        )
    trans.save()
def updatepbalance(userid,total):
    
        paymnt=Payment.objects.filter(username=userid).values('balance')
        existingbalance=paymnt[0]['balance']
        newbal=existingbalance-int(total)
        Payment.objects.filter(username=userid).update(balance=newbal)
     
#helper function for employee to record hitory of employee
def employeehistory(username,receipe):
     for rec in receipe:
               
        emph= EmployeeOrderHistory.objects.create(
            username=User.objects.get(id=username),
            itemname=Item.objects.get(id=rec.get('receipeid')),
            Quantity=rec.get('quantity'),
            price=rec.get('price')
        )
        emph.save()
   
#add user selected food receipe
@login_required(login_url="/login/")
def addordersdetail(request):
    
    if request.method=="POST":
        username=request.user
        userid= request.user.id      
        receipeid=request.POST.get('id')
        qty=request.POST.get('itemquantity')
        
        user=Employee.objects.filter(isguestlogin=True).values('username')
        
        if user.exists():
           userid=user[0]['username']
           username=User.objects.filter(id=userid)
        
        orderplaced(receipeid,qty,userid)
        cartcount=carcount(userid)
        return JsonResponse({'message':'order added','cartcount':cartcount},safe=False)

@login_required(login_url="/login/")
def deletecartitem(request):
   
   orderid=request.GET.get('orderid')
   currentuser=request.user
   #orders.objects.filter(orderid=orderid).delete()
   orders.objects.filter(orderid=orderid).delete()
       
   return JsonResponse({'message':'item deleted'},safe=False)
    
  

# add receipe details inserted by admin
@login_required(login_url="/login/")
def addfooditem(request):
    if request.method=="POST":
        itemName=request.POST.get('itemName')
        receipe=request.POST.get('receipe')
        price=request.POST.get('price')
        image= request.FILES.get('image')
        totalquantities=request.POST.get('totalquantities')
        item=Item.objects.create(
            itemName=itemName,
            receipe=receipe,
            price=price,
            image=image,
            totalquantities=totalquantities
        )

        item.save()
        return render(request,"addreceipe.html")
    return render(request,"addreceipe.html")

@login_required
def updatereceipe(request):
    if request.method=="POST":
        itemName=request.POST.get('itemName')
        receipe=request.POST.get('receipe')
        price=request.POST.get('price')
        image= request.FILES.get('re_image')
        item=Item.objects.filter('itemName').update(
            receipe=receipe,
            price=price,
            image=image
        )
        return redirect('/')
    return redirect('/')


#helper function to saving the the orders
def orderplaced(receipeid,qty,userid):
        
       
        uname=User.objects.get(id=userid)
        receipe=Item.objects.get(id=receipeid)
        order=orders.objects.create(
            username=uname,
            receipeid=receipe,
            itemquantity=qty,
            incart=True,
            paymentstatus='initiated',
            
        )
        order.save()

#helper function to get the cartcount
def carcount(userid):
     cartcount=0
     
     orderscount=orders.objects.filter(username=userid,paymentstatus='initiated').values('itemquantity')
     for ordercnt in  orderscount:
           cartcount= ordercnt['itemquantity'] + cartcount
     return cartcount

 #helper function to get the details of orders in cart   
def getitemsincart(username):
     username=User.objects.filter(username=username).values('id')
     userid=username[0]['id']
     order_items = orders.objects.filter(username=userid,paymentstatus='initiated').select_related('receipeid').values(
                                'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                'itemquantity','receipeid')
     return order_items


def getallrecepieslist(request):
     items=Item.objects.all()
     context={'items':items}
     return render(request,"recepies.html",context)

def getreceipedetails(request):
    
    id=request.GET.get('id')
        
    queryset=Item.objects.filter(id=id)
    
    context={'items':queryset}
    
    return render(request,"updatereceipe.html",context)


def updatereceipe(request):
    if request.method=='POST':
        id=request.POST.get('id')
        itemName=request.POST.get('itemName')
        receipe=request.POST.get('receipe')
        price=request.POST.get('price')
        totalquantities=request.POST.get('totalquantities')
        

        Item.objects.filter(id=id).update(
          itemName=itemName,
          receipe=receipe,
          price=price,
          totalquantities=totalquantities,
          
        )

    items=Item.objects.all()
    context={'items':items}
    return render(request,"recepies.html",context)


def deletereceipe(request):
    if request.method=='POST':
        id=request.POST.get('id')
        Item.objects.filter(id=id).delete()
        items=Item.objects.all()
        context={'items':items}
        return render(request,"recepies.html",context) 

def whatstoday(request):
     items=Item.objects.all()
     context={'items':items}
     return render(request,"itemoftheday.html",context)

def createtodaylist(request):
    if request.method=="POST":
        id=request.POST.get('id')
        itemslist=json.loads(request.POST.get('items'))
        TodaysMenu.objects.all().delete()
        for lst in itemslist:
            id=lst['id']
            itemdetails=Item.objects.filter(id=id)
            objtd=TodaysMenu.objects.create(
                itemName=itemdetails[0].itemName,
                receipe=itemdetails[0].receipe,
                price=itemdetails[0].price,
                image=itemdetails[0].image,
                totalquantities=lst['totalquantities']
            )
            objtd.save() 
        items=TodaysMenu.objects.all()
        context={'items':items}
        return render(request,"admintodayitemlist.html",context)
    
def whatstodaylist(request):
    items=TodaysMenu.objects.all()
    context={'items':items}
    return render(request,"admintodayitemlist.html",context)

def whatstodaylistpublic(request):
    items=TodaysMenu.objects.all()
    context={'items':items}
    return render(request,"todaysmenu.html",context)


# Create your views here.
@api_view(['GET'])
def getallrecepies(request):
    items = Item.objects.all()
    serializer = DataSerializer(items, many=True)
    return Response(serializer.data)
    