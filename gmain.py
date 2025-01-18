import os, json
import tkinter as tk
import turtle
from tkinter import font  # Import font module
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
gemini = genai.GenerativeModel("gemini-1.5-flash",
                      system_instruction=system_prompt)
class TurtleResponseGemini(typing.TypedDict):
    code: str # 도형을 그리는 파이썬 코드
    aux_response: str # 도형을 그리는 질문에 대한 응답이 아닌 일반적인 답변 

def execute_command(event=None):
    global  MODEL, CUR_POS
    
    # Get user input from the Text widget
    user_input = command_entry.get("1.0", "end-1c")  # Adjusted for Text widget
    
    while True:
        try:
            code, aux_response = invoke(MODEL, user_input, CUR_POS)
            exec(code)
            GEN_CODE_ERR = False

            # 현재위치 설정
            CUR_POS = turtle.pos()
            print("현재위치: ", CUR_POS)
            break
            
        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")
            GEN_CODE_ERR = True
            # 프롬프트 수정 후 다시 요청해야 하는데 
            # 수정하는 부분은 일단 보류
        finally:
            # Clear the text input field after executing the command
            command_entry.delete("1.0", "end")
        

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

def change_model(new_model, model_name):
    global MODEL, llm1_button, llm2_button
    MODEL = new_model
    status_label.config(text=f"Switched to {model_name}.", fg="green")

    if model_name == "ChatGPT":
        llm1_button.pack_forget()  # Hide ChatGPT button
        llm2_button.pack(side=tk.LEFT, padx=5)  # Show Gemini button
    else:
        llm2_button.pack_forget()  # Hide Gemini button
        llm1_button.pack(side=tk.LEFT, padx=5)  # Show ChatGPT button

# Initialize the start position
CUR_POS = (0,0)

# is there error in code generated by LLM
GEN_CODE_ERR = False

# model set
MODEL = chatgpt

# Create main Tkinter window
root = tk.Tk()
root.title("Turtle Command App")

# Define a font style
entry_font = ("Noto Sans CJK KR", 12)  # Replace with any preferred font

# Turtle canvas frame
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)

# Create a canvas and attach a TurtleScreen
canvas = turtle.ScrolledCanvas(canvas_frame, width=800, height=800)
canvas.pack(fill=tk.BOTH, expand=True)
turtle_screen = turtle.TurtleScreen(canvas)

# Create a RawTurtle
turtle = turtle.RawTurtle(turtle_screen)
# turtle.speed(1)

# Input and status frame
input_frame = tk.Frame(root)
input_frame.pack(fill=tk.X)

# Text input for commands
command_label = tk.Label(input_frame, text="Command:") #, font=entry_font)
command_label.pack(side=tk.LEFT, padx=5)

# command_entry = tk.Entry(input_frame) #, font=entry_font)
command_entry = tk.Text(input_frame, height=2)
command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
command_entry.bind("<Return>", execute_command)


# Model selection buttons
model_frame = tk.Frame(root)
model_frame.pack(fill=tk.X, pady=5)

llm1_button = tk.Button(model_frame, text="Use ChatGPT", command=lambda: change_model(chatgpt, "ChatGPT"))
llm1_button.pack_forget()

llm2_button = tk.Button(model_frame, text="Use Gemini", command=lambda: change_model(gemini, "Gemini"))
llm2_button.pack(side=tk.LEFT, padx=5)

# Status label
status_label = tk.Label(root, text="Enter a command and press Enter.", fg="blue")
status_label.pack(fill=tk.X, pady=5)

# Run the application
root.mainloop()
