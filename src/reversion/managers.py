# -*- coding: utf-8 -*-

from django.db.models.manager import Manager
from moderation.utils import django_17
from reversion.models import PENDING, REJECTED, APPROVED




class VersionManager(Manager):
    use_for_related_fields = True
    
    def get_queryset(self):
        query_set = None

        if django_17():
            query_set = super(VersionManager, self).get_queryset()
        else:
            query_set = super(VersionManager, self).get_query_set()
        return query_set.filter(**{"moderated_status": APPROVED})

    # def unmoderated(self):
    #     if django_17():
    #         query_set = super(VersionManager, self).get_queryset()
    #     else:
    #         query_set = super(VersionManager, self).get_query_set()
    #     return query_set.exclude(**{"moderated_status": APPROVED})


    # def moderated(self):
    #     if django_17():
    #         query_set = super(VersionManager, self).get_queryset()
    #     else:
    #         query_set = super(VersionManager, self).get_query_set()
    #     return query_set.filter(**{"moderated_status": APPROVED})



class ModerationManagerMixin(Manager):
    def filter_function_by_status(self, function, status=2, *args, **kwargs):
        """get objects from function filtered by moderation status"""
        if not function:
            function = "get_queryset"
        query = getattr(
                super(ModerationManagerMixin, self), function
            )(*args, **kwargs)

        if not status:
            return query
        return query.filter(moderated_status=status)
