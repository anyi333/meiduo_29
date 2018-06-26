# _*_ coding:utf-8 _*_
import urllib
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import logging
from django.conf import settings
from rest_framework.utils import json
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from oauth import constants
from oauth.exceptions import OAuthQQAPIError

logger = logging.getLogger('django')

class OAuthQQ(object):
    '''QQ认证辅助工具类'''

    def __init__(self,client_id=None,redirect_uri=None,state=None,client_secret=None):
        # 初始化实例对象
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  #保存登录成功后的跳转页面路径
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET

    def get_qq_login_url(self):
        '''
        获取qq登录的网址
        return:url
        '''
        params = {
            'response_type':'code',
            'client_id':self.client_id,
            'redirect_uri':self.redirect_uri,
            'state':self.state,
            'scope':'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?'

        # urllib.parse.urlencode(query)
        # 将query字典转换为url路径中的查询字符串
        url += urllib.parse.urlencode(params)

        return url

    def get_access_token(self,code):
        '''
        通过Authorization Code获取Access Token
        :param code: qq提供的code
        :return: asscess_token
        '''
        params = {
            'grant_type':'authorization_code',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'code':code,
            'redirect_uri':self.redirect_uri
        }

        url = 'https://graph.qq.com/oauth2.0/token?'
        url += urllib.parse.urlencode(params)

        try:
            # 发送请求
            response = urlopen(url)
            # 读取响应体数据，需要注意读取出的响应体数据为bytes类型
            response_data = response.read().decode()
            # urllib.parse.parse_qs(qs)将qs查询字符串格式数据转换为python的字典
            response_dict = urllib.parse.parse_qs(response_data)

        except Exception as e:
            logger.error('获取access_token异常:%s' % e)
            raise OAuthQQAPIError
        else:
            access_token = response_dict.get('access_token')
            return access_token[0]

    def get_openid(self,access_token):
        '''
        获取用户的openid
        :param access_token: qq提供的access
        :return: open_id
        '''
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:
            response = urlopen(url)
            response_data = response.read().decode()
            # 获取到openid,返回的数据为callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            # 包含10,不包括-4{'':''}
            # 解析
            response_dict = json.loads(response_data[10:-4])
        except Exception as e:
            logger.error('获取openid异常:%s' % e)
            raise OAuthQQAPIError
        else:
            openid = response_dict.get('openid')
            return openid

    def generate_save_user_token(self, openid):
        '''
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        '''
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({'openid': openid})
        return token.decode()

    @staticmethod
    def check_bind_user_access_token(access_token):
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data['openid']






