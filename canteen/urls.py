"""
URL configuration for canteen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from food.views import *
from accounts.views import *
urlpatterns = [
        path('', fooditems,name='fooditems'),
        path('profile/', profile,name='profile'),
        path('login/', login_page,name='login_page'),
        path('register/', register,name='register'),
        path('logout/', logoutusr,name='logoutusr'),
        path('users/', displayallusers,name='dipslayUsers'),
        path('edit/<id>/', updateUserDetailsEmployee,name='edit'),
        path('adminpanel/', adminpanel,name='admpanle'),
        path('address/<id>', address,name='address'),
        path('menuitem/', foodmenu,name='menuitems'),
        path('payment/', payment,name='payment'),
        path('deleteuser/', deleteuser,name='delete'),
        path('edituser/', editUseradmin,name='edit'),
        path('cart/', itemcart,name='cart'),
        path('additem/', addfooditem,name='additem'),
        path('quickview/', getitemdetails,name='quickview'),
        path('addorder/', addordersdetail,name='addorder'),
        path('deleteorder/', deletecartitem,name='deleteorder'),
        path('checkout/', checkout,name='checkout'),
        path('assignroles/', assignroles,name='assignroles'),
        path('removeroles/', removeroles,name='removeroles'),
        path('guestLogin/', guest_Login_page,name='guestLogin'),
        path('guestLogout/', guest_Logout_page,name='guestLogout'),
        path('userdashboard/', userdashboard,name='userdashboard'),
        path('orderhistory/', userorderHistory,name='orderhistory'),
        path('editemployee/', editUser,name='editemployee'),
        path('listreceipe/', getallrecepies,name='listreceipe'),
        path('getreceipedetails/', getreceipedetails,name='getreceipedetails'),
        path('updatereceipe/', updatereceipe,name='updatereceipe'),
        path('deletereceipe/', deletereceipe,name='deletereceipe'),
        path('whatstoday/', whatstoday,name='whatstoday'),
        path('createtodayslist/', createtodaylist,name='createtodayslist'),
        path('todayslist/', whatstodaylist,name='todayslist'),
        path('searchfood/', searchfood,name='searchfood'),
        path('todaysmenupublic/', whatstodaylistpublic,name='todayspublic'),
          path('fooditems/', getallrecepies,name='todayspublic'),
        path('admin/', admin.site.urls),
]


if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT,
                              )


urlpatterns += staticfiles_urlpatterns()