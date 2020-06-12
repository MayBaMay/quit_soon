#!/usr/bin/env python

from django import forms


class UserRelatedModelForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
