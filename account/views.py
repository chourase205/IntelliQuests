from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth

from .models import Profile
from quiz.models import QuizSubmission


# =========================
# REGISTER
# =========================
def register(request):

    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already used. Try login.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        # Create user (Profile will be auto-created by signals)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Login user
        user = auth.authenticate(username=username, password=password)
        auth.login(request, user)

        messages.success(request, "Account created successfully!")
        return redirect('profile', username)

    return render(request, "register.html")


# =========================
# LOGIN
# =========================
def login(request):

    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('profile', username)

        messages.error(request, "Invalid credentials!")
        return redirect('login')

    return render(request, "login.html")


# =========================
# LOGOUT
# =========================
@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')


# =========================
# PROFILE VIEW
# =========================
@login_required
def profile(request, username):

    profile_user = get_object_or_404(User, username=username)
    profile_data = get_object_or_404(Profile, user=profile_user)

    submissions = QuizSubmission.objects.filter(user=profile_user)

    chart_labels = []
    chart_percentages = []

    quiz_names = [s.quiz.title for s in submissions]
    quiz_scores = [s.score for s in submissions]
    quiz_totals = [s.quiz.question_set.count() for s in submissions]

    for submission in submissions:
        total_questions = submission.quiz.question_set.count()
        percentage = round((submission.score / total_questions) * 100, 1) if total_questions else 0
        chart_labels.append(submission.quiz.title)
        chart_percentages.append(percentage)

    context = {
        "profile_user": profile_user,
        "profile_data": profile_data,
        "submissions": submissions,
        "quiz_names": quiz_names,
        "quiz_scores": quiz_scores,
        "quiz_totals": quiz_totals,
        "chart_labels": chart_labels,
        "chart_percentages": chart_percentages,
    }

    return render(request, "profile.html", context)


# =========================
# EDIT PROFILE
# =========================
@login_required
def editProfile(request):

    viewer_user = request.user
    viewer_profile = get_object_or_404(Profile, user=viewer_user)

    if request.method == "POST":

        # Profile image
        if request.FILES.get('profile_img'):
            viewer_profile.profile_img = request.FILES.get('profile_img')

        # Email
        new_email = request.POST.get('email')
        if new_email and new_email != viewer_user.email:
            if User.objects.filter(email=new_email).exclude(id=viewer_user.id).exists():
                messages.error(request, "Email already in use.")
                return redirect('edit_profile')
            viewer_user.email = new_email

        # Username
        new_username = request.POST.get('username')
        if new_username and new_username != viewer_user.username:
            if User.objects.filter(username=new_username).exclude(id=viewer_user.id).exists():
                messages.error(request, "Username already in use.")
                return redirect('edit_profile')
            viewer_user.username = new_username

        viewer_user.first_name = request.POST.get('firstname')
        viewer_user.last_name = request.POST.get('lastname')

        viewer_user.save()

        viewer_profile.location = request.POST.get('location')
        viewer_profile.gender = request.POST.get('gender')
        viewer_profile.bio = request.POST.get('bio')
        viewer_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile', viewer_user.username)

    return render(request, "profile-edit.html", {"profile_data": viewer_profile})


# =========================
# DELETE PROFILE
# =========================
@login_required
def deleteProfile(request):

    viewer_user = request.user
    viewer_profile = get_object_or_404(Profile, user=viewer_user)

    if request.method == "POST":
        viewer_profile.delete()
        viewer_user.delete()
        return redirect('login')

    return render(request, "confirm.html", {"profile_data": viewer_profile})
