# _*_ coding:utf-8 _*_
import re
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_email

from users.models import User, Address


class CreateUserSerializer(serializers.ModelSerializer):
    '''创建用户序列化器'''

    # read_only:序列化   write_only:反序列化,把JSON转化成模型类,从前端到后端
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='登录状态token',read_only=True)

    class Meta:
        model = User
        fields = ('id','username','password','password2','sms_code', 'mobile', 'allow','token')
        extra_kwargs = {
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password':{
                'write_only':True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的用户名',
                    'max_length': '仅允许8-20个字符的用户名',
            }

        }
    }

    def validate_mobile(self,value):
        '''验证手机号'''

        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self,value):
        '''校验用户是否同意协议'''
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次输入的密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        '''重写保存方法,增加密码加密'''

        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 数据库原生
        # user = User.objects.create(键=值,键=值...)
        # user = User.objects.create(**validated_data)
        # 调用父类
        user = super().create(validated_data)

        # 调用django的认证系统加密码
        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user

class UserDetailSerializer(serializers.ModelSerializer):
    '''用户详细信息序列化器'''
    class Meta:
        model = User
        fields = ('id','username','mobile','email','email_active')

class EmailSerializer(serializers.ModelSerializer):
    '''邮箱序列化器'''
    class Meta:
        model = User
        fields = ('id','email')
        extra_kwargs = {
            'email':{
                'required':True
            }
        }

    def update(self, instance, validated_data):  #更新
        # instance:视图传过来的user
        email = validated_data['email']
        instance.email = email
        # 先保存
        instance.save()

        # 生成激活链接
        verify_url = instance.generate_verify_email_url()
        # 发送验证邮件
        send_verify_email.delay(email,verify_url)

        return instance

class UserAddressSerializer(serializers.ModelSerializer):
    '''用户地址序列化器'''
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID',required=True)
    city_id = serializers.IntegerField(label='市ID',required=True)
    district_id = serializers.IntegerField(label='区ID',required=True)

    class Meta:
        model = Address
        exclude = ('user','is_delete','create_time','update_time')

    def validate_mobile(self,value):
        '''验证手机号'''
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        '''保存'''
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressTitleSerializer(serializers.ModelSerializer):
    '''地址标题'''

    class Meta:
        model = Address
        fields = ('title',)
