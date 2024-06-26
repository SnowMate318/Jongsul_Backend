import getpass
import os, sys, re
import json
import uuid
from typing import Dict, List, TypedDict, Optional
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_community.utils.openai_functions import (
    convert_pydantic_to_openai_function,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.callbacks import get_openai_callback

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, '../jongsul'))  # 상대 경로를 사용하여 jongsul 폴더를 시스템 경로에 추가
from my_settings import OPENAI_API_KEY  # my_settings에서 OPENAI_API_KEY 가져오기 

from langsmith import traceable

class Choice(BaseModel):
    """선택지 번호와 선택지 내용을 제공"""
    choice_num: int = Field(description="선택지 번호")
    choice_content: str = Field(description="선택지 내용")

class Question(BaseModel):
    """생성한 문제를 제공"""
    question_num: int = Field(description="문제 번호")    
    question_title: str = Field(description="문제 제목")
    question_type : int = Field(description = """
                                    문제 유형
                                    1: 객관식 문제
                                    2: 단답형 문제
                                    3: OX 문제
                                """)
    choices: List[Choice] = Field(description="""
                                    question_type=1인 경우 크기가 4인 Choice 리스트를 제공
                                    question_type=2인 경우 빈 리스트를 제공
                                    question_type=3인 경우 빈 리스트를 제공
                                    
                                  """)
    question_answer: str = Field(description="문제 정답")
    question_explanation: str = Field(description="생성한 문제의 정답에 대한 설명을 답해줘")
        
class Questions(BaseModel):
    """생성한 문제 리스트를 제공"""
    questions: List[Question] = Field(description="생성한 문제 리스트")

