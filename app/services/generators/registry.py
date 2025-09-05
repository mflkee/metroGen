from __future__ import annotations

from .base import TableGenerator
from .pressure_common import GENERATOR as _PRESSURE
from .pressure_common import TEMPLATE_ID as _PRESSURE_ID


class _DefaultGenerator(TableGenerator):
    def generate(self, gi):
        err_val = gi.allowable_error.value(ref=gi.range_max, fsv=gi.range_max, ctx=gi.ctx)
        var_val = gi.allowable_variation.value(ref=gi.range_max, fsv=gi.range_max, ctx=gi.ctx)
        return {
            "rows": [],
            "unit_label": gi.unit,
            "allowable_error": f"{err_val:.2f}",
            "allowable_variation": f"{var_val:.2f}",
        }


_REGISTRY: dict[str, TableGenerator] = {}
_DEFAULT = _DefaultGenerator()


def register_template(template_id: str, generator: TableGenerator) -> None:
    _REGISTRY[template_id.strip().lower()] = generator


def get_by_template(template_id: str | None) -> TableGenerator:
    if not template_id:
        return _DEFAULT
    return _REGISTRY.get(template_id.strip().lower(), _DEFAULT)


# регистрация встроенных
register_template(_PRESSURE_ID, _PRESSURE)
