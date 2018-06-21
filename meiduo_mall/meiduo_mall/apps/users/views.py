from django.shortcuts import render
from rest_framework.response import Response

from rest_framework.views import APIView

# Create your views here.
from users.models import User


class UsernameCountView(APIView):
    '''用户名数量'''

    def get(self, request, username):
        '''获取指定用户名数量'''

        count = User.objects.filter(username=username).count()
        data = {
            'username' : username,
            'count' : count
        }

        return Response(data)