@traceable
def getQuestions(script, multiple_choice, short_answer, ox_prob):

    gpt_model = "gpt-3.5-turbo-0125"
    # gpt_model = "gpt-4"
    model = ChatOpenAI(model=gpt_model, openai_api_key=OPENAI_API_KEY, temperature=0).bind_tools([])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
            f"당신은 입력한 개념을 이해하고 주제를 파악하여 해당 주제와 관련된 문제를 생성해주는 알고리즘입니다."
            "output is in Korean"
            "당신은 총 3가지 유형의 문제를 생성할 수 있어야 합니다. 문제 유형의 종류는 객관식 문제, 단답형 문제, OX 문제가 있습니다."
            """
            객관식 문제에 대해 설명하겠습니다.
            객관식 문제는 4가지 선택지 제공하며, 사용자가 정답을 선택할 수 있습니다.
            객관식 문제의 선택지의 번호는 1부터 4까지 제공됩니다.
            question_answer는 반드시 1부터 4까지의 번호 중 하나로 설정되어야 합니다.
            객관식 문제의 question_type은 1이 되어야 합니다.
            """
            """
            단답형 문제에 대해 설명하겠습니다.
            단답형 문제는 사용자가 질문에 대한 답을 짧게 작성할 수 있는 문제입니다.
            단답형 문제의 question_answer는 2 어절 이하여야 합니다.
            단답형 문제의 선택지 리스트는 반드시 빈 리스트가 되어야 합니다.
            단답형 문제의 question_type은 2가 되어야 합니다.
            """
            """
            OX 문제에 대해 설명하겠습니다.
            OX 문제는 주어진 문장이 참인지 거짓인지 판단하는 문제입니다.
            OX 문제의 question_title은 반드시 '(O/X)'로 마무리되어야 합니다.
            OX 문제의 question_title은 반드시 참 거짓을 판단할 수 있는 문장으로 생성되어야 합니다.
            
            몇 가지 예를 들어보겠습니다.
            eg.1
            question_title:'간접 주소 모드에서는 명령어의 주소 필드가 가리키는 주소에는 유효주소가 있다. (O/X)',
            valid: true
            
            eg.2
            question_title:'RISC는 명령어의 수가 많다는 설명이 맞는지 판단합니다.',
            valid: false
            이유: question_title은 '(O/X)'로 마무리되어야 합니다.
            
            eg.3
            question_title:'소프트웨어 공학의 제약사항 중 하나는 무엇인가? (O/X)',
            valid: false
            이유: question_title은 반드시 참 거짓을 판단할 수 있는 문장으로 생성되어야 합니다.
            
            eg.4
            question_title:'어플리케이션 레이어 프로토콜 정의 중 공개적이지 않은 프로토콜은 무엇인가?',
            valid: false
            이유: question_title은 반드시 참 거짓을 판단할 수 있는 문장으로 생성되어야 합니다. , question_title은 '(O/X)'로 마무리되어야 합니다.
            
            question_answer는 무조건 'O' 또는 'X'로 설정되어야 합니다.
            몇 가지 예를 들어보겠습니다.
            eg.1
            question_title:'간접 주소 모드에서는 명령어의 주소 필드가 가리키는 주소에는 유효주소가 있다. (O/X)',
            choices: [], 
            question_answer: 'O'  
            eg.2
            question_title:'RISC는 비교적 많은 수의 명령어를 가지고 있다. (O/X)',
            choices: [],
            question_answer: 'X'
            
            OX 문제의 question_type은 3이 되어야 합니다.
            """
            f"사용자가 입력한 개념입니다. {script}"
            ), 
            #MessagesPlaceholder("examples"),
            ("user", "{input}")]
            
    )
    
    questions = []
    chain = prompt | model.with_structured_output(schema=Questions, method="function_calling", include_raw=False,) 
    try:
        with get_openai_callback() as cb:
            if multiple_choice > 0:
                res = chain.invoke({
                "input": f''' 
                    다음과 같은 STEP을 따라 문제를 생성합니다.
                    STEP 1: 사용자가 입력한 개념의 주제를 파악합니다.
                    STEP 2: 이 주제 대해 당신이 알고있는 지식과, 개념 내용을 바탕으로 문제 생성을 준비합니다.
                    STEP 3: 객관식 문제를 {multiple_choice}개 생성합니다.
                    STEP 4: 생성한 문제에 대한 정답과 해설을 제공합니다.
                    ''',
                })
                questions = res.questions
            if short_answer > 0:
                res = chain.invoke({
                "input": f''' 
                    다음과 같은 STEP을 따라 문제를 생성합니다.
                    STEP 1: 사용자가 입력한 개념의 주제를 파악합니다.
                    STEP 2: 이 주제 대해 당신이 알고있는 지식과, 개념 내용을 바탕으로 문제 생성을 준비합니다.
                    STEP 3: 단답형 문제를 {short_answer}개 생성합니다.
                    STEP 4: 생성한 문제에 대한 정답과 해설을 제공합니다.
                    ''',
                })
                questions.extend(res.questions)
            if ox_prob > 0:
                res = chain.invoke({
                "input": f''' 
                    다음과 같은 STEP을 따라 문제를 생성합니다.
                    STEP 1: 사용자가 입력한 개념의 주제를 파악합니다.
                    STEP 2: 이 주제 대해 당신이 알고있는 지식과, 개념 내용을 바탕으로 문제 생성을 준비합니다.
                    STEP 3: OX 문제를 {ox_prob}개 생성합니다.
                    STEP 4: 생성한 문제에 대한 정답과 해설을 제공합니다.
                    ''',
                })
                questions.extend(res.questions)
                
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # 혹은 오류에 대한 추가 정보를 포함한 오류 객체를 반환할 수 있습니다.
        
    if not res:
        print("No response received from the API.")
        return None
        
        # 결과 데이터가 기대한 형식을 따르는지 확인

    # questions 리스트를 딕셔너리 리스트로 변환
    print(questions)
    # JSON으로 변환
    json_output = convert_pydantic_list_to_json(questions)
    print("-----------------")
    print(json_output) 
    # 결과 출력
    print("-----------------")
    print(cb)
    

       
    return json_output

def convert_pydantic_list_to_json(pydantic_list: List[BaseModel]) -> str:
    return [item.dict() for item in pydantic_list]
