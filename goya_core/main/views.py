from django.shortcuts import render
from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 


# Create your views here.
@require_http_methods(["GET"])
def home_view(request, *args, **kwargs):
    '''
    This is the home page view. 
    At this moment it's empty until we learn what we want to add here.
    '''
    context = {
    }
    return render(request, "home/home.html", context)
