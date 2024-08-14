from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from .models import SearchHistory
from .forms import ChatForm
from openai import OpenAI
from django.conf import settings
import fitz # PyMuPDF
from youtube_transcript_api import YouTubeTranscriptApi

# 클라이언트 인스턴스 생성
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_completion(prompt, model="gpt-3.5-turbo"):
    try:
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.5
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

def extract_text_from_pdf(pdf_file): # PDF 파일에서 텍스트 출출하는 함수
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_youtube(url): # YouTube URL에서 동영상의 스크립트를 추출하는 함수
    video_id = url.split('v=')[-1]  # URL에서 비디오 ID 추출
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([item['text'] for item in transcript])
    return transcript_text

def translate_to_korean(text, model="gpt-3.5-turbo"):
    try:
        translation_prompt = f"Translate : {text}"
        translation = client.chat.completions.create(
            model=model,
            messages=[
                {'role':'system', 'content': 'You are a translator. Translate to Korean.'},
                {'role':'user', 'content': translation_prompt}
                ],
            max_tokens=100,
            temperature=0.5
        )
        return translation.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"


def generate_prompt(text_input=None, file_input=None, url_input=None):
    if text_input:
        return f"Summarize in less than 10 lines: {text_input}"
    elif file_input:
        file_content = extract_text_from_pdf(file_input)
        return f"Summarize in less than 10 lines: (PDF) {file_content}"
    elif url_input:
        url_content = extract_text_from_youtube(url_input)
        return f"Summarize in less than 10 lines: (URL) {url_content}"
    else:
        return "Nothing to summarize."

class ChatView(LoginRequiredMixin, FormView):
    form_class = ChatForm
    template_name = "chat/index.html"
    success_url = '/' # 폼 제출 후 다시 메인페이지로 이동

    def form_valid(self, form):
        text_input = form.cleaned_data['text_input'] # 사용자가 입력한 데이터를 딕셔너리로 제공 (drf)
        # user_input = form.cleaned_data['user_input']
        file_input = form.cleaned_data['file_input']
        url_input = form.cleaned_data['url_input']
        prompt = generate_prompt(text_input, file_input, url_input) # user_input도 가능(단, 처리함수 필요)
        summary_result = get_completion(prompt)
        translation_result = translate_to_korean(summary_result)

        # 검색 기록을 DB에 저장
        SearchHistory.objects.create(
            user=self.request.user,
            url_domain=url_input,
            text_input=text_input,
            file_name=file_input,
            summary_result=summary_result,
            translation_result=translation_result,
        )

        return self.render_to_response(self.get_context_data(
            summary_result=summary_result,
            translation_result=translation_result
            )) # result가 템플릿의 result로 들어감

class HomeView(TemplateView):
    template_name = 'chat/home.html'

class SearchHistoryView(LoginRequiredMixin, ListView):
    model = SearchHistory
    template_name = 'chat/search_history.html'
    context_object_name = 'search_histories'

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).order_by('-created_at')