concept1= '''
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

concept2 = '''소웨공 개념
v
v
v
1.1 소프트웨어
Ø 프로그램 + 프로그램의 개발, 운용, 보수에 필요한 정보 일체
개념적, 무형적
추가적 소프트웨어의 특징
Ø 극히 적은 비용으로 복제 가능
Ø 소프트웨어의 비마모성(오래쓴다고 닳지않음) Ø 노동집약성
Ø 고치기 힘듦
Ø 품질 높이기 쉽지않음
Ø 잘 훈련받지않으면 제작 어려움
Ø 코드가 누적되면 오류율 높아짐
소프트웨어의 종류
Ø 주문형 소프트웨어
§ 특정 고객의 수요를 만족시키기 위해 개발된 소프트웨어 § 장점:특정고객수요만족가능
§ 단점: 사용자가 한정되고 비용이 많이 듦
Ø 패키지형 소프트웨어
§ 공개된 시장에서 판매되는 소프트웨어, COTS라고도 불림 § 장점: 저렴하고 신뢰도 높음(다수의 베타테스터)
§ 단점: 특정기관의 요구에 최적화되지 않음
v
Ø 임베디드 소프트웨어
§ 장점: 개발 비용이 비교적 저렴
§ 단점: 하드웨어 교체하지 않은 이상 소프트웨어 교체 어려움
소프트웨어 공학의 정의 v 소프트웨어 공학
Ø 고객의 문제를 해결해주기 위해 대규모의 품질좋은 소프트웨어 시스템을 정해진 시 간과 비용으로 개발하거나 발전시키는 체계적인 프로세스
Ø 소프트웨어 개발에 사용되는 방법이 일회성이 아닌 반복 사용 가능 v 소프트웨어 공학의 제약사항
Ø 비용, 시간, 기타 제약
§ 한정된 자원(시간, h/w, 인력, 돈)
§ 얻는 이득이 비용을 초과해야 함
§ 더빠르고싸게개발하도록다른기업과경쟁
§ 비용과 시간의 부정확한 예측으로 대부분의 프로젝트가 실패
v 소프트웨어 공학의 목표 Ø 복잡도 낮춤
Ø 비용 최소화
Ø 개발기간 단축
Ø 대규모 프로젝트 관리 Ø 고품질 소프트웨어
Ø 효율성 증가
v 소프트웨어 공학의 주제

