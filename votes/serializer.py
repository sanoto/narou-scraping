from rest_framework import serializers

from .models import VoteParser, Voting, Vote, WriterDetail


class VoteParserSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteParser
        fields = ['id', 'regex']
        extra_kwargs = {'id': {'read_only': True}}


class VotingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = [
            'id', 'name', 'novel', 'start_time', 'end_time',
            'in_impression', 'in_writer_report', 'parsers', 'participants',
        ]
        extra_kwargs = {'id': {'read_only': True}}


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'voting', 'participant', 'posted_at', 'content']
        extra_kwargs = {'id': {'read_only': True}}


class WriterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterDetail
        fields = ['id', 'writer', 'twitter_id']
        extra_kwargs = {'id': {'read_only': True}}
