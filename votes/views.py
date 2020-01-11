from django.shortcuts import render
from rest_framework import viewsets

from .models import VoteParser, Voting, Vote, WriterDetail
from .serializer import VoteParserSerializer, VotingSerializer, VoteSerializer, WriterDetailSerializer


class VoteParserViewSet(viewsets.ModelViewSet):
    queryset = VoteParser.objects.all()
    serializer_class = VoteParserSerializer


class VotingViewSet(viewsets.ModelViewSet):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class WriterDetailViewSet(viewsets.ModelViewSet):
    queryset = WriterDetail.objects.all()
    serializer_class = WriterDetailSerializer
