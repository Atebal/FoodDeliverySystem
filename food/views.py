from django.shortcuts import render,redirect
from accounts.models import *
import json
from django.http import HttpResponseBadRequest,JsonResponse

# Create your views here.

def fooditems(request):
    isAdminplaced=request.COOKIES.get('isAdminplaced')
    employeename=request.COOKIES.get('employeename')
    items=Item.objects.all()
    cartcount=0
    orderscount=orders.objects.filter(username=request.user.id,paymentstatus='initiated').values('itemquantity')
    for ordercnt in  orderscount:
           cartcount= ordercnt['itemquantity'] + cartcount  

    context={'items':items,'cartcount':cartcount}
     
    return render(request,"food.html",context)
    

def foodmenu(request):
     items=Item.objects.all()
     
     cartcount=0
     orderscount=orders.objects.filter(username=request.user.id,paymentstatus='initiated').values('itemquantity')
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

def ordersuccess(request):
    return render(request,"orderplaced.html")

def itemcart(request):
    userid=request.user.id
    isAdminplaced=request.POST.get('isAdminplaced')
    employeename=request.POST.get('employeename')
    

    if(isAdminplaced=='true'):
        employee=User.objects.filter(username=employeename).values('id')
        employeeid=employee[0]['id']
        order_items = orders.objects.filter(username=employeeid,incart=True,isplacedbyadmin=True).select_related('receipeid').values(
                                    'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                    'itemquantity','receipeid','orderid','receipeid__id')
    
    else:
        order_items = orders.objects.filter(username=userid,incart=True,isplacedbyadmin=False).select_related('receipeid').values(
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
     username=request.user
     data=request.POST
     total=data.get('total')
     receipe=json.loads(data.get('receipe'))
     ordersdata=json.loads(data.get('orders'))
     isAdminplaced=request.POST.get('isAdminplaced')
     employeename=request.POST.get('employeename')
    
    if(isAdminplaced=='true'):
        ordercheckout(employeename,total,receipe,ordersdata,True)
        updatetransactions(username,total)
        employeehistory(username,receipe)
        updateitemsquantity(receipe)
    else:
        ordercheckout(username,total,receipe,ordersdata,False)
        updatetransactions(username,total)
        employeehistory(username,receipe)
        updateitemsquantity(receipe)
    return JsonResponse({'message':'order placed'},safe=False)
   

#helper method for checkout to save the records
def ordercheckout(username,total,receipe,ordersdata,isAdminplaced):
      for ord in ordersdata:
         orderid=ord.get('orderid')
         qty=ord.get('itemquantity')
         orders.objects.filter(orderid=orderid ,isplacedbyadmin=isAdminplaced).update(itemquantity=qty,incart=False,paymentstatus='completed')
     
   
 #helper function to update item quantity 

#helper method for checkout to update quantity
def updateitemsquantity(receipe):
    totalquantities=0
    for it in receipe:
        totalquantities=int(it.get('quantity'))-totalquantities
       # Item.objects.filter(id=it.rec.get('receipeid')).update(totalquantities=totalquantities)
        totalquantities=0
    

#helper function for employee transactios  entry in transations table
def updatetransactions(username,total):
    trans=Transactions.objects.create(
        username=User.objects.get(username=username),
        amount=total,
        transactype='debit'
        )
    trans.save()
    
#helper function for employee to record hitory of employee
def employeehistory(username,receipe):
     for rec in receipe:
               
        emph= EmployeeOrderHistory.objects.create(
            username=User.objects.get(username=username),
            itemname=Item.objects.get(id=rec.get('receipeid')),
            Quantity=rec.get('quantity'),
            price=rec.get('price')
        )
        emph.save()
   


#add user selected food receipe
def addordersdetail(request):
    
    if request.method=="POST":
        receipeid=request.POST.get('id')
        qty=request.POST.get('itemquantity')
        #cartcount=request.POST.get('cartcount')
        isAdminplaced=request.POST.get('isAdminplaced')
        employeename=request.POST.get('employeename')
        currentuser=request.user
        if (isAdminplaced=='true'):
                orderplaced(receipeid,qty,employeename,True)
                cartcount=carcount(employeename,True)
                return JsonResponse({'message':'order added','cartcount':cartcount},safe=False)
        else:
            orderplaced(receipeid,qty,currentuser,False)
            cartcount=carcount(currentuser,False)
            return JsonResponse({'message':'order added','cartcount':cartcount},safe=False)


def deletecartitem(request):
   
   orderid=request.GET.get('orderid')
   currentuser=request.user
   isAdminplaced=request.POST.get('isAdminplaced')
   employeename=request.POST.get('employeename')
   #orders.objects.filter(orderid=orderid).delete()
   if (isAdminplaced=='true'):
       orders.objects.filter(orderid=orderid,isplacedbyadmin=True).delete()
       
       return JsonResponse({'message':'item deleted'},safe=False)
        
   elif(isAdminplaced=='false' or isAdminplaced==''):
        orders.objects.filter(orderid=orderid,isplacedbyadmin=False).delete()
        
        return JsonResponse({'message':'item deleted'},safe=False)
   elif(isAdminplaced==None):
        orders.objects.filter(orderid=orderid,isplacedbyadmin=False).delete()
        
        return JsonResponse({'message':'item deleted'},safe=False)
  

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


#helper function to saving the the orders
def orderplaced(receipeid,qty,username,orderbyadmin):
        username=User.objects.filter(username=username).values('id')
        userid=username[0]['id']
        username=User.objects.get(id=userid)
        receipe=Item.objects.get(id=receipeid)
        order=orders.objects.create(
            username=username,
            receipeid=receipe,
            itemquantity=qty,
            incart=True,
            paymentstatus='initiated',
            isplacedbyadmin=orderbyadmin
        )
        order.save()

#helper function to get the cartcount
def carcount(username,orderbyadmin):
     cartcount=0
     username=User.objects.filter(username=username).values('id')
     userid=username[0]['id']
     orderscount=orders.objects.filter(username=userid,paymentstatus='initiated',isplacedbyadmin=orderbyadmin).values('itemquantity')
     for ordercnt in  orderscount:
           cartcount= ordercnt['itemquantity'] + cartcount
     return cartcount

 #helper function to get the details of orders in cart   
def getitemsincart(username,orderbyadmin):
     username=User.objects.filter(username=username).values('id')
     userid=username[0]['id']
     order_items = orders.objects.filter(username=userid,isplacedbyadmin=orderbyadmin,paymentstatus='initiated').select_related('receipeid').values(
                                'receipeid__itemName','receipeid__price','receipeid__receipe','receipeid__image',
                                'itemquantity','receipeid')
     return order_items
     