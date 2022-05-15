from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods # To restrict access to views based on the request method 
from communicator.views import send_analytics
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
@require_http_methods(["GET"])
def home_view(request, *args, **kwargs):
    '''
    This is the home page view. It renders the home page of the application
    '''
    send_analytics(request, "Open Home Page")
    context = {
    }
    return render(request, "home/home.html", context)

@staff_member_required  # the message is protected. 
@require_http_methods(["GET"])
def management_view(request, *args, **kwargs):
    '''
    This is the management page view. It renders the buttons to run the delivery of services on a click of a button if automation fails
    '''
    send_analytics(request, "Open Management Page")
    context = {
    }
    return render(request, "management/home.html", context)

@require_http_methods(["POST"])
def sandbox_view(request, *args, **kwargs):
    '''
    Work in progress - This is the view that guides the users to the Beyondmachines Sandbox slack workspace for demos
    '''
    send_analytics(request, "Click Sandbox")
    context = {
    }
    return redirect(request, "home/home.html", context)


def err_handler404(request, exception):
    '''
    internal function custom error 404 handler
    '''
    return render(request, "errors/error404.html", status=404)


def err_handler500(request, exception=None):
    '''
   internal function  custom error 500 handler
    '''
    return render(request, "errors/error500.html", status=500)


def err_handler403(request, exception=None):
    '''
    internal function custom error 403 handler
    '''
    return render(request, "errors/error403.html", status=403)


def err_handler400(request, exception=None):
    '''
    internal function custom error 400 handler
    '''
    return render(request, "errors/error400.html", status=400)
