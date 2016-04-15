# -*- coding: utf-8 -*-

from django import forms



class ModeratedModelFormMixin(forms.BaseModelForm):
    def __init__(self, *args, **kwargs):
        inst = kwargs.get("instance")
        print(inst)

        m = super(ModeratedModelFormMixin, self).__init__(*args, **kwargs)
        print(self.initial)