import time

from app.services import template_rules
from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.level_meter import GENERATOR as LEVEL_GENERATOR
from app.services.html_renderer import _template_name_from_context
from app.services.templates import TEMPLATES


def _rule(rule_id, instrument_kind, match_field, match_value, template_id, priority):
    return template_rules._Rule(
        id=rule_id,
        instrument_kind=instrument_kind,
        match_field=match_field,
        match_value=match_value,
        template_id=template_id,
        priority=priority,
    )


def _set_cache(monkeypatch, rules, methodology_forms=None):
    """Seed the resolver cache so the tests need no database."""
    monkeypatch.setattr(template_rules, "_cache", (rules, methodology_forms or {}))
    monkeypatch.setattr(template_rules, "_cache_at", time.monotonic())


def _gen_input(template_id, mitype_number, points=5):
    return GenInput(
        range_min=0.0,
        range_max=10.0,
        unit="м",
        points=points,
        allowable_error=FixedPctTol(5.0),
        allowable_variation=FixedPctTol(5.0),
        ctx={"template_id": template_id, "mitype_number": mitype_number},
    )


async def test_override_wins_over_everything(monkeypatch):
    _set_cache(
        monkeypatch,
        [_rule(1, "manometers", "mitype_number", "13535-93", "pressure_common", 30)],
    )

    resolution = await template_rules.resolve_form(
        None,
        method_code="ГОСТ 8.461-2009",
        mitype_number="13535-93",
        mitype_title="Манометр",
        override="rtd_platinum",
    )

    assert resolution.template_id == "rtd_platinum"
    assert resolution.source == "override"


async def test_rule_beats_heuristics_and_reports_source(monkeypatch):
    _set_cache(
        monkeypatch,
        [_rule(7, "level_meters", "mitype_number", "86065-22", "level_meter_two_tables", 28)],
    )

    resolution = await template_rules.resolve_form(
        None,
        method_code="МП 1657-7-2024",
        mitype_number="86065-22",
        mitype_title="Уровнемер Insol",
    )

    assert resolution.template_id == "level_meter_two_tables"
    assert resolution.source == "rule"
    assert resolution.rule_id == 7


async def test_lower_priority_value_wins(monkeypatch):
    _set_cache(
        monkeypatch,
        [
            _rule(1, "level_meters", "title_keyword", "УРОВН", "level_meter", 35),
            _rule(2, "level_meters", "title_keyword", "УРОВНЕМЕР", "level_meter_two_tables", 10),
        ],
    )

    resolution = await template_rules.resolve_form(None, mitype_title="Уровнемер ультразвуковой")

    assert resolution.template_id == "level_meter_two_tables"
    assert resolution.rule_id == 2


async def test_title_keyword_requires_all_words(monkeypatch):
    _set_cache(
        monkeypatch,
        [_rule(1, "manometers", "title_keyword", "ДАВЛЕН,ДАТЧИК", "pressure_sensor", 28)],
    )

    matched = await template_rules.resolve_form(None, mitype_title="Датчик давления ДД-10")
    unmatched = await template_rules.resolve_form(None, mitype_title="Датчик температуры")

    assert matched.template_id == "pressure_sensor"
    # «Датчик» без «давления» правилом не ловится и падает в эвристику (манометры по умолчанию).
    assert unmatched.source == "fallback"


async def test_methodology_default_form(monkeypatch):
    _set_cache(
        monkeypatch,
        [],
        methodology_forms={"МИ 2124-90": "pressure_sensor"},
    )

    resolution = await template_rules.resolve_form(None, method_code="МИ 2124-90")

    assert resolution.template_id == "pressure_sensor"
    assert resolution.source == "methodology"


async def test_fallback_mirrors_the_heuristics(monkeypatch):
    _set_cache(monkeypatch, [])

    assert (
        await template_rules.resolve_form(None, method_code="ГОСТ 8.461-2009")
    ).template_id == "rtd_platinum"
    assert (
        await template_rules.resolve_form(None, mitype_number="43790-12")
    ).template_id == "controller_43790_12"
    assert (
        await template_rules.resolve_form(None, mitype_title="Манометр МП-100")
    ).template_id == "pressure_common"
    assert (
        await template_rules.resolve_form(None, mitype_title="Уровнемер VEGAPULS")
    ).template_id == "level_meter"


def test_level_meter_sub_form_follows_template_id():
    two_tables = LEVEL_GENERATOR.generate(_gen_input("level_meter_two_tables", "86065-22"))
    assert two_tables.get("insol_two_tables") is True
    assert two_tables.get("table_rows_b")

    current = LEVEL_GENERATOR.generate(_gen_input("level_meter_current_output", "47249-16"))
    assert current.get("has_current_output_table") is True
    assert current.get("current_output_rows")

    plain = LEVEL_GENERATOR.generate(_gen_input("level_meter", ""))
    assert not plain.get("insol_two_tables")
    assert not plain.get("has_current_output_table")


def test_level_meter_base_form_falls_back_to_the_registration_number():
    """Without an explicit sub-form the old number check still decides (rollout safety)."""
    result = LEVEL_GENERATOR.generate(_gen_input("level_meter", "86065-22"))
    assert result.get("insol_two_tables") is True


def test_level_meter_sub_forms_are_rendered_by_the_same_html():
    for template_id in ("level_meter", "level_meter_two_tables", "level_meter_current_output"):
        assert TEMPLATES[template_id]["path"] == "level_meter.html"


def test_renderer_renders_the_resolved_form():
    assert (
        _template_name_from_context({"template_id": "level_meter_two_tables"}) == "level_meter.html"
    )
    assert _template_name_from_context({"template_id": "rtd_platinum"}) == "rtd.html"
    assert _template_name_from_context({"template_id": "pressure_sensor"}) == "pressure_sensor.html"


def test_renderer_falls_back_to_heuristics_without_template_id():
    """An old caller that passes no template_id still renders (and the fallback is logged)."""
    assert _template_name_from_context({"methodology_full": "ГОСТ 8.461-2009"}) == "rtd.html"
