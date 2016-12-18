from django.conf.urls import url
from server import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^counter/$', views.counterSession, name='counter'),
    url(r'^register_user/$', views.register_user, name='register_user'),
    url(r'^nologged/$', views.nologged, name='nologged'),
    url(r'^move/$', views.move, name='move'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^create_game/$', views.create_game, name='create_game'),
    url(r'^clean_orphan_games/$', views.clean_orphan_games, name='clean_orphan_games'),
    url(r'^join_game/$', views.join_game, name='join_game'),
    url(r'^status_turn/$', views.status_turn, name='status_turn'),
    url(r'^status_board/$', views.status_board, name='status_board'),
    url(r'^game/$', views.game, name='game'),
    url(r'^show/$', views.show, name='show'),
    url(r'^show_ajax/$', views.show_ajax, name='show_ajax'),
    url(r'^wait/$', views.wait, name='wait'),
]
