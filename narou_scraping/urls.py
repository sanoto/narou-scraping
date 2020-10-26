"""narou_scraping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from rest_framework import routers

from users import views as users_views
from votes import views as votes_views
from narou import views as narou_views

router = routers.DefaultRouter()
router.register(r'users', users_views.UserViewSet)
router.register(r'narou/writers', narou_views.WriterViewSet)
router.register(r'narou/novels', narou_views.NovelViewSet)
router.register(r'narou/chapters', narou_views.ChapterViewSet)
router.register(r'narou/episodes', narou_views.EpisodeViewSet)
router.register(r'narou/illusts', narou_views.IllustViewSet)
router.register(r'narou/words', narou_views.WordViewSet)
router.register(r'narou/key_words', narou_views.KeyWordViewSet)
router.register(r'narou/novel_details', narou_views.NovelDetailViewSet)
router.register(r'votes/parsers', votes_views.VoteParserViewSet)
router.register(r'votes/voting_list', votes_views.VotingViewSet)
router.register(r'votes/votes', votes_views.VoteViewSet)
router.register(r'votes/writer_details', votes_views.WriterDetailViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('webhook/twitter/', narou_views.TwitterWebhook.as_view())
]
