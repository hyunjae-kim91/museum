import gradio as gr
import os
from PIL import Image
import json
import pandas as pd
from dotenv import load_dotenv

from chat_completion import chatCompletion
from qa_from_document import qaDocuments

load_dotenv()

cache = {}

product_df = pd.read_csv('src/product_map.csv', index_col=False, sep='|')
product_list = product_df['product'].to_list()

def get_image(path: str, image_file_name: str):
    image_path = f'{path}/{image_file_name}'
    if os.path.exists(image_path):
        image = Image.open(image_path)  
    else:
        image = None  
    return image

def get_product_info(product_name: str):
    product_df = pd.read_csv('src/product_map.csv', index_col=False, sep='|')
    product_info = product_df[product_df['product']==product_name]
    product_json = json.loads(product_info.to_json(orient="records", force_ascii=False))[0]
    return product_json

def download_caption():
    return "caption.txt", result_caption.value

def get_text(path, file_name):
    description_path = f"{path}/{file_name}"
    if os.path.exists(description_path):
        with open(description_path, "r", encoding="utf-8") as desc_file:
            description = desc_file.read()
    else:
        description = "No description available."
    return description

def display_item(product_name):
    qa_document = qaDocuments()
    product_info = get_product_info(product_name)

    document_file_name = product_info.get('document_file_name')

    prompt_folder = product_info.get('prompt_folder_name')
    prompt_path = f'src/prompts/{prompt_folder}'

    prompt_01 = get_text(path=prompt_path, file_name='query_01.txt')
    prompt_02 = get_text(path=prompt_path, file_name='query_02.txt')
    prompt_03 = get_text(path=prompt_path, file_name='query_03.txt')
    prompt_04 = get_text(path=prompt_path, file_name='query_04.txt')

    # DB에서 꼭지 1~4 생성
    answer_01 = qa_document.get_answer_from_document(
        document_file_name=document_file_name,
        query=prompt_01
    )
    answer_02 = qa_document.get_answer_from_document(
        document_file_name=document_file_name,
        query=prompt_02
    )
    answer_03 = qa_document.get_answer_from_document(
        document_file_name=document_file_name,
        query=prompt_03
    )
    answer_04 = qa_document.get_answer_from_document(
        document_file_name=document_file_name,
        query=prompt_04
    )

    image = get_image(path='src/images', image_file_name=product_info.get('image_file_name'))
    description = get_text(path='src/description', file_name=product_info.get('description'))

    return image, description, answer_01, answer_02, answer_03, answer_04


with gr.Blocks() as item_drafts:
    gr.Markdown("# 소장품 초안")
    with gr.Row():  # 좌우 레이아웃
        with gr.Column(scale=1):  # 왼쪽 영역
            dropdown = gr.Dropdown(
                product_list,
                label="소장품 선택",
                value="Nolan Ryan 324 Wins Ball",
                show_label=True
            )
            search_button = gr.Button("검색")  # 검색 버튼
            image = gr.Image(label="이미지", show_label=True)
            description = gr.Textbox(label="소장품 설명", lines=5, interactive=False, show_label=True)
            user_prompt = gr.Textbox(label="캡션 추가 설명", lines=5, interactive=True, show_label=True)
        with gr.Column(scale=1):  # 오른쪽 영역
            text1 = gr.Textbox(label="소장품 설명 #1", interactive=False, show_label=True)
            text2 = gr.Textbox(label="소장품 설명 #2", interactive=False, show_label=True)
            text3 = gr.Textbox(label="소장품 설명 #3", interactive=False, show_label=True)
            text4 = gr.Textbox(label="소장품 설명 #4", interactive=False, show_label=True)

    # 이벤트 연결
    search_button.click(
        fn=display_item,
        inputs=[dropdown],  # 드롭다운과 description을 입력값으로 전달
        outputs=[image, description, text1, text2, text3, text4]  # 출력값 설정
    )

    generate_button = gr.Button("결과 보기")

# 소장품 데이터를 처리하는 함수
def generate_caption(dropdown_value, image, user_prompt, text1, text2, text3, text4):
    chat = chatCompletion()
    cache_key = f"{dropdown_value}_{user_prompt}"

    product_info = get_product_info(dropdown_value)

    prompt_folder = product_info.get('prompt_folder_name')
    prompt_path = f'src/prompts/{prompt_folder}'

    prompt_05 = get_text(path=prompt_path, file_name='query_05.txt')
    
    if cache_key in cache:
        print("캐시에서 결과 반환")
        return cache[cache_key]

    with open("src/prompts/final_query.txt", "r", encoding="utf-8") as file:
        query_06 = file.read()

    caption_05 = prompt_05.format(
        collection_nm=dropdown_value,
        answer_01=text1,
        answer_02=text2,
        answer_03=text3,
        answer_04=text4
    )
    answer = chat.get_answer(caption_05)
    answer_json = json.loads(answer)
    answer_05 = answer_json['choices'][0]['message']['content']

    caption_06 = query_06.format(
        answer_05=answer_05,
        answer_query=user_prompt
    )
    answer = chat.get_validation(caption_06)
    answer_json = json.loads(answer)
    result_caption = answer_json['choices'][0]['message']['content']

    # 댓글과 생성 이미지 로드
    generate_image = get_image(path='src/generate_images', image_file_name=product_info.get('generate_image_file_name'))
    reply_caption = get_text(path='src/replies', file_name=product_info.get('reply_file_name'))

    # 결과를 캐시에 저장
    result = (dropdown_value, image, result_caption, generate_image, reply_caption)
    cache[cache_key] = result
    
    return dropdown_value, image, result_caption, generate_image, reply_caption
    
with gr.Blocks() as item_results:
    gr.Markdown("# 최종결과물")
    
    with gr.Row():
        with gr.Column(scale=1):  # 왼쪽 영역
            result_name = gr.Textbox(label="소장품명", interactive=False)
            result_image = gr.Image(label="이미지", interactive=False)
            generate_image = gr.Image(label="생성이미지", interactive=False)
        
        with gr.Column(scale=1):  # 오른쪽 영역
            result_caption = gr.Textbox(label="캡션", interactive=False, lines=20)  # 크기를 20로 고정
            download_button = gr.Button(value="캡션 다운로드")  # 캡션 바로 아래에 다운로드 버튼 추가
            download_file = gr.File()
            download_button.click(download_caption, outputs=download_file)

            reply_caption = gr.Textbox(label="댓글", interactive=False, lines=20)  # 크기를 20로 고정

    generate_button.click(
        fn=generate_caption,
        inputs=[dropdown, image, user_prompt, text1, text2, text3, text4],
        outputs=[result_name, result_image, result_caption, generate_image, reply_caption]
    )

demo = gr.TabbedInterface([item_drafts, item_results], ["소장품 초안", "최종결과물"])

if __name__ == "__main__":
    demo.launch(debug=True, share=True)
