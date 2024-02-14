from django.shortcuts import render,redirect
from accounts.models import *
import json
from django.http import HttpResponseBadRequest

# Create your views here.

def fooditems(request):
    return render(request,"food.html")

def foodmenu(request):
     items=Item.objects.all()
     context={'items':items}
     return render(request,"todaysmenu.html",context)

def getitemdetails(request):
    query_string=request.GET
    id=query_string['id']
    #itemid=json.loads(query_string)
    item=Item.objects.get(id=id)
    context={'item':item}
         
    return render(request,"clickedfooditem.html",context)


def itemcart(request):
    userid=request.user.id
      
    order_items = orders.objects.filter(username=userid,incart=True).select_related('receipeid').values(
                                'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                'itemquantity','receipeid','orderid','receipeid__id')
    
    ordtotal=0
    total=0
    for ord in order_items:
        ordtotal += (ord['itemquantity'] * ord['receipeid__price'])
    
    total=(ordtotal*0.2) + ordtotal    
    context={'items':order_items,'subtotal':ordtotal,'total':total}
    
    return render(request,"itemcart.html",context)

def checkout(request):
    if request.method=='POST':
     username=request.POST.get('username')
     data=request.POST
     total=data.get('total')
     receipe=json.loads(data.get('receipe'))
     ordersdata=json.loads(data.get('orders'))
    
     for ord in ordersdata:
         orderid=ord.get('orderid')
         qty=ord.get('itemquantity')
         orders.objects.filter(orderid=orderid).update(itemquantity=qty,incart=False,paymentstatus='completed')

    

     trans=Transactions.objects.create(
        username=User.objects.get(username=username),
        amount=total,
        transactype='debit'
        )
     trans.save()
   
    

    for rec in receipe:
               
        emph= EmployeeOrderHistory.objects.create(
            username=User.objects.get(username=username),
            itemname=Item.objects.get(id=rec.get('receipeid')),
            Quantity=rec.get('quantity'),
            price=rec.get('price')
        )
        emph.save()
    totalquantities=0
    for it in receipe:
        totalquantities=int(it.get('quantity'))-totalquantities
       # Item.objects.filter(id=it.rec.get('receipeid')).update(totalquantities=totalquantities)
        totalquantities=0

    return redirect('/')


#add user selected food receipe
def addordersdetail(request):
    if request.method=="POST":
        receipeid=request.POST.get('id')
        qty=request.POST.get('itemquantity')
        username=User.objects.get(id=request.user.id)
        receipe=Item.objects.get(id=receipeid)
        order=orders.objects.create(
            username=username,
            receipeid=receipe,
            itemquantity=qty,
            incart=True,
            paymentstatus='initiated'
        )
        order.save()
    return redirect('/menuitem')

def deletecartitem(request):
   userid=request.user.id
   orderid=request.GET.get('orderid')
   orders.objects.filter(orderid=orderid).delete()
   order_items = orders.objects.filter(username=userid).select_related('receipeid').values(
                                'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                'itemquantity','receipeid')
    
   context={'items':order_items}
    
   return render(request,"itemcart.html",context) 

# add receipe details inserted by admin
def addfooditem(request):
    if request.method=="POST":
        itemName=request.POST.get('itemName')
        receipe=request.POST.get('receipe')
        price=request.POST.get('price')
        image= request.FILES.get('re_image')
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