Ø 단계적 프로세스
§ 소프트웨어에 대한 비전과 개념을 파악하고 만족하는 소프트웨어로 구현될 때까
지 정해진 순서 반복(요구사항 명세, 설계, 구현, 테스팅 등 단계적 절차) Ø 품질 보증
§ 소프트웨어의 품질 보증(Software Quality Assurance)는 개발작업의 적절한 수행 여부를 확인하는 작업
Ø 프로젝트 관리
§ 개발과 품질보증 작업을 관리하고 감독하는 일(예측, 프로젝트 계획, 일정, 리스 트 관리, 행정 등'''

concept3 = '''1. 선사시대 및 고대
구석기 - 뗀석기, 주먹도끼, 사냥 및 채집
신석기 - 간석기, 빗살무늬 토기, 가락바퀴, 움집, 농경시작
청동기 - 비파형 동검, 농경 및 목축 확대, 일부지역 벼농사, 고인돌
고구려 : 5부족 연맹. 국내성 천도, 서옥제, 고분벽화 별자리
- 태조 : 옥저 정복
- 미천왕 : 낙랑군 축출
- 소수림왕 : 태학 설립, 율령 반포
- 광개토 대왕 : 만주 정복
- 장수왕 : 남진정책(평양 천도)
백제 : 22담로, 백제 금동 대향로
- 문주왕 : 웅진(공주) 천도
- 성왕 : 사비 천도
신라 : 화랑도, 나 당 전쟁 - 삼국 통일, 첨성대
통일 신라 : 집사부, 시중 강화, 상수리 제도(지방 견제), 6두품, 관료전 지급 및 녹읍
폐지, 정전 지급, 독서 삼품과, 무구정광대다리니경, 불국사 3층 석탑, 장보고 청해진
설립
발해 : 대조영 건국, 독자적 연호, 해동성국, 3성 6부, 5경 15부 62주, 고구려 계승, 주자감 설치(교육)
2. 고려시대
태조 : 북진 정책(서경 중시), 훈요 10조
광종 : 노비안검법, 과거제, 황제 칭호 및 독자적 연호
성조 : 최승로 시무 28조, 12목 설치, 지방관 파견, 향리 제도
중앙 통치 조직 : 2성 6부(중서문하성-문하시중, 상서성-6부), 중추원, 삼사, 도병마
사, 식목도감
지방 행정 조직 : 5도(일반), 양계(군사)
거란 침입 - 1차 : 서희 담판외교, 3차 - 강감찬 귀주대첩 -> 천리장성 축조
여진 관계
- 별무반 창설(윤관), 동북 9성 설치, 금과의 군신관계(이자겸 등 문벌귀족세력 등장)
문벌귀족 사회 : 공음전, 음서제도, 이자겸의 난
서경 천도 운동(묘청) : 김부식(관군세력)이 진압
무신정권(이의방, 정중부) : 중방을 중심으로 권력 행사
- 원인 : 무신 차별대우
최씨 무신정권 : 최충헌 - 교정도감 설치, 최우 - 삼별초 설치
몽골 항쟁 : 강화도 천도, 처인성 전투(김윤후, 살리타 사망), 충주성 전투(하충민), 최
씨정권 몰락, 개경 환도, 삼별초 항쟁, 황룡사 9층 목탑, 초조대장경 등 소실 + 팔만
대장경 제작
원 내정간섭 : 2성 6부 -> 1부 4사, 쌍성총관부 등 소실, 정동행성(내정 간섭기구),
다루가치 파견, 공녀요구, 권문세족 성장
공민왕 : 전민변정도감 설치, 친원 숙청, 정동행성 이문소 폐지, 쌍성총관부 공격 및
영토회복, 신진사대부 성장
농업 : 2년 3작, 고려 말 일부 모내기법, 농상집요, 화폐 : 건원중보, 삼한통보, 해동통보, 은병
상업 : 벽란도 - 아라비아 상인과 교류(코리아)
기타 용어 : 혜민국, 삼국사기(김부식, 전기), 삼국유사(후기)'''

concept4 = '''기본 컴퓨터에서 메모리는 다음 용도로 사용됩니다:
•	포인터, 카운터, 반환 주소 등
•	곱셈 중 임시 결과, 부분적인 결과 등 • 메모리 접근 시간 >> 레지스터 접근 시간
•	더 많은 레지스터가 필요합니다.
•	CPU에 더 많은 레지스터가 있으면 성능이 향상됩니다. • 많은 수의 레지스터를 어떻게 연결할 수 있을까요?
이제 각 항목에 대해 자세히 설명해보겠습니다.
1.	메모리의 용도:
o	포인터, 카운터, 반환 주소 등: 메모리는 다양한 중요한 데이터를 저장하는 데 사용됩니다. 예를 들어, 포인터는 메모리의 특정 위치를 가리키는 데 사용되고, 카운터는 반복 작업의 횟수를 세는 데 사용됩니다. 반환 주소는 함수 호출 후 복귀할 위치를 저장하는 데 사용됩니다.
o	임시 결과, 부분적인 결과 등: 메모리는 복잡한 계산 중간 결과를 저장하는 데도 사용됩니다. 예를 들어, 곱셈 과정에서 나오는 부분적인 결과를 저장하는 데 사용됩니다. 이는 연산을 단계별로 처리하는 데 필요합니다.
2.	메모리 접근 시간과 레지스터 접근 시간:
o	메모리 접근 시간 >> 레지스터 접근 시간: 메모리에 데이터를 읽거나 쓰는 데 걸리는 시간은 레지스터보다 훨씬 깁니다. 이는 메모리가 물리적으로 더 멀리 있고, 구조적으로 더 복잡하기 때문입니다.
o	더 많은 레지스터 필요: 따라서 더 많은 데이터를 빠르게 처리하기 위해 CPU 내부에 더 많은 레지스터가 필요합니다.
o	CPU에 더 많은 레지스터가 있으면 성능 향상: 레지스터는 CPU 내부에 있어 접근 시간이 매우 짧기 때문에, 더 많은 레지스터를 사용하면 성능이 향상됩니다.


3.	많은 수의 레지스터 연결 방법
o	다중 버스 구조: 여러 레지스터를 연결하는 한 가지 방법은 다중 버스를 사용하는 것입니다. 다중 버스 구조는 여러 데이터 버스를 통해 레지스터와 메모리 간의 데이터 전송을 병렬로 처리할 수 있어 성능을 향상시킵니다.
o	레지스터 파일: 또 다른 방법은 레지스터 파일을 사용하는 것입니다. 레지스터 파일은 여러 레지스터를 하나의 논리적 블록으로 묶어 관리합니다. 이를 통해 필요한 레지스터를 빠르게 선택하고 접근할 수 있습니다.
o	하드웨어 멀티플렉서: 멀티플렉서를 사용하여 여러 레지스터 중에서 하나를 선택하고 데이터를 전송할 수 있습니다. 이는 복잡한 연결을 단순화하고 효율적으로 만들 수 있습니다.

Implied 모드
피연산자가 묵시적으로 명령어의 정의에 따라 정해져있음
Ex) ‘누군가의 보수를 취하라’ -> 피연산자가 누산기에 있기 때문에 implied 모드가 되며, 누산기를 사용하는 모든 명령어는 Implied 명령어다
스택 구조일 경우, 피연산자가 스택의 top 이기 때문에 implied 명령어다.

