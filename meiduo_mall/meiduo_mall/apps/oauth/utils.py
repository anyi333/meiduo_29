# _*_ coding:utf-8 _*_
import urllib
from urllib.parse import urlencode
from django.conf import settings


class OAuthQQ(object):
    '''QQ认证辅助工具类'''

    def __init__(self,client_id=None,redirect_uri=None,state=None):
        # 初始化实例对象
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  #保存登录成功后的跳转页面路径



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

