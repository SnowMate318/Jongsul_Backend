#git ignore 설정하기

myDATABASES = {
	'default' : {
					'ENGINE' : 'django.db.backends.mysql', # 벡엔드 엔진
					'NAME' : 'jongsul', # 'mysql'의 이름을 가진 데이터베이스
					'USER' : 'gimtaehyeon', # 계정
					'PASSWORD' : 'xogus0318*', #rootpassword로 지정할 숫자(6번에 나와있음)
					'HOST' : '127.0.0.1',
					'PORT' : '3306'
		}
}

OPENAI_API_KEY = "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"

SOCIALACCOUNT_PROVIDERS = {
    'kakao': {
        'APP': {
            'client_id': '1bf406f1b9c00885caa2e9b34b95035d',
            'secret': '1079055',
            'key': ''
        }
    }
}