Immediate 모드
이 모드에서는 피연산자가 명령어 그 자체 내에 있다.
주소 필드라기보다도 피연산자 필드를 가지게 된다.
상수 레지스터에 초기 값으로 줄 때 편리하다
 *명령어의 주소 필드는 메모리의 주소나 레지스터를 지정하는것은 레지스터 모드이다.

레지스터 모드
레지스터 모드는 cpu 내의 레지스터에 피연산자가 있다.
2^k 레지스터 중 하나를 선택할 수 있다.

레지스터 간접 모드
명령어가 피연산자의 주소를 가지고있는 레지스터를 지정
선택된 레지스터는 피연산자가 아닌 피연산자의 주소이다.
적은 비트가 든다는 장점이 있지만 피연산자 access time이 증가한다.

자동증가 또는 자동감소 모드
레지스터 값이 메모리를 엑세스하고 난 직후 자동적으로 하나 증가하거나 감소한다는 것을 제외하면 레지스터. 간접 모드와 같다
메모리가 있는 데이터가 어떤 표라면, 편하다

유효 주소(EA, Effective Address)
주어진 주소 지정 모드에 따라 계산된 주소
연산 유형 명령어에서 피연산자의 주소
분기 유형 명령어에서 제어가 분기되는 주소

직접 주소 모드
명령어의 주소 부분이 그대로 유효 명령어의 주소 필드에 의해 직접적으로 주어진다
분기(branch) 형식의 명령어에서는 실제 분기할 주소를 나타낸다

간접 주소 모드
간접 주소 모드에서는 명령어의 주소 필드가 가리키는 주소에는 유효주소가 있다.
이 명령어를 수행할 때에는 메모리로부터 명령어를 fetch하고 그것의 주소 부분으로부터 다시 유효 주소를 메모리에서 가져와서 연산한다.
유효 주소 = 명령어에서의 주소 부분 + CPU 내의 현재 레지스터의 값
이때 CPU의 레지스터는 프로그램 카운터나 인덱스 레지스터나 베이스 레지스터가 될 수 있다.

상대 주소 모드
프로그램 카운터가 명령어의 주소 부분과 더해져서 유효 주소가 결정된다.
명령어의 주소 부분은 보통 기호를 포함한 수(2의 보수 표현)이며 음수나 양수 둘 다 될 수 있다.
이 숫자가 프로그램 카운터에 더해져서 유효 주소가 된다.

