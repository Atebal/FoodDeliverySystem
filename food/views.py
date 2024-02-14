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
      
    order_items = orders.objects.filter(username=userid).select_related('receipeid').values(
                                'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                'itemquantity','receipeid','orderid')
    
    context={'items':order_items}
    
    return render(request,"itemcart.html",context)

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
        item=Item.objects.create(
            itemName=itemName,
            receipe=receipe,
            price=price,
            image=image
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