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
sys.path.append('jongsul')  # jongsul 폴더를 시스템 경로에 추가
from my_settings import OPENAI_API_KEY  # my_settings에서 OPENAI_API_KEY 가져오기



class Choice(BaseModel):
    """선택지 번호와 선택지 내용을 제공"""
    choice_num: int = Field(description="선택지 번호")
    choice_content: str = Field(description="선택지 내용")

class Question(BaseModel):
    """생성한 문제를 제공"""
    question_num: int = Field(description="문제번호")    
    question_title: str = Field(description="문제 제목")
    question_type : int = Field(description = "객관식:1, 주관식: 2, ox: 3")
    choices: List[Choice] = Field(description="객관식일 경우 선택지를 제공, 아닐 경우 []")
    question_answer: str = Field(description="문제 정답 객관식의 경우 (1, 2, 3, 4), 주관식의 경우 정답 내용, ox의 경우 O or X")
    question_explanation: str = Field(description="생성한 문제의 정답에 대한 설명을 답해줘")
        
class Questions(BaseModel):
    """Extracted data about question."""
    questions: List[Question]
    
class Example(TypedDict):
    """A representation of an example consisting of text input and expected tool calls.

    For extraction, the tool calls are represented as instances of pydantic model.
    """

    input: str  # This is the example text
    tool_calls: List[BaseModel]  # Instances of pydantic model that should be extracted


def tool_example_to_messages(example: Example) -> List[BaseMessage]:
    """Convert an example into a list of messages that can be fed into an LLM.

    This code is an adapter that converts our example to a list of messages
    that can be fed into a chat model.

    The list of messages per example corresponds to:

    1) HumanMessage: contains the content from which content should be extracted.
    2) AIMessage: contains the extracted information from the model
    3) ToolMessage: contains confirmation to the model that the model requested a tool correctly.

    The ToolMessage is required because some of the chat models are hyper-optimized for agents
    rather than for an extraction use case.
    """
    messages: List[BaseMessage] = [HumanMessage(content=example["input"])]
    openai_tool_calls = []
    for tool_calls in example["tool_calls"]:
        for tool_call in tool_calls:
            openai_tool_calls.append(
            {
                "id": str(uuid.uuid4()),
                "type": "function",
                "function": {
                    "name": tool_call.__class__.__name__,
                    "arguments": tool_call.json(),
                },
            }
        )
    messages.append(
        AIMessage(content="", additional_kwargs={"tool_calls": openai_tool_calls})
    )
    tool_outputs = example.get("tool_outputs") or [
        "You have correctly called this tool."
    ] * len(openai_tool_calls)
    for output, tool_call in zip(tool_outputs, openai_tool_calls):
        messages.append(ToolMessage(content=output, tool_call_id=tool_call["id"]))
    return messages