베이스 레지스터 어드레싱 모드
베이스 레지스터의 내용이 명령어의 주소 부분에 더해져서 유효 주소가 결정된다.
인덱스드 어드레싱 모드와의 차이점: 인덱스 레지스터 대신 베이스 레지스터가 사용되었다.
인덱스 레지스와 쓰임새에서 차이점이 있다.
인덱스 레지스터는 주소 부분에 대한 상대적인 위치를 가지고 있음에 반해, 베이스 레지스터는 베이스 주소를 가지고 있고, 명령어의 주소 부분은 이 베이스 주소로부터의 상대적인 displacement가 된다.
프로그램이나 데이터가 메모리의 한 세그먼트로부터 다른 세그먼트로 옮겨질 때, 명령어의 주소는 이러한 위치의 변경을 반영해야한다.
베이스 레지스터가 있다면 명령어의 displacement는 변경될 필요가 없다
베이스 레지스터 값이 다른 메모리 세그먼트의 시작 부분을 참고로 해서 변경하면 된다.


복잡한 명령 집합 컴퓨터 (CISC)
크고 느린 명령어 사용
-	많은 수의 명령어 (일반적으로 100~250개)
-	특수 작업을 수행 목적 또는 자주 사용되지않는 일부 명령어
-	다양한 주소 지정 (어드레싱모드 5~20개)
-	가변 길이 명령어 형식
-	메모리의 피연산자를 조작

설계 및 구현에서의 어려움
-	복잡한 마이크로프로그래밍
-	느린 실행

축소 명령어 집합 컴퓨터 (RISC)
하드와이어드 제어를 사용한 단일 사이클 실행
-	비교적 적은 수의 명령어
-	비교적 적은 수의 주소 지정 모드
-	메모리 접근이 로드 및 스토어 명령어로 제한
-	모든 연산은 CPU의 레지스터 내에서 수행
-	고정 길이, 쉽게 해독할 수 있는 명령어 형식
-	강력한 파이프라인
-	단일 사이클 명령어 실행
-	마이크로프로그래밍이 아닌 하드와이어드 제어
컴파일러는 작지만 빠른 명령어를 사용

