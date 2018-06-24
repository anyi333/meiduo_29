from rest_framework.permissions import IsAuthenticated

from . import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
from users.models import User


class UserView(CreateAPIView):
    '''
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    '''
    serializer_class = serializers.CreateUserSerializer

class MobileCountView(APIView):
    '''手机号数量'''

    def get(self, request, mobile):
        '''获取指定手机号数量'''

        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)

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

class UserDetailView(RetrieveAPIView):
    '''用户详情'''
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user




