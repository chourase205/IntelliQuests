from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth   # ✅ FIXED
from .models import Profile
from quiz.models import QuizSubmission


# REGISTER
def register(request):

    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.info(request, "Password Not Matching.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email Already Used. Try to Login.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username Already Taken.")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Login user
        user_login = auth.authenticate(username=username, password=password)
        auth.login(request, user_login)

        # Create empty profile
        Profile.objects.create(user=user)

        return redirect('profile', username)

    return render(request, "register.html")



# PROFILE VIEW (🔧 FIXED)
@login_required
def profile(request, username):

    # Get user safely
    profile_user = get_object_or_404(User, username=username)

    # Get profile safely
    profile_data = get_object_or_404(Profile, user=profile_user)

    # Quiz submissions of profile owner
    submissions = QuizSubmission.objects.filter(user=profile_user)

    # Chart data
    quiz_names = [s.quiz.title for s in submissions]
    quiz_scores = [s.score for s in submissions]
    quiz_totals = [s.quiz.question_set.count() for s in submissions]

    context = {
        "profile_user": profile_user,
        "profile_data": profile_data,
        "submissions": submissions,

        # Chart data
        "quiz_names": quiz_names,
        "quiz_scores": quiz_scores,
        "quiz_totals": quiz_totals,
    }

    return render(request, "profile.html", context)



# EDIT PROFILE
@login_required
def editProfile(request):

    # Use 404 for safety
    viewer_user = get_object_or_404(User, id=request.user.id)
    viewer_profile = get_object_or_404(Profile, user=viewer_user)

    if request.method == "POST":

        # Image
        if request.FILES.get('profile_img'):
            viewer_profile.profile_img = request.FILES.get('profile_img')

        # Email
        new_email = request.POST.get('email')
        if new_email:
            exist = User.objects.filter(email=new_email).first()
            if exist and exist != viewer_user:
                messages.info(request, "Email Already Used, Choose a different one!")
                return redirect('edit_profile')
            viewer_user.email = new_email

        # Username
        new_username = request.POST.get('username')
        if new_username:
            exist = User.objects.filter(username=new_username).first()
            if exist and exist != viewer_user:
                messages.info(request, "Username Already Used, Choose a unique one!")
                return redirect('edit_profile')
            viewer_user.username = new_username

        # First/Last name
        viewer_user.first_name = request.POST.get('firstname')
        viewer_user.last_name = request.POST.get('lastname')

        viewer_user.save()

        # Profile info
        viewer_profile.location = request.POST.get('location')
        viewer_profile.gender = request.POST.get('gender')
        viewer_profile.bio = request.POST.get('bio')
        viewer_profile.save()

        return redirect('profile', viewer_user.username)

    return render(request, 'profile-edit.html', {"profile_data": viewer_profile})



# DELETE PROFILE
@login_required
def deleteProfile(request):

    viewer_user = request.user
    viewer_profile = Profile.objects.get(user=viewer_user)

    if request.method == "POST":
        viewer_profile.delete()
        viewer_user.delete()
        return redirect('logout')

    return render(request, 'confirm.html', {"profile_data": viewer_profile})



# LOGIN
def login(request):

    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('profile', username)

        messages.info(request, 'Credentials Invalid!')
        return redirect('login')

    return render(request, "login.html")



# LOGOUT
@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')
