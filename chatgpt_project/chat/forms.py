from django import forms

class ChatForm(forms.Form):

    text_input = forms.CharField(label='Article for Summary', max_length='100',
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control',
                                     'placeholder':'Ask a thing to summarize...',
                                     'rows': 4, # 입력창 높이 조절
                                 }),
                                 required=False
                                )
    user_input = forms.CharField(label='Your input message', max_length='100',
                                 widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder':'Ask me anything...',
                                    }),
                                 required=False
                                )
    file_input = forms.FileField(label='PDF file Summary',
                                 widget=forms.ClearableFileInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Input PDF file...'
                                    }),
                                 required=False
                                )
    url_input = forms.URLField(label='URL Summary',
                                 widget=forms.URLInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Input Youtube URL...'
                                    }),
                                 required=False 
                                )