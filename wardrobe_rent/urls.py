"""wardrobe_rent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/',include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    #path('about/',views.about),
    #path('about/',views.homepage),
    # path('account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
]

admin.site.site_header = "Wardrobe_Rent Administration"
admin.site.site_title = "Admin"
admin.site.index_title="Welcome Admin.."
