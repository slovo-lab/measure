# Report to the authors of p6plab-mcp-calculator

Status: **sent on 25 November 2026 at 14:15 (Madrid)** by e-mail from the lab owner's mailbox to the address in the package's metadata, after he confirmed the text. The e-mail went as plain text, without the formatting marks below. No second message will follow if there is no answer. Written by Claude (AI).

Checks done (see [`REPORTING.md`](../REPORTING.md)):

1. Reproduced by calling the server directly over stdio, version 2.0.1 from the package index, Python 3.13.
2. Documentation: the package's description on the package index was read as a search excerpt only; it lists unit conversion among the features. The repository named in the metadata (github.com/peepeepopapapeepeepo/mcp-calculator) answers "page not found", so its README and changelog could not be read. **This check is incomplete.**
3. Existing issues: none can be seen; there is no public tracker.
4. Source for rounding: NIST Special Publication 811 (2008), Appendix B.7.1.

Where it would go: by e-mail to the address in the package's metadata, since there is no tracker.

## Text

**Subject:** p6plab-mcp-calculator 2.0.1: `round` gives 2.67 for 2.675, and `convert_units` returns a placeholder as a success

Hello. This report comes from Measure (https://github.com/slovo-lab/measure), an open test bench that checks calculators used by AI agents against reference answers with cited sources. It is written by an AI (Claude) and curated by a human, Anton Krugovov. The repository named in the package's metadata is not reachable, so this comes by e-mail.

With p6plab-mcp-calculator 2.0.1, called over stdio:

**1. `round`**

```
round {"params": {"number": 2.675, "decimals": 2}}  ->  2.67
round {"params": {"number": 2.665, "decimals": 2}}  ->  2.67
```

2.675 rounded to two decimal places is 2.68 under every common rule (half up, and half to even, since 7 is odd). The tool appears to round the binary number nearest to 2.675, which is slightly below it. Passing the number as the text "2.675" gives the same answer. For 2.665 the answer 2.67 agrees with rounding half up and not with half to even (NIST SP 811, Appendix B.7.1), so the two answers together follow no single decimal rule.

A fix could be to round with Python's `decimal` module on the number as written, and to say in the tool's description which rule is used.

**2. `convert_units`**

```
convert_units {"params": {"value": 1, "from_unit": "inch", "to_unit": "mm"}}
->  {"success": true, "result": {"success": true, "result": {"result": "Unit conversion not yet implemented", "status": "placeholder"}, ...}}
```

Every conversion we tried returns this. The tool is listed to the agent, and the reply is marked as a success, so an agent has no signal that nothing was converted. Returning an error, or not listing the tool until it works, would make this visible.

Nothing is asked of you. Thank you for publishing the server.

## Русский перевод текста

**Тема:** p6plab-mcp-calculator 2.0.1: `round` даёт 2,67 для 2,675, а `convert_units` возвращает заглушку как успех

Здравствуйте. Это сообщение от Measure (https://github.com/slovo-lab/measure), открытого стенда, который сверяет калькуляторы, используемые ИИ-агентами, с эталонными ответами, у которых есть источники. Его написал ИИ (Claude), куратор-человек — Антон Круговов. Репозиторий, указанный в метаданных пакета, недоступен, поэтому пишем письмом.

В p6plab-mcp-calculator 2.0.1, при вызове через stdio:

**1. `round`.** 2,675 и 2,665 при округлении до двух знаков оба дают 2,67. 2,675 по любому распространённому правилу даёт 2,68 (и «половина вверх», и «половина к чётному», так как 7 нечётно). Похоже, инструмент округляет двоичное число, ближайшее к 2,675, а оно чуть меньше. Передача числа текстом "2.675" даёт тот же ответ. Для 2,665 ответ 2,67 согласуется с «половина вверх», но не с «половина к чётному» (NIST SP 811, приложение B.7.1), так что два ответа вместе не следуют ни одному десятичному правилу. Исправить можно, округляя модулем `decimal` число так, как оно записано, и указав в описании инструмента, какое правило применяется.

**2. `convert_units`.** На любой пересчёт приходит ответ с `"success": true` и текстом «Unit conversion not yet implemented», статус «placeholder». Инструмент показан агенту, ответ помечен как успех, и у агента нет признака, что ничего не пересчитано. Ошибка в ответе или отсутствие инструмента в списке, пока он не работает, сделали бы это видимым.

От вас ничего не требуется. Спасибо, что опубликовали сервер.
