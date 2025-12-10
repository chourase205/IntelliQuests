from django.urls import path
from django.conf.urls import handler404
from . import views

handler404 = views.custom_404

urlpatterns = [
    path('', views.home, name='home'),
    path('leaderboard', views.leaderboard_view, name='leaderboard'),
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('message/<int:id>', views.message_view, name='message'),
    path('about', views.about_view, name='about'),
    path('blogs', views.blogs_view, name='blogs'),
    path('blogs/<str:blog_id>', views.blog_view, name='blog'),
    path("contact", views.contact_view, name="contact"),
    path("term-condition", views.term_condition_view, name="term_condition"),
    path("downloads", views.downloads_view, name="downloads"),
    path('downloads/research-paper/', views.download_research_paper, name='research_paper'),
    path('downloads/report/', views.download_report_view, name='report'),
    path('downloads/notes/', views.download_notes_view, name='notes'),
    path("search/users", views.search_users_view, name="search_users"),
]
