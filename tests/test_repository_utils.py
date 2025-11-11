from app.db.repositories import utils


def test_normalize_owner_alias_handles_quotes_and_case():
    assert utils.normalize_owner_alias(' "АО ""Прибор"" " ') == "ао прибор"


def test_normalize_owner_alias_handles_curly_quotes():
    fancy = "ООО «ГАЗПРОМНЕФТЬ-ЯМАЛ»"
    plain = 'ООО "ГАЗПРОМНЕФТЬ-ЯМАЛ"'
    assert utils.normalize_owner_alias(fancy) == utils.normalize_owner_alias(plain)


def test_normalize_methodology_alias_collapse_spaces():
    value = "МИ   2124-90 (ред. 2023)"
    assert utils.normalize_methodology_alias(value) == "ми 2124 90 ред 2023"
