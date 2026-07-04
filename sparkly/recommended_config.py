import json
from collections import defaultdict

from sparkly.index_config import IndexConfig
from sparkly.query_generator.query_spec import QuerySpec


class RecommendedConfig:
    """
    Minimal user-facing config for Sparkly Auto.
    """

    def __init__(
        self,
        *,
        id_col: str,
        concat_fields: dict,
        spec: dict,
        boost_map: dict | None = None,
    ):
        self.id_col = id_col
        self.concat_fields = concat_fields
        self.spec = spec
        self.boost_map = boost_map or {}

    @classmethod
    def from_components(
        cls,
        *,
        index_config: IndexConfig,
        query_spec: QuerySpec,
    ):
        query_spec_dict = query_spec.to_dict(json_safe=True)

        return cls(
            id_col=index_config.id_col,
            concat_fields=index_config.concat_fields,
            spec=query_spec_dict["spec"],
            boost_map=query_spec_dict.get("boost_map", {}),
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_col=data["id_col"],
            concat_fields=data.get("concat_fields", {}),
            spec=data["spec"],
            boost_map=data.get("boost_map", {}),
        )

    @classmethod
    def from_json(cls, data):
        if isinstance(data, str):
            data = json.loads(data)

        return cls.from_dict(data)

    def to_dict(self) -> dict:
        return {
            "id_col": self.id_col,
            "concat_fields": self.concat_fields,
            "spec": self.spec,
            "boost_map": self.boost_map,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_index_config(self) -> IndexConfig:
        index_config = IndexConfig()
        index_config.id_col = self.id_col

        for field, source_fields in self.concat_fields.items():
            index_config.concat_fields[field] = source_fields

        for field, analyzers in self._infer_field_to_analyzers().items():
            index_config.add_field(field, analyzers)

        return index_config

    def to_query_spec(self) -> QuerySpec:
        return QuerySpec.from_dict({
            "spec": self.spec,
            "boost_map": self.boost_map,
            "filter": [],
        })

    def to_components(self) -> tuple[IndexConfig, QuerySpec]:
        return self.to_index_config(), self.to_query_spec()

    def _infer_field_to_analyzers(self) -> dict:
        field_to_analyzers = defaultdict(set)

        for query_fields in self.spec.values():
            for query_field in query_fields:
                field, analyzer = query_field.rsplit(".", 1)
                field_to_analyzers[field].add(analyzer)

        return {
            field: sorted(analyzers)
            for field, analyzers in field_to_analyzers.items()
        }