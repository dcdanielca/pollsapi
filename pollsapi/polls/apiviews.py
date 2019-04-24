from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer, UserSerializer
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework import generics, viewsets
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def destroy(self, request, pk):
        get_object_or_404(Poll, pk = pk)
        poll = Poll.objects.filter(pk=pk, created_by=request.user) 
        if poll:
            poll.delete()
            return Response({"detail": "Poll deleted"}, status = status.HTTP_200_OK)
        else:
            return Response({"detail": "You can not delete this poll."}, status = status.HTTP_403_FORBIDDEN)

class ChoiceList(generics.ListCreateAPIView):
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs["pk"])

    def post(self, request, pk):
        choice_text = request.data.get("choice_text")
        data = {'choice_text': choice_text, 'poll': pk}
        serializer = ChoiceSerializer(data=data)
        poll = Poll.objects.filter(pk=pk, created_by=request.user)

        if poll and serializer.is_valid():
            choice = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You can not create choice for this poll."}, status=status.HTTP_403_FORBIDDEN)


class CreateVote(APIView):
    def post(self, request, pk, choice_pk):
        voted_by = request.data.get("voted_by")
        data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            vote = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer
