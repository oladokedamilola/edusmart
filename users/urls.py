from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.verify_id, name='verify_id'),
    path('create-account/', views.create_account, name='create_account'),
    path('login/', views.login_view, name='login'),

    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('logout/', views.logout_view, name='logout'),

path('profile/', views.view_profile, name='view_profile'),

]
