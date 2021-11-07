from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from app import forms
from app.models import Post, Area
from django.core.mail import send_mail
from django.conf import settings

def indexpage(request):
    return render(request,'index.html')

@login_required
def homepage(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    return render(request,'index.html')

def signup(request):
    form = forms.SignUpForm()
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = form.save(commit=False)
            user.username = email
            user.save()
            login(request, user)
            return redirect('/home/')
    return render(request, 'signup.html', {
        'form': form
    })

@login_required()
def profile(request):
    current_user = request.user.area
    user_form = forms.BasicUserForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    area_form = forms.Area()
    if request.method == 'POST':
        if request.POST.get('action') == 'update_profile':
            user_form = forms.BasicUserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('/profile/')
        elif request.POST.get('action') == 'update_area':
            area_form = forms.Area(request.POST, instance=current_user)
            if area_form.is_valid():
                area_form = area_form.save(commit=False)
                area_form.area = area_form.area.lower()
                area_form.area = area_form.area.replace(" ", "")
                area_form.save()
                messages.success(request, 'Your area has been updated.')
                return redirect('/profile/')
        elif request.POST.get('action') == 'update_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request,user)
                messages.success(request, 'Your profile has been updated.')
                return redirect('/profile/')
    return render(request, 'profile.html', {
        "user_form": user_form,
        "area_form": area_form,
        "password_form": password_form,
    })

@login_required()
def PostOrganization(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    post_form = forms.PostOrganization()
    if request.method == "POST":
        if request.POST.get('step') == '1':
            post_form = forms.PostOrganization(request.POST)
            if post_form.is_valid():
                creating_post = post_form.save(commit=False)
                creating_post.email = request.user.email
                creating_post.area = creating_post.area.lower()
                creating_post.area = creating_post.area.replace(" ", "")
                creating_post.save()
                return redirect('/post/')
    return render(request, 'post.html', {
        "post_form": post_form,
    })

@login_required()
def myposts(request):
    myposts = Post.objects.filter(email=request.user.email).order_by('-created_at')
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    return render(request, 'myposts.html', {
        "myposts": myposts,
    })

@login_required()
def editpost(request, name_of_organization):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    edit = Post.objects.filter(email=request.user.email).get(name_of_organization=name_of_organization)
    post_form = forms.PostOrganization(request.POST or None, instance=edit)
    if post_form.is_valid():
        post_form.save()
        return redirect('/myposts/')
    return render(request, 'editpost.html', {
        "edit": edit,
        "post_form": post_form,
    })

@login_required()
def deletepost(request, name_of_organization):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    delete = Post.objects.filter(email=request.user.email).get(name_of_organization=name_of_organization)
    delete.delete()
    return redirect('/myposts/')

@login_required()
def unfollowpost(request, name_of_organization):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    post = Post.objects.get(name_of_organization=name_of_organization)
    if post.saved.filter(id=request.user.id).exists():
        post.saved.remove(request.user)
    else:
        return redirect('/following/')
    return redirect('/following/')

@login_required()
def savepost(request, name_of_organization):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    post = Post.objects.get(name_of_organization=name_of_organization)
    if post.saved.filter(id=request.user.id).exists():
        return redirect('/following/')
    else:
        post.saved.add(request.user)
    return redirect('/following/')

@login_required()
def SavedPosts(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    user = request.user
    saved_posts = user.saved.all()
    return render(request, 'following.html', {
        "saved_posts": saved_posts,
    })

@login_required()
def email(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'POST':
        tocontact = request.POST.get("to")
        subject = request.POST.get("subject")
        message = request.POST.get("message") + "\nContact Sender " + request.user.email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [tocontact],
        )
        return redirect('/')
    return render(request, 'email.html')

@login_required()
def searchforevents(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforevents')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Event").filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Event").filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'searchforevents.html', context)
        else:
            online = Post.filter(organization="Event").filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Event").filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'searchforevents.html', context)

@login_required()
def searchforeventsenv(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforevents')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Event").filter(interest='Environment').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Event").filter(interest='Environment').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'events/environmental.html', context)
        else:
            online = Post.filter(organization="Event").filter(interest='Environment').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Event").filter(interest='Environment').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'events/environmental.html', context)

@login_required()
def searchforeventsstem(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforevents')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Event").filter(interest='STEM').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Event").filter(interest='STEM').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'events/STEM.html', context)
        else:
            online = Post.filter(organization="Event").filter(interest='STEM').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Event").filter(interest='STEM').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'events/STEM.html', context)

@login_required()
def searchforeventsread(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforevents')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Event").filter(interest='Reading/Writing').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Event").filter(interest='Reading/Writing').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'events/readingwriting.html', context)
        else:
            online = Post.filter(organization="Event").filter(interest='Reading/Writing').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Event").filter(interest='Reading/Writing').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'events/readingwriting.html', context)

@login_required()
def searchforeventsart(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforevents')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Event").filter(interest='Music/Art').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Event").filter(interest='Music/Art').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'events/artmusic.html', context)
        else:
            online = Post.filter(organization="Event").filter(interest='Music/Art').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Event").filter(interest='Music/Art').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'events/artmusic.html', context)

@login_required()
def searchforclubs(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforclubs')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Club").filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Club").filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')

            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'searchforclubs.html', context)
        else:
            online = Post.filter(organization="Club").filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Club").filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'searchforclubs.html', context)

@login_required()
def searchforclubsenv(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforclubs')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Club").filter(interest='Environment').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Club").filter(interest='Environment').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                        'searchbutton': searchbutton}
            return render(request, 'clubs/environmental.html', context)
        else:
            online = Post.filter(organization="Club").filter(interest='Environment').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Club").filter(interest='Environment').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'clubs/environmental.html', context)

@login_required()
def searchforclubsstem(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforclubs')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Club").filter(interest='STEM').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Club").filter(interest='STEM').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'clubs/STEM.html', context)
        else:
            online = Post.filter(organization="Club").filter(interest='STEM').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Club").filter(interest='STEM').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'clubs/STEM.html', context)

@login_required()
def searchforclubsread(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforclubs')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Club").filter(interest='Reading/Writing').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Club").filter(interest='Reading/Writing').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'clubs/readingwriting.html', context)
        else:
            online = Post.filter(organization="Club").filter(interest='Reading/Writing').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Club").filter(interest='Reading/Writing').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'clubs/readingwriting.html', context)

@login_required()
def searchforclubsart(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforclubs')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Club").filter(interest='Music/Art').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Club").filter(interest='Music/Art').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                        'searchbutton': searchbutton}
            return render(request, 'clubs/artmusic.html', context)
        else:
            online = Post.filter(organization="Club").filter(interest='Music/Art').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Club").filter(interest='Music/Art').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'clubs/artmusic.html', context)

@login_required()
def searchforstartups(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforstartups')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Start-Up").filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Start-Up").filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'searchforstartups.html', context)
        else:
            online = Post.filter(organization="Start-Up").filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Start-Up").filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'searchforstartups.html', context)

@login_required()
def searchforstartupsenv(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforstartups')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Start-Up").filter(interest='Environment').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Start-Up").filter(interest='Environment').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                        'searchbutton': searchbutton}
            return render(request, 'startups/environmental.html', context)
        else:
            online = Post.filter(organization="Start-Up").filter(interest='Environment').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Start-Up").filter(interest='Environment').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'startups/environmental.html', context)

@login_required()
def searchforstartupsstem(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforstartups')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Start-Up").filter(interest='STEM').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Start-Up").filter(interest='STEM').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'startups/STEM.html', context)
        else:
            online = Post.filter(organization="Start-Up").filter(interest='STEM').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Start-Up").filter(interest='STEM').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'startups/STEM.html', context)

@login_required()
def searchforstartupsread(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforstartups')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Start-Up").filter(interest='Reading/Writing').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Start-Up").filter(interest='Reading/Writing').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                      'searchbutton': searchbutton}
            return render(request, 'startups/readingwriting.html', context)
        else:
            online = Post.filter(organization="Start-Up").filter(interest='Reading/Writing').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Start-Up").filter(interest='Reading/Writing').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'startups/readingwriting.html', context)

@login_required()
def searchforstartupsart(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    if request.method == 'GET':
        query = request.GET.get('searchforstartups')
        searchbutton = request.GET.get('submit')
        if query is not None:
            onlinesearch = Post.filter(organization="Start-Up").filter(interest='Music/Art').filter(description__icontains=query).filter(communication="Online").order_by('-created_at')
            inpersonsearch = Post.filter(organization="Start-Up").filter(interest='Music/Art').filter(description__icontains=query).filter(communication="In-Person").order_by('-created_at')
            context = {'onlinesearch': onlinesearch,
                       'inpersonsearch': inpersonsearch,
                        'searchbutton': searchbutton}
            return render(request, 'startups/artmusic.html', context)
        else:
            online = Post.filter(organization="Start-Up").filter(interest='Music/Art').filter(communication="Online").order_by('-created_at')
            inperson = Post.filter(organization="Start-Up").filter(interest='Music/Art').filter(communication="In-Person").filter(area=current_user).order_by('-created_at')
            context = {'online': online,
                       'inperson': inperson,
                       'searchbutton': searchbutton}
            return render(request, 'startups/artmusic.html', context)

@login_required()
def Popular(request):
    current_user = request.user.area
    if not current_user.area:
        return redirect('/profile/')
    startenv = Post.objects.filter(organization="Start-Up").filter(interest='Environment').order_by('-saved').all()[:10]
    startstem = Post.objects.filter(organization="Start-Up").filter(interest='STEM').order_by('-saved').all()[:10]
    startread = Post.objects.filter(organization="Start-Up").filter(interest='Reading/Writing').order_by('-saved').all()[:10]
    startart = Post.objects.filter(organization="Start-Up").filter(interest='Music/Art').order_by('-saved').all()[:10]
    startother = Post.objects.filter(organization="Start-Up").filter(interest='Other').order_by('-saved').all()[:10]
    clubenv = Post.objects.filter(organization="Club").filter(interest='Environment').order_by('-saved').all()[:10]
    clubstem = Post.objects.filter(organization="Club").filter(interest='STEM').order_by('-saved').all()[:10]
    clubread = Post.objects.filter(organization="Club").filter(interest='Reading/Writing').order_by('-saved').all()[:10]
    clubart = Post.objects.filter(organization="Club").filter(interest='Music/Art').order_by('-saved').all()[:10]
    clubother = Post.objects.filter(organization="Club").filter(interest='Other').order_by('-saved').all()[:10]
    eventenv = Post.objects.filter(organization="Event").filter(interest='Environment').order_by('-saved').all()[:10]
    eventstem = Post.objects.filter(organization="Event").filter(interest='STEM').order_by('-saved').all()[:10]
    eventread = Post.objects.filter(organization="Event").filter(interest='Reading/Writing').order_by('-saved').all()[:10]
    eventart = Post.objects.filter(organization="Event").filter(interest='Music/Art').order_by('-saved').all()[:10]
    eventother = Post.objects.filter(organization="Event").filter(interest='Other').order_by('-saved').all()[:10]
    return render(request, 'popular.html', {
        "startenv": startenv,
        "startstem": startstem,
        "startread": startread,
        "startart": startart,
        "startother":startother,
        "clubenv": clubenv,
        "clubstem": clubstem,
        "clubread": clubread,
        "clubart": clubart,
        "clubother":clubother,
        "eventenv": eventenv,
        "eventstem": eventstem,
        "eventread": eventread,
        "eventart": eventart,
        "eventother":eventother,
    })
