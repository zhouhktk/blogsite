# -*- coding:utf-8 -*-
from django import forms
from .models import Comment
from ckeditor.widgets import CKEditorWidget


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
