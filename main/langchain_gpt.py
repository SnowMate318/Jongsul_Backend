import getpass
import os, sys
from typing import List
from langchain_openai import ChatOpenAI, OpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_community.utils.openai_functions import (
    convert_pydantic_to_openai_function,
)
from langchain_community.callbacks import get_openai_callback
sys.path.append('jongsul')  # jongsul 폴더를 시스템 경로에 추가
from my_settings import OPENAI_API_KEY  # my_settings에서 OPENAI_API_KEY 가져오기

def getQuestions(script, difficulty, multiple_choice, short_answer, ox_prob, all_prob):
    class Choice(BaseModel):
        choice_num: int = Field(description="선택지를 4개로 하고, 선택지 번호를 1~4로 해줘")
        choice_content: str = Field(description="선택지 내용을 답해줘")

    class Question(BaseModel):
        question_num: int = Field(description="문제번호를 답해줘")    
        question_title: str = Field(description="생성한 문제의 제목을 답해줘")
        choices: List[Choice]
        "객관식 문제일 경우 4개의 초이스를 만들어줘"
        question_answer: str = Field(description="생성한 문제의 정답을 답해줘. 객관식: 번호(1~4) ox문제: o 또는 x, 단답형: 정답에 해당하는 단어")
        question_explanation: str = Field(description="생성한 문제의 정답에 대한 설명을 답해줘")
        question_type : int = Field(description = "객관식 문제일경우 1, 단답형 문제일경우 2, ox문제일경우 3이라고 답해줘")
        
    
    class Questions(BaseModel):
        "반환할 문제들"
        question: List[Question]
        
    gpt_model = "gpt-3.5-turbo-0125"
    #gpt_model = "gpt-4"


    model = ChatOpenAI(model=gpt_model, openai_api_key=OPENAI_API_KEY, temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are helpful assistant"), ("user", "{input}")]
    )

    parser = JsonOutputFunctionsParser(key_name="question")
    openai_functions = [convert_pydantic_to_openai_function(Questions)]
    chain = prompt | model.bind(functions=openai_functions) | parser

    try:
        with get_openai_callback() as cb:
            res = chain.invoke({"input": f"개념을 문제로 만들어줘 개념: {concept}, 난이도(1->(쉬움) ~ 10->어려움): {difficulty},총 문제 갯수:  객관식 {multiple_choice}문제, 단답형 {short_answer}문제, ox문제 {ox_prob}문제"})
            print(res)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # 혹은 오류에 대한 추가 정보를 포함한 오류 객체를 반환할 수 있습니다.
    
    if not res:
        print("No response received from the API.")
        return None
    print(res)
    # 결과 데이터가 기대한 형식을 따르는지 확인


    print("-----------------")
    print(cb)
    
    return res
        
        

concept= '''
	어플리케이션 레이어
	네트워크 어플리케이션 원리
	호스트가 어플리케이션 서비스를 전달해주는 목적의 레이어
	네트워크로 의사소통
	네트워크 어플리케이션 구조s
	클라이언트 - 서버
	클라이언트 서버
•	서버
♦	정보 제공
♦	언제나 켜져있는 호스트
♦	고유 IP 주소 가짐
•	클라이언트
♦	정보 요청
♦	주로 간헐적으로 연결
♦	주로 동적 IP주소를 가짐
♦	클라이언트 끼리 상호작용하지 않음
	Peer-To-Peer(P2P)
•	서버 클라이언트 구조 아님
•	자기확장성을 가짐
•	피어는 다른 피어의 서비스를 제공
•	간헐적으로 연결되 호스트 쌍이 서로 직접 연결한다
	어플리케이션 레이어 프로토콜 정의
	메세지 유형
•	요청
•	응답
	메세지 형식
	메세지 송수신 규칙
	오픈 프로토콜
•	RCF와 같은 공개 문서를 통해 정의
•	다른 조직이나 업체에서 구현하고 사용할 수 있음
•	HTTP SMTP 등이 있다.
	공개적이지 않은 프로토콜
•	해당 조직 또는 업체의 제품 간에만 사용
•	스카이프가 이에 해당된다 
	어플리케이션 요구
	데이터 무결성
•	어떤 앱은 100%의 신뢰성 요구
•	다른 앱은 조금의 데이터 로스 허용
	타이밍
•	몇몇 앱은 적은 딜레이를 원함
	처리융(스루풋)
•	몇몇 어플은 처리율이 항상 r bps 이상인 앱이여야 한다
•	다른 어플은 처리율 제한이 없다
	보안
•	TCP vs UDP
♦	인터넷 프로토콜 스택에서 사용되는 두 가지 중요한 전송 계층 프로토콜
♦	TCP
	신뢰성 있는 전송
	데이터가 손실되거나 손상되지 않도록 보장하며, 순서대로 전달
	흐름 제어
	수신 측이 처리할 수 있는 속도에 따라 데이터의 전송 속도 전달
	혼잡 제어
	네트워크 혼잡을 감지하고 발신자의 전송 속도를 조절
	기타 요소
	타이밍, 최소 대역폭 보장, 보안, 연결 설정 등에 대한 지원을 제공하지 않음 이건 응용 프로그램 수준에서 관리해야 함
	연결 지향
	데이터 전송 전에 클라이언트와 서버 간의 연결 설정 요구
♦	UDP
	신뢰성 없는 데이터 전송
	데이터를 전송하지만, 데이터 손실이나 손상에 대한 보장을 제공하지 않음
	데이터 손실 또는 순서가 뒤섞일 수 있음
	흐름 제어 및 혼잡 제어 없음
	UDP는 흐름 제어, 혼잡 제어, 타이밍, 최소 대역폭 보장, 보안 연결설정과 같은 기능을 제공하지 않음
♦	소켓
	어플리케이션 계층과 트랜스포트 계층을 이어주는 통로
♦	주소 쳬게
	프로세스는 식별자가 필요하다
	Ipv4 기준 32bit 주소체계를 이용한다
	Ipv6는 128bit
	Ip주소가 있으면 충분할까?
	충분하지 않다
	같은 ip라도 프로세스가 많다
	프로세스를 구분하려면 포트 번호가 필요하다

'''



