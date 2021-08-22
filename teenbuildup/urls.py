from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib import admin
from app import views

urlpatterns = [
    path('deletepost/<name_of_organization>', views.deletepost, name='deletepost'),
    path('editpost/<name_of_organization>', views.editpost, name='editpost'),
    path('savepost/<name_of_organization>', views.savepost, name='savepost'),
    path('unfollowpost/<name_of_organization>', views.unfollowpost, name='unfollowpost'),
    path('admin/', admin.site.urls),
    path('', views.indexpage),
    path('home/', views.homepage),
    path('popular/', views.Popular),
    path('log-in/', auth_views.LoginView.as_view(template_name="login.html")),
    path('sign-out/', auth_views.LogoutView.as_view(next_page="/")),
    path('sign-up/', views.signup),
    path('profile/', views.profile),
    path('post/', views.PostOrganization),
    path('myposts/', views.myposts),
    path('following/', views.SavedPosts),
    path('contact/', views.email),
    path('searchforstartups/', views.searchforstartups),
    path('searchforstartups/environmental/', views.searchforstartupsenv),
    path('searchforstartups/STEM/', views.searchforstartupsstem),
    path('searchforstartups/reading-writing/', views.searchforstartupsread),
    path('searchforstartups/art-music/', views.searchforstartupsart),
    path('searchforclubs/', views.searchforclubs),
    path('searchforclubs/environmental/', views.searchforclubsenv),
    path('searchforclubs/STEM/', views.searchforclubsstem),
    path('searchforclubs/reading-writing/', views.searchforclubsread),
    path('searchforclubs/art-music/', views.searchforclubsart),
    path('searchforevents/', views.searchforevents),
    path('searchforevents/environmental/', views.searchforeventsenv),
    path('searchforevents/STEM/', views.searchforeventsstem),
    path('searchforevents/reading-writing/', views.searchforeventsread),
    path('searchforevents/art-music/', views.searchforeventsart),
]
