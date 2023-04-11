from epsilion_wars_mmorpg_automation.game.parsers import get_resource_counters


def test_get_resource_counters():
    payload = """🔮Эссенция Пурги - 2шт
Эссенция в которой содержится энергия снежной девы.

🔮Эссенция Метели - 2шт
Эссенция в которой содержится энергия снежной девы.

🔮Эссенция Маржаны - 1шт
Эссенция в которой содержится энергия снежной девы.

🔮Эссенция Вьюги - 1шт
Эссенция в которой содержится энергия снежной девы.

📄Рецепт [I]: 🌡 Эликсир усиления - 25шт
Инструкция по созданию вещи.

Страница (1/23)"""

    result = get_resource_counters(payload)

    assert len(result.keys()) == 5
    assert '📄Рецепт [I]: 🌡 Эликсир усиления' in result
    assert result['📄Рецепт [I]: 🌡 Эликсир усиления'] == 25
    assert '🔮Эссенция Вьюги' in result
    assert result['🔮Эссенция Вьюги'] == 1