def extract_json(message: AIMessage) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json and ``` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    text = message.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        raise ValueError(f"Failed to parse: {message}")
            
def getQuestions(script, difficulty, multiple_choice, short_answer, ox_prob, all_prob):
 
    #gpt_model = "gpt-4"
    examples = [
        
            (
            f'''
            개념: {concept}, 
            난이도: 7,
            문제갯수: 객관식 1문제, 단답형 1문제, ox문제 1문제.

            ''',                
            [Question(
                question_num=1,
                question_type=1,
                question_title="TCP와 UDP의 차이점은 무엇인가요?",
                choices=[
                    Choice(choice_num=1, choice_content="신뢰성 있는 전송 vs 신뢰성 없는 전송"),
                    Choice(choice_num=2, choice_content="흐름 제어 및 혼잡 제어 vs 흐름 제어 및 혼잡 제어 없음"),
                    Choice(choice_num=3, choice_content="연결 지향 vs 연결 설정 없음"),
                    Choice(choice_num=4, choice_content="데이터 손실이나 손상에 대한 보장 vs 데이터 손실이나 손상에 대한 보장을 제공하지 않음"),
                ],
                question_answer=1,
                question_explanation="TCP는 신뢰성 있는 전송을 제공하고 데이터의 손실이나 손상을 보장합니다. UDP는 신뢰성 없는 전송을 하며 데이터 손실이나 손상에 대한 보장을 제공하지 않습니다."
                ),
            Question(
                question_num=2,
                question_type=2,
                question_title="TCP와 UDP 중에서 연결 지향적인 프로토콜은 무엇인가요?",
                choices=[],
                question_answer="TCP",
                question_explanation="TCP는 연결 지향적인 프로토콜이며, 데이터 전송 전에 클라이언트와 서버 간의 연결 설정이 요구됩니다."
                ),
            Question(
                question_num=3,
                question_type=3,
                question_title="TCP는 연결 지향적인 프로토콜인가요? (O/X)",
                choices=[],
                question_answer="O",
                question_explanation="TCP는 연결 지향적인 프로토콜입니다. 데이터 전송 전에 클라이언트와 서버 간의 연결 설정이 요구됩니다."
                )]
        ),
        (
            f'''
            개념: {concept}, 
            난이도: 7,
            문제갯수: 객관식 2문제, 단답형 3문제, ox문제 3문제.

            ''',                
            [Question(
                question_num=1, 
                question_title='TCP와 UDP의 차이점은 무엇인가요?', 
                question_type=1, 
                choices=[
                    Choice(choice_num=1, choice_content='신뢰성 있는 전송 vs 신뢰성 없는 전송'), 
                    Choice(choice_num=2, choice_content='흐름 제어 및 혼잡 제어 vs 흐름 제어 및 혼잡 제어 없음'), 
                    Choice(choice_num=3, choice_content='연결 지향 vs 연결 설정 없음'), 
                    Choice(choice_num=4, choice_content='데이터 손실이나 손상에 대한 보장 vs 데이터 손실이나 손상에 대한 보장을 제공하지 않음')
                ], 
                question_answer='1', 
                question_explanation='TCP는 신뢰성 있는 전송을 제공하고 데이터의 손실이나 손상을 보장합니다. UDP는 신뢰성 없는 전송을 하며 데이터 손실이나 손상에 대한 보장을 제공하지 않습니다.'
            ),
            Question(
                question_num=2, 
                question_title='TCP와 UDP 중에서 연결 지향적인 프로토콜은 무엇인가요?', 
                question_type=2, 
                choices=[], 
                question_answer='TCP', 
                question_explanation='TCP는 연결 지향적인 프로토콜이며, 데이터 전송 전에 클라이언트와 서버 간의 연결 설정이 요구됩니다.'
            ),
            Question(
                question_num=3, 
                question_title='TCP는 연결 지향적인 프로토콜인가요? (O/X)', 
                question_type=3, 
                choices=[], 
                question_answer='O', 
                question_explanation='TCP는 연결 지향적인 프로토콜입니다. 데이터 전송 전에 클라이언트와 서버 간의 연결 설정이 요구됩니다.'
            ),
            Question(
                question_num=4, 
                question_title='TCP 프로토콜에서 제공되는 기능은 무엇인가요?', 
                question_type=1, 
                choices=[
                    Choice(choice_num=1, choice_content='신뢰성 있는 전송, 흐름 제어, 혼잡 제어, 연결 설정'), 
                    Choice(choice_num=2, choice_content='데이터 손실이나 손상에 대한 보장, 흐름 제어, 혼잡 제어, 타이밍'), 
                    Choice(choice_num=3, choice_content='신뢰성 있는 전송, 흐름 제어, 혼잡 제어, 기타 요소'), 
                    Choice(choice_num=4, choice_content='연결 지향, 데이터 손실이나 손상에 대한 보장, 흐름 제어, 혼잡 제어')
                ], 
                question_answer='1', 
                question_explanation='TCP 프로토콜은 신뢰성 있는 전송, 흐름 제어, 혼잡 제어, 연결 설정 기능을 제공합니다.'
            ),
            
            Question(
                question_num=5,
                question_title='IPv4 주소체계에서는 몇 비트의 주소를 사용하나요?',
                question_type=2,
                choices=[],
                question_answer='32bit',
                question_explanation='IPv4 주소체계에서는 32비트의 주소를 사용합니다.'
            ),
            Question(
                question_num=6, 
                question_title='프로세스를 구분하기 위해 사용되는 것은 무엇인가요?', 
                question_type=2, 
                choices=[], 
                question_answer='포트 번호', 
                question_explanation='프로세스를 구분하기 위해 포트 번호가 사용됩니다.'
            ),
            Question(
                question_num=7, 
                question_title='TCP 프로토콜은 흐름 제어와 혼잡 제어를 제공하나요? (O/X)', 
                question_type=3, 
                choices=[], 
                question_answer='O', 
                question_explanation='TCP 프로토콜은 흐름 제어와 혼잡 제어를 제공합니다.'
            ),
            Question(
                question_num=8, 
                question_title='UDP 프로토콜은 연결 지향적인 프로토콜인가요? (O/X)', 
                question_type=3, 
                choices=[], 
                question_answer='X', 
                question_explanation='UDP 프로토콜은 연결 지향적인 프로토콜이 아닙니다.'
            )
        ]
        ),
        (
            f'''
            개념: {concept2}, 
            난이도: 7,
            문제갯수: 객관식 1문제, 단답형 2문제, ox문제 2문제.

            ''',                
            [
            
            Question(
                question_num=1,
                question_title='소프트웨어의 종류 중 패키지형 소프트웨어의 장단점은 무엇인가요?',
                question_type=1,
                choices=[
                    Choice(choice_num=1, choice_content='저렴하고 신뢰도 높음 / 특정기관의 요구에 최적화되지 않음'),
                    Choice(choice_num=2, choice_content='특정고객수요만족가능 / 사용자가 한정되고 비용이 많이 듦'),
                    Choice(choice_num=3, choice_content='개발 비용이 비교적 저렴 / 소프트웨어 교체 어려움'),
                    Choice(choice_num=4, choice_content='특정고객수요만족가능 / 개발 비용이 비교적 저렴')
                ],
                question_answer='1',
                question_explanation='패키지형 소프트웨어는 저렴하고 신뢰도가 높으며 다수의 베타테스터를 통해 검증되는 장점이 있지만 특정기관의 요구에 최적화되지 않는 단점이 있습니다.'
            ),
            Question(
                question_num=2,
                question_title='소프트웨어 공학의 목표 중 하나는 무엇인가요?',
                question_type=2,
                choices=[],
                question_answer='복잡도 낮춤',
                question_explanation='소프트웨어 공학의 목표 중 하나는 복잡도를 낮추는 것입니다.'
            ),
            Question(
                question_num=3,
                question_title='소프트웨어 공학의 주제 중 하나는 무엇인가요?',
                question_type=2,
                choices=[],
                question_answer='품질 보증',
                question_explanation='소프트웨어 공학의 주제 중 하나는 품질 보증입니다.'
            ),
            
            Question(
                question_num=4,
                question_title='소프트웨어 공학의 정의에 대한 설명 중 틀린 것은 무엇인가요?',
                question_type=3,
                choices=[],
                question_answer='X',
                question_explanation='소프트웨어 공학은 고객의 문제를 해결하기 위해 대규모의 품질 좋은 소프트웨어 시스템을 개발하거나 발전시키는 체계적인 프로세스를 의미합니다.'
            ),
            Question(
                question_num=5,
                question_title='소프트웨어의 특징 중 노동집약성을 가지고 있는 소프트웨어는 무엇인가요? (O/X)',
                question_type=3,
                choices=[],
                question_answer='O',
                question_explanation='소프트웨어는 노동집약성을 가지고 있습니다.'
            )
        ]
            
            
          
        ),
    ]
    messages = []

    for text, tool_call in examples:
        messages.extend(
            tool_example_to_messages({"input": text, "tool_calls": [tool_call]})
        )
    gpt_model = "gpt-3.5-turbo-0125"
    model = ChatOpenAI(model=gpt_model, openai_api_key=OPENAI_API_KEY, temperature=0).bind_tools([])


    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
            "입력한 개념을 기반으로 문제를 만들어주는 알고리즘이야. "
            "1~10까지의 난이도를 설정할 수 있어. 1은 쉬운 문제, 10은 어려운 문제야."
            "문제의 갯수를 설정할 수 있어. 객관식, 단답형, ox문제의 유형 별 갯수를 설정할 수 있어."
            "예를 들어 문제갯수: 객관식 4문제, 단답형 3문제, ox문제 2문제.'라고 해줘."

            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
            ), 
            MessagesPlaceholder("examples"),
            ("user", "{input}")]
            
    )
    
    
    chain = prompt | model.with_structured_output(schema=Questions, method="function_calling", include_raw=False,) 
    try:
        with get_openai_callback() as cb:
            res = chain.invoke({
                "input": f''' 
                개념: {concept2}, 
                난이도: {difficulty},
                문제갯수: 객관식 {multiple_choice}문제, 단답형 {short_answer}문제, ox문제 {ox_prob}문제.
                ''',
                "examples": messages,
                })
                #print(res)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # 혹은 오류에 대한 추가 정보를 포함한 오류 객체를 반환할 수 있습니다.
        
    if not res:
        print("No response received from the API.")
        return None
        
        # 결과 데이터가 기대한 형식을 따르는지 확인

    def to_dict(obj):
        if isinstance(obj, list):
            return [to_dict(i) for i in obj]
        elif hasattr(obj, "__dict__"):
            return {key: to_dict(value) for key, value in obj.__dict__.items()}
        else:
            return obj

    # questions 리스트를 딕셔너리 리스트로 변환
    print(res)
    print("-----------------")
    questions_dict = to_dict(res)

    # 딕셔너리 리스트를 JSON 문자열로 변환
    questions_json = json.dumps(questions_dict, ensure_ascii=False, indent=4)

    # 결과 출력
    print(questions_json)
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
#getQuestions(concept3, 5, 2, 3, 1, 6)