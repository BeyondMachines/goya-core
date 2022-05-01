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

def err_handler404(request, exception):
    return render(request, "errors/error404.html", status=404)

def err_handler500(request, exception=None):
    return render(request, "errors/error500.html", status=500)

def err_handler403(request, exception=None):
    return render(request, "errors/error403.html", status=403)

def err_handler400(request, exception=None):
    return render(request, "errors/error400.html", status=400)
