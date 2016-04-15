# -*- coding: utf-8 -*-

from django.utils.encoding import force_text
from django.template.loader import render_to_string 
from django.shortcuts import render_to_response

try:
    from diff_match_patch import diff_match_patch
    dmp = diff_match_patch()
except ImportError:  # pragma: no cover
    pass


class BaseDiff(object):
    template = "reversion/base_diff.html"

    def __init__(self, field, old, new, template=None):
        if template:
            self.template = template

        self.field = field
        self.field_name = field.name
        self.old_value = old
        self.new_value = new


    def margin(self):
        return self.new_value != self.old_value

    @property
    def diff(self, pretty=True, cleanup="semantic"):
        clean_diff = None
        diffs = dmp.diff_main(
            force_text(self.old_value),
            force_text(self.new_value))

        if cleanup == "semantic":
            clean_diff = dmp.diff_cleanupSemantic(diffs)
        if pretty:
            diffs = dmp.diff_prettyHtml(clean_diff or diffs)
        return {"changes": diffs}

    def render(self, context=None):
        if not context:
            context = self.diff
        # return context.values()
        return render_to_response(self.template, context).content


class ForeignKeyDiff(BaseDiff):
    template = "reversion/foreign_key_diff.html"

    @property
    def diff(self, pretty=True, cleanup="semantic"):
        clean_diff = None
        return {
            "left": str(self.old_value),
            "right": str(self.new_value)
        }


class ManyToManyDiff(BaseDiff):
    template = "reversion/many_to_many_diff.html"

    def __init__(self, field, old, new, template=None):
        if template:
            self.template = template

        self.field = field
        self.field_name = field.name
        self.old_value = set(old)
        self.new_value = set(new)

    def margin(self):
        return self.new_value-self.old_value or self.old_value-self.new_value

    @property
    def diff(self):
        clean_diff = None
        # get removed items
        left = self.new_value-self.old_value
        # get new items
        right = self.old_value-self.new_value
        
        return {
            "left": left,
            "right": right
        }