'''

@traceable
def getQuestions(script, multiple_choice, short_answer, ox_prob):

    gpt_model = "gpt-3.5-turbo-0125"
    # gpt_model = "gpt-4"
    model = ChatOpenAI(model=gpt_model, openai_api_key=OPENAI_API_KEY, temperature=0).bind_tools([])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
            f"당신은 입력한 개념을 이해하고 주제를 파악하여 해당 주제와 관련된 문제를 생성해주는 알고리즘입니다."
            "output is in Korean"
            "당신은 총 3가지 유형의 문제를 생성할 수 있어야 합니다. 문제 유형의 종류는 객관식 문제, 단답형 문제, OX 문제가 있습니다."
            """
            객관식 문제에 대해 설명하겠습니다.
            객관식 문제는 4가지 선택지 제공하며, 사용자가 정답을 선택할 수 있습니다.
            객관식 문제의 선택지의 번호는 1부터 4까지 제공됩니다.
            question_answer는 반드시 1부터 4까지의 번호 중 하나로 설정되어야 합니다.
            객관식 문제의 question_type은 1이 되어야 합니다.
            """
            """
            단답형 문제에 대해 설명하겠습니다.
            단답형 문제는 사용자가 질문에 대한 답을 짧게 작성할 수 있는 문제입니다.
            단답형 문제의 question_answer는 2 어절 이하여야 합니다.
            단답형 문제의 선택지 리스트는 반드시 빈 리스트가 되어야 합니다.
            단답형 문제의 question_type은 2가 되어야 합니다.
            """
            """
            OX 문제에 대해 설명하겠습니다.
            OX 문제는 주어진 문장이 참인지 거짓인지 판단하는 문제입니다.
            OX 문제의 문장의 끝은 '(O/X)'로 마무리되어야 합니다.
            OX 문제의 제목은 반드시 참 거짓을 판단할 수 있는 문장으로 생성되어야 합니다.
            몇 가지 예를 들어보겠습니다.  
            question_title: 'UDP는 데이터의 신뢰성을 보장하지 않는다. (O/X)' valid: true    
            question_title: 'TCP 프로토콜은 어떤 특징을 가지고 있나요? (O/X)' valid: false   question_title: 'RISC는 비교적 많은 수의 명령어를 가지고 있다. (O/X)' valid: true   question_title:'다중 버스 구조는 레지스터와 메모리 간의 데이터 전송을 어떻게 처리하는가? (O/X)', valid: false
            OX 문제의 선택지 리스트는 반드시 빈 리스트가 되어야 합니다.
            question_answer는 무조건 'O' 또는 'X'로 설정되어야 합니다.
            몇 가지 예를 들어보겠습니다.
            question_title:'간접 주소 모드에서는 명령어의 주소 필드가 가리키는 주소에는 유효주소가 있다. (O/X)',choices: [], question_answer: 'O'  question_title:'RISC는 비교적 많은 수의 명령어를 가지고 있다. (O/X)',choices: [], question_answer: 'X'
            OX 문제의 question_type은 3이 되어야 합니다.
            """
            f"사용자가 입력한 개념입니다. {script}"
            ), 
            #MessagesPlaceholder("examples"),
            ("user", "{input}")]
            
    )
    
    questions = []
    chain = prompt | model.with_structured_output(schema=Questions, method="function_calling", include_raw=False,) 
    try:
        with get_openai_callback() as cb:
            if multiple_choice > 0:
                res = chain.invoke({
                "input": f''' 
                    다음과 같은 STEP을 따라 문제를 생성합니다.
                    STEP 1: 사용자가 입력한 개념의 주제를 파악합니다.
                    STEP 2: 이 주제 대해 당신이 알고있는 지식과, 개념 내용을 바탕으로 문제 생성을 준비합니다.
                    STEP 3: 객관식 문제를 {multiple_choice}개 생성합니다.
                    STEP 4: 생성한 문제에 대한 정답과 해설을 제공합니다.
                    ''',
                })
                questions = res.questions
            if short_answer > 0:
                res = chain.invoke({
                "input": f''' 
                    다음과 같은 STEP을 따라 문제를 생성합니다.
                    STEP 1: 사용자가 입력한 개념의 주제를 파악합니다.
                    STEP 2: 이 주제 대해 당신이 알고있는 지식과, 개념 내용을 바탕으로 문제 생성을 준비합니다.
                    STEP 3: 단답형 문제를 {short_answer}개 생성합니다.
                    STEP 4: 생성한 문제에 대한 정답과 해설을 제공합니다.
                    ''',
                })
                questions.extend(res.questions)
            if ox_prob > 0:
                res = chain.invoke({
                "input": f''' 
                    다음과 같은 STEP을 따라 문제를 생성합니다.
                    STEP 1: 사용자가 입력한 개념의 주제를 파악합니다.
                    STEP 2: 이 주제 대해 당신이 알고있는 지식과, 개념 내용을 바탕으로 문제 생성을 준비합니다.
                    STEP 3: OX 문제를 {ox_prob}개 생성합니다.
                    STEP 4: 생성한 문제에 대한 정답과 해설을 제공합니다.
                    ''',
                })
                questions.extend(res.questions)
                
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # 혹은 오류에 대한 추가 정보를 포함한 오류 객체를 반환할 수 있습니다.
        
    if not res:
        print("No response received from the API.")
        return None
        
        # 결과 데이터가 기대한 형식을 따르는지 확인

    # questions 리스트를 딕셔너리 리스트로 변환
    print(questions)
    # JSON으로 변환
    json_output = convert_pydantic_list_to_json(questions)
    print("-----------------")
    print(json_output) 
    # 결과 출력
    print("-----------------")
    print(cb)
    

       
    return json_output

concepts = [concept1, concept2, concept3, concept4]

def testQuestion():
    testdata = getQuestions(concept1,4,3,3)
    for concept in concepts:
        testdata = getQuestions(concept, 4,3,3)
        print(testdata)
        testdata = getQuestions(concept, 10,0,0)
        print(testdata)
        testdata = getQuestions(concept, 0,10,0)
        print(testdata)
        testdata = getQuestions(concept, 0,0,10)
        print(testdata)
        
    
def validator(testdata):
    return 