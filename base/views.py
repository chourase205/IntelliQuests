from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from account.models import Profile
from quiz.models import UserRank, Quiz, QuizSubmission, Question
from django.contrib.auth.decorators import login_required, user_passes_test
import datetime
from .models import Message, Blog
import math
from django.db.models.functions import ExtractYear
from django.db.models import Count, Q
from django.http import FileResponse, Http404
import os
from django.conf import settings

# Create your views here.
def home(request):
    
    leaderboard_users = UserRank.objects.order_by('rank')[:4]

    context = {"leaderboard_users": leaderboard_users}

    return render(request, 'welcome.html', context)


@login_required(login_url="login")
def leaderboard_view(request):
    
    leaderboard_users = UserRank.objects.order_by('rank')
    
    context = {"leaderboard_users": leaderboard_users,}
    return render(request, "leaderboard.html", context)


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
@login_required(login_url="login")
def dashboard_view(request):

    total_users = User.objects.all().count()
    total_quizzes = Quiz.objects.all().count()
    total_quiz_submit = QuizSubmission.objects.all().count()
    total_questions = Question.objects.all().count()

    today = datetime.date.today()
    today_users = User.objects.filter(date_joined__date=today).count()
    today_quizzes_objs = Quiz.objects.filter(created_at__date=today)
    today_quizzes = today_quizzes_objs.count()
    today_quiz_submit = QuizSubmission.objects.filter(submitted_at__date=today).count()

    today_questions = sum(q.question_set.count() for q in today_quizzes_objs)

    gain_users = gain_percentage(total_users, today_users)
    gain_quizzes = gain_percentage(total_quizzes, today_quizzes)
    gain_quiz_submit = gain_percentage(total_quiz_submit, today_quiz_submit)
    gain_questions = gain_percentage(total_questions, today_questions)

    # FIXED — use a different variable name
    inbox_messages = Message.objects.all().order_by('-created_at')[:10]

    context = {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_quiz_submit": total_quiz_submit,
        "total_questions": total_questions,
        "today_users": today_users,
        "today_quizzes": today_quizzes,
        "today_quiz_submit": today_quiz_submit,
        "today_questions": today_questions,
        "gain_users": gain_users,
        "gain_quizzes": gain_quizzes,
        "gain_quiz_submit": gain_quiz_submit,
        "gain_questions": gain_questions,

        # FIXED VARIABLE
        "inbox_messages": inbox_messages,
    }

    return render(request, "dashboard.html", context)



def gain_percentage(total, today):
    if total > 0 and today > 0:
        gain = math.floor((today * 100) / total)
        return gain
    return 0


def about_view(request):
    return render(request, "about.html")


def blogs_view(request):
    
    year_blog_count = Blog.objects.annotate(year=ExtractYear('created_at')).values('year').annotate(count=Count('id')).order_by('-year').filter(status='public')

    blogs = Blog.objects.filter(status='public').order_by('-created_at')
    
    context = {"year_blog_count":year_blog_count, "blogs":blogs}
    return render(request, "blogs.html", context)


@login_required(login_url="login")
def blog_view(request, blog_id):
    
    blog =get_object_or_404(Blog, pk=blog_id)

    context = {"blog": blog}
    return render(request, "blog.html", context)


@login_required(login_url="login")
def contact_view(request):

    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if subject and message:
            Message.objects.create(
                user=request.user,
                subject=subject,
                message=message
            )
            messages.success(request, "We got your message. We will resolve your query soon.")
            return redirect('profile', request.user.username)

    return render(request, "contact.html", {"user_profile": user_profile})

@user_passes_test(is_superuser)
@login_required
def message_view(request, id):
    
    message = Message.objects.filter(id=int(id)).first()
    message = get_object_or_404(Message, pk=id)
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {"message":message}
    return render(request, "message.html", context)


def term_condition_view(request):
    return render(request, "term-condition.html")


@login_required(login_url="login")
def downloads_view(request):
    return render(request, "downloads.html")

def search_users_view(request):

    query = request.GET.get('q')

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).order_by('date_joined')

    else:
        users = []

    context = {"query": query, "users": users}
    return render(request, "search-users.html", context)

def download_research_paper(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'downloads', 'research_paper.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        raise Http404("File not found")
    
def download_report_view(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'downloads', 'report.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        raise Http404("File not found")
    
def download_notes_view(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'downloads', 'notes.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        raise Http404("File not found")


def custom_404(request, exception):
    return render(request, "404.html", status=404)