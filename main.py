import google.generativeai as genai
import turtle
import math

import openai

from openai import OpenAI
client = OpenAI(
    api_key=''
)

turtle.home()
turtle.clear()

# API 키 설정
# genai.configure(api_key="AIzaSyBzGZs-z4WnwlhVRA7UNyGdv-o9EDBCNsI")
# model = genai.GenerativeModel("gemini-1.5-pro")

user_input = ""
while True:
    user_input = input("무엇을 그리고 싶나요? (종료: exit 입력) >>> ")

    if user_input != "exit":
        system_prompt = f"""
        SYSTEM MESSAGE
        당신은 각 나라의 국기를 python turtle로 그리는 어시스턴트입니다.
        다음 규칙을 반드시 지켜 python 코드로 생성하세요.
        
        - 코드 생성 규칙
        1. 국기의 경계선을 반드시 검은색 펜으로 먼저 그리고 국기 내부를 채우세요.
        2. 사용자가 요청한 코드는 exec()로 실행되어 사용자가 국기를 그리는데 사용되므로 정확하게 생성하세요.
        3. 초기 위치는 중앙 (0,0)이며 turtle라이브러리는 turtle로 import되었다고 가정하기 때문에 반드시 `turtle.`을 붙이세요.
        4. 반드시 turtle 코드만 출력하고 기타 다른 코드 및 주석은 !!!!절대로!!!! 출력하지 마시오.
            예를들어 python코드를 나타내는 구분자 ```python```을 제외하고 출력하시오.
        5. 다음은 사용자의 입력에 대응하는 출력의 예시임
            사용자 입력 예시: 각 변이 10인 정사각형
            출력코드 예시
            turtle.forward(10); turtle.right(90); 
            turtle.forward(10); turtle.right(90); 
            turtle.forward(10); turtle.right(90); 
            turtle.forward(10); turtle.right(90);

        """
        
        completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""USER INPUT
###################################
{user_input}"""
                    
                }
            ]
        )

        code = completion.choices[0].message.content

        # # response = model.generate_content(
        # #     prompt, 
        # #     generation_config = genai.GenerationConfig(
        # #         temperature=0.1,
        # #     )
        # # )
        print(code)
        code = code.replace("python", "").replace("```", "")
        print(code)

        # 터틀 그래픽 설정
        # turtle.speed(50)  # 속도 설정 (0이 가장 빠름)
        exec(code)
        # turtle.done()  # 화면 유지
    else:
        break
