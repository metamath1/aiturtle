import os, json
import turtle
from dotenv import load_dotenv
from pydantic import BaseModel
import typing_extensions as typing

from openai import OpenAI
import google.generativeai as genai

load_dotenv()

system_prompt = f"""
        SYSTEM MESSAGE
        당신은 python turtle로 각종 도형을 그리는 어시스턴트입니다.
        다음 규칙을 반드시 지켜 python 코드로 생성하시오.
        
        - 코드 생성 규칙
        1. 사용자가 색을 지정하지 않으면 기본적으로 도형은 검은색 펜으로 그리시오.
        2. 초기 위치는 중앙 (0,0)이며 turtle라이브러리는 turtle로 import되었다고 가정하기 때문에 반드시 `turtle.`을 붙이시오.
        3. 사용자가 요청한 코드는 exec()로 실행되어 사용자가 입력한 도형을  그리는데 사용되므로 파이썬 문법적으로 정확하게 생성하여야 함.
           예를들어 python코드를 나타내는 구분자 ```python```을 제외하고 출력하시오.
        4. 반드시 turtle 코드만 출력하고 기타 다른 코드 및 주석은 !!!!절대로!!!! 출력하지 마시오.
        5. 마지막에 turtle.done()은 출력하지 마시오.
        6. 다음은 사용자의 입력에 대응하는 출력의 예시임
            사용자 입력 예시: 각 변이 10인 정사각형
            출력코드 예시
            turtle.forward(10); turtle.right(90); 
            turtle.forward(10); turtle.right(90); 
            turtle.forward(10); turtle.right(90); 
            turtle.forward(10); turtle.right(90);
        7. 응답은 항상 code, aux_response를 포함합니다.
        8. code: 도형을 그리는 파이썬 코드
           aux_response: 사용자의 요구가 파이썬 코드를 사용하는 것이 아닐 경우에 대한 응답
        9. aux_response에 응답할 항목이 없으면 빈문자열을 출력합니다.
        10. 8항에서 명시한것처럼 터틀 조정에 대한 요청이 아닐 경우 aux_response에 충실히 질문에 대답해야 합니다.
        11. 복잡한 도형 요청이 오면 가능한 도형을 부분으로 분할하고 분할된 부분을 그리는 함수를 만든후
            그 함수들을 호출하여 전체 도형을 완성하시오.
        """

chatgpt = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GPT_MESSAGES = [
    {
        "role": "system", 
        "content": system_prompt
    },
]
class TurtleResponseChatGpt(BaseModel):
    code: str # 도형을 그리는 파이썬 코드
    aux_response: str # 도형을 그리는 질문에 대한 응답이 아닌 일반적인 답변 


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MESSAGES = []
# chat_gemini = genai.GenerativeModel("gemini-1.5-flash").start_chat(
#     history=GEMINI_MESSAGES
# )
gemini = genai.GenerativeModel("gemini-1.5-flash",
                      system_instruction=system_prompt)
class TurtleResponseGemini(typing.TypedDict):
    code: str # 도형을 그리는 파이썬 코드
    aux_response: str # 도형을 그리는 질문에 대한 응답이 아닌 일반적인 답변 


def invoke(model, user_input, cur_pos):
    if isinstance(model, OpenAI):
        # Update the system message with current start position
        GPT_MESSAGES.append(
            {
                "role": "user",
                "content": f"{user_input} (현재 위치: {cur_pos})"
            }
        )
        completion = model.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=GPT_MESSAGES,
            response_format=TurtleResponseChatGpt
        )

        response = completion.choices[0].message.parsed
        GPT_MESSAGES.append(
            {
                "role": "assistant",
                "content": str(response)
            }
        )
        print(GPT_MESSAGES[-2:])
        code = response.code
        code = code.replace("python", "").replace("```", "")
        aux_response = response.aux_response
    
    # elif isinstance(model, google.generativeai.generative_models.ChatSession):
    else:
        GEMINI_MESSAGES.append(
            {
                "role": "user",
                "parts": f"{user_input} (현재 위치: {cur_pos})"
            }
        )
        response = model.generate_content(
            GEMINI_MESSAGES,
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json", 
                response_schema=TurtleResponseGemini,
            )
        )
        GEMINI_MESSAGES.append(
            {
                "role": "model",
                "parts": response.text
            }
        )
        print(GEMINI_MESSAGES[-2:])
        response = json.loads(response.text)
        code = response['code']
        aux_response = response['aux_response']
    
    return code, aux_response

turtle.setup(800,800)
turtle.home()
turtle.clear()

# Initialize the start position
cur_pos = (0,0)

user_input = ""
flag = False
while True:
    if flag == False:
        user_input = input("무엇을 그리고 싶나요? (종료: exit 입력) >>> ")

    if user_input != "exit":
        code, aux_response = invoke(gemini, user_input, cur_pos)

        # 터틀 그래픽 설정
        # turtle.speed(50)  # 속도 설정 (0이 가장 빠름)
        try:
            exec(code)
            flag = False

            # 현재위치 설정
            cur_pos = turtle.pos()
            print("현재위치: ", cur_pos)
            
        except Exception as e:
            print(e) 
            flag = True
        
    else:
        break
