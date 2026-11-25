# Report to the authors of convert-units

Status: **prepared on 25 November 2026, not sent.** Waiting for the lab owner's decision: the README's comment "tested to 4 significant figures" may make this a documented limit under [`REPORTING.md`](../REPORTING.md). Written by Claude (AI).

Checks done: reproduced by calling the library directly (2.3.4, the latest release, and 3.0.0-beta.8; Node 22); the README inside the package read: one example carries the comment "0.4536... (tested to 4 significant figures)", nothing else about accuracy; issues searched for "inch", "precision", "accuracy", "inaccurate", "3.28084": issue 281 ("Inaccuracies in conversion between ft² and m²", closed as completed) is about the area ratio; none about length; source read: NIST SP 811, Appendix B.8 (inch 2.54 E-02 m and foot 3.048 E-01 m, exact) and B.9.

## Text

**Title:** Length conversions between metric and imperial use the rounded ratio 3.28084 (1 in gives 25.3999992 mm)

Hello. This report comes from Measure (https://github.com/slovo-lab/measure), an open test bench that checks unit and uncertainty calculators against reference answers with cited sources. It is written by an AI (Claude) and curated by a human, Anton Krugovov.

With convert-units 2.3.4, and the same with 3.0.0-beta.8:

```js
const convert = require('convert-units');
console.log(convert(1).from('in').to('mm'));   // 25.399999187200024
console.log(convert(6).from('ft').to('m'));    // 1.828799941478402
console.log(convert(26.2).from('mi').to('km')); // 42.164811450726035
```

The inch is exactly 25.4 mm and the foot exactly 0.3048 m (NIST SP 811, Appendix B.8), so the expected results are 25.4, 1.8288 and 42.1648128. The difference is a relative 3.2e-8 and comes from the anchor ratio in `definitions/length`: `3.28084` feet per metre, where the exact value is `1 / 0.3048`.

Two neighbours of the same kind, for completeness:

- area: ratio `10.7639` (issue #281 reported it; `2 in2` to `mm2` gives 1290.32124870, exact 1290.32);
- volume: `1 gal` to `l` gives 3.7854117954, where the US gallon of 231 cubic inches is exactly 3.785411784.

In 2.3.4 the mass ratio was `453.592` grams per pound (exact: 453.59237); in 3.0.0-beta.8 the pound comes out exact, so this kind of change seems welcome. We saw the README's note that the pound example is tested to 4 significant figures; we report the length ratio because an inch that is not 25.4 mm can surprise a user, and the fix is to write the ratio as `1 / 0.3048`.

## Русский перевод текста

**Заголовок:** Пересчёты длины между метрическими и английскими единицами используют округлённое отношение 3,28084 (1 дюйм даёт 25,3999992 мм)

Здравствуйте. Это сообщение от Measure (https://github.com/slovo-lab/measure), открытого стенда, который сверяет калькуляторы единиц и неопределённости с эталонными ответами, у которых есть источники. Его написал ИИ (Claude), куратор-человек — Антон Круговов.

В convert-units 2.3.4, и так же в 3.0.0-beta.8: 1 дюйм в мм даёт 25,399999187200024; 6 футов в м — 1,828799941478402; 26,2 мили в км — 42,164811450726035.

Дюйм равен ровно 25,4 мм, а фут ровно 0,3048 м (NIST SP 811, приложение B.8), поэтому ожидаемые результаты: 25,4, 1,8288 и 42,1648128. Расхождение составляет 3,2e-8 в относительном выражении и происходит от опорного отношения в `definitions/length`: `3.28084` фута в метре, тогда как точное значение равно `1 / 0.3048`.

Два соседних случая того же рода, для полноты:

- площадь: отношение `10.7639` (о нём сообщало обращение #281; `2 in2` в `mm2` даёт 1290,32124870, точно 1290,32);
- объём: `1 gal` в `l` даёт 3,7854117954, тогда как американский галлон в 231 кубический дюйм равен ровно 3,785411784.

В 2.3.4 отношение для массы было `453.592` грамма в фунте (точно: 453,59237); в 3.0.0-beta.8 фунт получается точным, так что такие изменения, похоже, приветствуются. Мы видели в README пометку, что пример с фунтом проверен до 4 значащих цифр; сообщаем об отношении для длины, потому что дюйм, не равный 25,4 мм, может удивить пользователя, а исправление состоит в том, чтобы записать отношение как `1 / 0.3048`.
