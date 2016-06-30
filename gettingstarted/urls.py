from django.conf.urls import include, url
from app import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # /Votes/
    url(r'^$', views.index, name='index'),

    # /results/
    url(r'^results/$', views.results, name='results'),

    # /prev_results/
    url(r'^prev_results/$', views.prev_results, name='prev_results'),

    # /arguments/
    url(r'^arguments/$', views.arguments, name='arguments'),

    # vote-check
    url(r'^vote-check/$', views.process_vote, name='check_vote'),

    # Captcha
    url(r'^captcha/', include('captcha.urls')),

    # logout
    url(r'^logout/$', views.logout_user, name='logout'),

    # login
    url(r'^login/$', views.login_user, name='login'),

    # user_info
    url(r'^user_info/$', views.user_info, name='user_info'),

    # submit_arg
    url(r'^submit_arg/$', views.submit_arg, name='submit_arg'),

    # Comments
    url(r'^arguments/(?P<arg_id>[0-9]+)$', views.comments, name='comments'),

    # submit_comment
    url(r'^submit_comment/$', views.submit_comment, name='submit_comment'),

    # like
    url(r'^like_arg/$', views.like_arg, name='like_arg'),

    # like_comment
    url(r'^like_comment/$', views.like_comment, name='like_comment'),

    # dislike
    url(r'^dislike_arg/$', views.dislike_arg, name='dislike_arg'),

    # dislike_comment
    url(r'^dislike_comment/$', views.dislike_comment, name='dislike_comment'),

    # delete arg
    url(r'^delete_arg/$', views.delete_arg, name='delete_arg'),

    # delete comment
    url(r'^delete_comment/$', views.delete_comment, name='delete_comment'),

    # help
    url(r'^help/$', views.help_page, name='help_page'),

    # help
    url(r'stats/$', views.down_stats, name='stats.txt'),

    # send mail
    url(r'email/$', views.send_email_all, name='send_mail'),

    # change name
    url(r'change_name/$', views.change_name, name='change_name'),

    # delete account
    url(r'delete_account/$', views.delete_account, name='delete_account'),

    # Admins
    url(r'^admin/', include(admin.site.urls)),
]
