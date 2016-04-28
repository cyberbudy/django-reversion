# -*- coding: utf-8 -*-

from django.utils.encoding import force_text
from django.template.loader import render_to_string 
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.db import models
from reversion.revisions import get_adapter
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

try:
    from filer.fields.image import FilerImageField
    from filer.models.imagemodels import Image
    filer_image = True
except:
    filer_image = False

try:
    from diff_match_patch import diff_match_patch
    dmp = diff_match_patch()
except ImportError:  # pragma: no cover
    pass


class BaseDiff(object):
    template = "reversion/base_diff.html"

    def __init__(self, field, old, new, template=None):
        """initialize/override base variables"""
        if template:
            self.template = template

        self.field = field
        self.field_name = field.name
        self.set_values(old, new)

    def set_values(self, old, new):
        """
        process values for getting proper difference and margin
        expects:
            new value - is version dict data or some data from it
            old value - is current object or some data from it
        """
        self.choices = self.has_choices(old, self.field.name)

        if self.choices:
            self.old_value = self.get_choice_value(
                getattr(old, self.field.name))
            self.new_value = self.get_choice_value(
                new.get(self.field.name))
        else:
            self.old_value = getattr(old, self.field.name)
            self.new_value = new.get(self.field.name)

    def has_choices(self, obj, field_name):
        return obj._meta.get_field(field_name).choices

    def get_choice_value(self, value):
        for key, name in self.choices:
            if key == value:
                return name
        return value

    def margin(self):
        """check if new and old values are different"""
        return self.new_value != self.old_value and (self.new_value or self.old_value)

    @property
    def diff(self, pretty=True, cleanup="semantic"):
        """find changes between current value and previous version"""
        if self.choices:
            return {
                "changes": "<del>{0}</del>\n<ins>{1}</ins>".format(
                    self.old_value, self.new_value)
            }
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
        """render changes from diff using configured template"""
        if not context:
            context = self.diff
        return render_to_response(self.template, context).content


class ForeignKeyDiff(BaseDiff):
    template = "reversion/foreign_key_diff.html"

    def set_values(self, old, new):
        self.old_value = getattr(old, self.field.name)
        try:
            objs = self.field.related_model.objects
            if hasattr(objs, "include_unmoderated"):
                self.new_value = objs.\
                    include_unmoderated(id=new.get(self.field.name, None))[:1]
            else:
                self.new_value = objs.filter(id=new.get(self.field.name, None))[:1]
        except ObjectDoesNotExist:
            self.new_value = None
        if self.new_value:
            self.new_value = self.new_value[0]
        else:
            self.new_value = None

    @property
    def diff(self, pretty=True, cleanup="semantic"):
        return {
            "left": str(self.old_value),
            "right": str(self.new_value)
        }


class BooleanDiff(BaseDiff):
    template = "reversion/foreign_key_diff.html"

    @property
    def diff(self, pretty=True, cleanup="semantic"):
        return {
            "left": self.old_value,
            "right": self.new_value
        }


class ImageDiff(BaseDiff):
    template = "reversion/image_diff.html"

    def set_values(self, old, new):
        self.old_value = getattr(old, self.field.name+"_id")
        self.new_value = new.get(self.field.name)

    @property
    def diff(self):
        if (filer_image and isinstance(self.field, FilerImageField) or 
                isinstance(self.field, models.ImageField)):
            if self.old_value:
                left_image = Image.objects.get(id=self.old_value).icons["64"]
            else:
                left_image = None

            if self.new_value:
                right_image = Image.objects.get(id=self.new_value).icons["64"]
            else:
                right_image = None
            return {
                'left': left_image,
                'right': right_image
            }
        return {}


class ManyToManyDiff(BaseDiff):
    template = "reversion/many_to_many_diff.html"

    def set_values(self, old, new):
        self.old_value = set(getattr(old, self.field.name).all())
        self.new_value = set(self.field.related_model.objects.filter(
            id__in=new.get(self.field.name, [])))

    def margin(self):
        return self.new_value-self.old_value or self.old_value-self.new_value

    @property
    def diff(self):
        # removed items
        left = self.old_value-self.new_value
        # new items
        right = self.new_value-self.old_value
        return {
            "left": left,
            "right": right
        }



class DateTimeDiff(BaseDiff):
    template = "reversion/datetime_diff.html"

    @property
    def diff(self):
        return {
            "left": self.old_value,
            "right": self.new_value,
        }


def get_changes_between_models(new, old=None):
    """
    check old and new objects, if both present - return their field's diffs
    """
    global type_diff

    if not new:
        return

    if not old:
        ct = ContentType.objects.get(id=new.content_type_id)
        Model = ct.model_class()
        
        try:
            old = Model.objects.include_unmoderated(id=new.object_id)[0]
        except (ObjectDoesNotExist, IndexError):
            return _("Sorry. There is no such object in the system.")

    adapter = get_adapter(old.__class__)
    new_data = new.field_dict

    if adapter:
        opts = adapter.model._meta.concrete_model._meta
        fields = adapter.fields or (field.name for field in opts.local_fields + opts.local_many_to_many)
        fields = (opts.get_field(field) for field in fields if not field in adapter.exclude)
    else:
        fields = []
    return get_fields_diff(fields, old, new_data)


def get_fields_diff(fields, old, new):
    """return formated fields diffs"""
    diffs = {}

    for field in fields:
        field_type = type(field)

        if field_type in type_diff:
            dif = type_diff[field_type](field, old, new)
        else:
            dif = type_diff["base"](field, old, new)

        if dif.margin():
            diffs[field.name] = dif
        else:
            continue
    return diffs


def change_diff_types(diffs, new=False):
    global type_diff
    if not new:
        type_diff.update(diffs)
    else:
        type_diff = diffs


type_to_diff = {
    "base": BaseDiff,
    models.ManyToManyField: ManyToManyDiff,
    models.ImageField: ImageDiff,
    models.ForeignKey: ForeignKeyDiff,
    models.OneToOneField: ForeignKeyDiff,
    models.DateField: DateTimeDiff,
    models.DateTimeField: DateTimeDiff,
    models.BooleanField: BooleanDiff,
    models.NullBooleanField: BooleanDiff,
}

if filer_image:
    type_to_diff[FilerImageField] = ImageDiff

# moderation api
type_diff = type_to_diff
changes_between_models = get_changes_between_models
