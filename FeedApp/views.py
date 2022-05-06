from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required #decorator = varifies something, once varified, allows use to following function. Restricts access unless user is logged in
def profile(request): #access DB and posting things to website
    #only want ppl logged in to have access to it. (hence decorator)
    profile = Profile.objects.filter(user=request.user) #user refers to currently logged in user. user = fields in profile model. user filter b/c get doesn't work w/ exists
    if not profile.exists(): #checks to see if user has profile, if not, creates one
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user) #can use ".get()" here b/c not working w/ ".exists()"

    if request.method != 'POST':
        form = ProfileForm(instance=profile) #instance = profile in case user already has a profile and wants to update it
    else: #request method = "POST", trying to save to DB
        form = ProfileForm(instance=profile, data=request.POST) #grab all info from Profile class form for that specific user instance
                                                                #if user has filled out all information described in Profile class in forms.py, the form is valid
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile') #keeps them on the profile page

    context = {'form': form}
    return render(request, 'FeedApp/profile.html', context)

@login_required
def myfeed(request): #want to see all of our posts + all likes and comments
    comment_count_list = []
    like_count_list = [] #create empty lists b/c there are multiple comments 
    posts = Post.objects.filter(username=request.user).order_by('-date_posted')#use filter if >1, use get() if only 1
                                                                               #order_by = descending order
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()#provides number of comments on each post
        l_count = Like.objects.filter(post=p).count() #provides number of likes on each post
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    #iterate through the comments and likes of each post together
    zipped_list = zip(posts,comment_count_list,like_count_list)

    context = {'posts':posts, 'zipped_list': zipped_list} #context is how we pass all of the things in this function to myfeed in urls?
    return render(request, 'FeedApp/myfeed.html', context)

@login_required
def new_post(request):
    #check if GET or POST request
    #pulls info from forms.py --> PostForm
        #form only needs 2 pieces of info: description and image
    if request.method != 'POST':
        form = PostForm()
    else: 
        form=PostForm(request.POST, request.FILES) #Pull all the data from the PostForm and the images
        if form.is_valid():
           new_post = form.save(commit=False) #don't write to DB yet (don't have username info yet), just save instance.
           new_post.username=request.user
           new_post.save()
           return redirect('FeedApp:myfeed') #once user posts, keep them on MyFeed page so they can see their post
    
    context= {'form':form}
    return render(request, 'FeedApp/new_post.html', context)


'''
comments class is different from others b/c we don't have a form for it. 
Need to mannually create the fields.
'''

@login_required
def comments(request, post_id): #post_id is needed b/c we have to link each comment to a particular post
                                #Comments class in models.py file has post as a FK 
    if request.method == 'POST' and request.POST.get("btn1"): #check if sending info to DB AND if "submit" button has been clicked (submit button variable = "btn1")
        comment = request.POST.get("comment") #request.get() = getting text in comment box
        Comment.objects.create(post_id=post_id, username=request.user,text=comment, date_added=date.today()) #capital C b/c refering to the Comments model (in model.py file)
                                    #post = a field in Comments model, Django assigns it an ID automatically
                                    #to call that ID, you use the DB column name_id
                                    #we need the ID number, NOT the actual post text itself, to connect to a particular post

                                    #need post_id, username, text, & date_added b/c those are the fields assigned in the Comments model
                                        #creates a new row in comment model w/ those fields in the DB
        

    '''
    once comment = created, refresh screen so shows up on the page
    but need to get ALL comments on the post once comment = submitted
    '''
    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context = {'post':post,'comments':comments}
    
    return render(request, 'FeedApp/comments.html', context)




