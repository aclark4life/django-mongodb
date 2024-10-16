from django.db.models.query import QuerySet
from django.db.models.manager import BaseManager

class MongoQuerySet(QuerySet):
    def raw_mql(self):
        pass


class MongoManager(BaseManager.from_queryset(MongoQuerySet)):
    pass
