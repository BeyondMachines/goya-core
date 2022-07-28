"""goya_core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main.views import home_view, err_handler400, err_handler403, err_handler404, err_handler500, management_view, contact_view
from slack_app.views import slack_install_view, slack_callback_view, slack_sandbox_invite_view

from communicator.views import send_advisories_view, send_event_report_view, send_awareness_message_view, send_potentital_candidates_message_view
from content.views import get_event_candidates_from_rss, list_awareness_message, get_reddit_events

from django.contrib.flatpages import views
from django.conf import settings
from django.conf.urls.static import static

handler400 = err_handler400
handler403 = err_handler403
handler404 = err_handler404
handler500 = err_handler500


urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('contact/', contact_view, name='contact'),
    path('management/', management_view, name='management'),
    path('slack/install', slack_install_view, name='slack_install'),
    path('sandbox/', slack_sandbox_invite_view, name='slack_sandbox_invite'),

    path('slack/oauth/callback', slack_callback_view, name='slack_callback'),
    path('send_advisory/', send_advisories_view, name='send_advisories'),
    path('send_events/', send_event_report_view, name='send_events'),
    path('send_awareness/', send_awareness_message_view, name='send_awareness'),
    path('send_potentital_candidates_message_view/', send_potentital_candidates_message_view, name="send_potentital_candidates_message_view"),

    path('get_event_candidates/', get_event_candidates_from_rss, name='get_event_candidates'),
    path('list_awareness_message/', list_awareness_message, name='list_awareness_message'),
    path('get_reddit_events/', get_reddit_events, name='get_reddit_events'),

    #  path('slack/design', design_page_view, name='design'),
    # below are the flatpages content objects
    path('privacy/', views.flatpage, {'url': '/privacy/'}, name='privacy'),
    path('faq/', views.flatpage, {'url': '/faq/'}, name='faq'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)