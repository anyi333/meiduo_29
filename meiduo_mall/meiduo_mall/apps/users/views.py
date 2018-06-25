from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from . import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
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

class EmailView(UpdateAPIView):
    '''保存用户邮箱'''
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        # 重写get_object方法,不用写query_set
        # 返回当前请求的用户
        # 在类视图对象中,可以通过类视图对象的属性获取request
        # 在django的请求request对象中,user属性表示当前请求的用户
        return self.request.user

    # def put(self):
    # 获取email-->校验email-->查询user-->更新数据-->序列化返回

class VerifyEmailView(APIView):
    '''邮箱验证'''
    def get(self,request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message':'缺少token'},status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message':'链接信息无效'},status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message':'OK'})
