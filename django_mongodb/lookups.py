from django.db import NotSupportedError
from django.db.models.fields.related_lookups import In, MultiColSource, RelatedIn
from django.db.models.lookups import BuiltinLookup, Exact, IsNull, UUIDTextMixin

from .query_utils import process_lhs, process_rhs


def builtin_lookup(self, compiler, connection):
    lhs_mql = process_lhs(self, compiler, connection, bare_column_ref=True)
    value = process_rhs(self, compiler, connection)
    rhs_mql = connection.mongo_operators[self.lookup_name](value)
    return {lhs_mql: rhs_mql}


def builtin_lookup_agg(self, compiler, connection):
    lhs_mql = process_lhs(self, compiler, connection)
    value = process_rhs(self, compiler, connection)
    return connection.mongo_aggregations[self.lookup_name](lhs_mql, value)


def exact(self, compiler, connection):
    lhs_mql = process_lhs(self, compiler, connection)
    value = process_rhs(self, compiler, connection)
    return {"$expr": {"$eq": [lhs_mql, value]}}


def in_(self, compiler, connection):
    if isinstance(self.lhs, MultiColSource):
        raise NotImplementedError("MultiColSource is not supported.")
    return builtin_lookup(self, compiler, connection)


def is_null(self, compiler, connection):
    if not isinstance(self.rhs, bool):
        raise ValueError("The QuerySet value for an isnull lookup must be True or False.")
    lhs_mql = process_lhs(self, compiler, connection, bare_column_ref=True)
    rhs_mql = connection.mongo_operators["isnull"](self.rhs)
    return {lhs_mql: rhs_mql}


def uuid_text_mixin(self, compiler, connection):  # noqa: ARG001
    raise NotSupportedError("Pattern lookups on UUIDField are not supported.")


def register_lookups():
    BuiltinLookup.as_mql = builtin_lookup
    BuiltinLookup.as_mql_agg = builtin_lookup_agg
    Exact.as_mql = exact
    In.as_mql = RelatedIn.as_mql = in_
    IsNull.as_mql = is_null
    UUIDTextMixin.as_mql = uuid_text_mixin
