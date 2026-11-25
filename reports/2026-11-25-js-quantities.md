# Report to the authors of js-quantities

Status: **sent on 25 November 2026**, after the lab owner confirmed the text, as an issue opened from his account: https://github.com/gentooboontoo/js-quantities/issues/153. One comment in the code example was changed to what the library prints: 3.785411783999999. Written by Claude (AI).

Checks done (see [`REPORTING.md`](../REPORTING.md)): reproduced by calling the library directly (js-quantities 1.8.0, Node 22); the README inside the package read for "gallon", "precision" and "exact": nothing about the precision of definitions; issues searched for "gallon": three results; 132 ("Lacking precision necessary for required comparisons", open) is about floating-point comparison and says in passing that the definitions "aren't exact" without naming which or by how much; 62 and 63 ask for new units; source read: NIST Handbook 44, Appendix C, and NIST SP 811, Appendix B.8.

## Text

**Title:** `gallon` and `pint` are defined with rounded values (4e-9 from 231 and 28.875 cubic inches)

Hello. This report comes from Measure (https://github.com/slovo-lab/measure), an open test bench that checks unit and uncertainty calculators against reference answers with cited sources. It is written by an AI (Claude) and curated by a human, Anton Krugovov.

With js-quantities 1.8.0:

```js
const Qty = require('js-quantities');
console.log(Qty(1, 'gal').to('l').scalar);    // 3.7854118
console.log(Qty(1, 'pt').to('l').scalar);     // 0.473176475
console.log(Qty(231, 'in^3').to('l').scalar); // 3.785411784
```

In `src/quantities/definitions.js` the gallon is `0.0037854118` cubic metres and the pint `0.000473176475`. The US gallon is 231 cubic inches and the US liquid pint 28.875 cubic inches (NIST Handbook 44, Appendix C, "Units of Liquid Volume"); with the inch at exactly 25.4 mm these are exactly 0.003785411784 and 0.000473176473 cubic metres. The definitions differ from that by a relative 4e-9. We did not check the quart, cup, fluid ounce and spoons, which are likely defined from the same figures.

The inch, foot, mile, nautical mile, pound and short ton in the same file gave exact values in our runs.

This is related to issue 132 but is a separate, smaller point: the stored constants themselves, not floating-point arithmetic. The difference is far below what most uses need; we report it because the values are exact by definition.

## Русский перевод текста

**Заголовок:** `gallon` и `pint` определены округлёнными значениями (4e-9 от 231 и 28,875 кубического дюйма)

Здравствуйте. Это сообщение от Measure (https://github.com/slovo-lab/measure), открытого стенда, который сверяет калькуляторы единиц и неопределённости с эталонными ответами, у которых есть источники. Его написал ИИ (Claude), куратор-человек — Антон Круговов.

В js-quantities 1.8.0 один галлон в литрах даёт 3,7854118, одна пинта — 0,473176475, а 231 кубический дюйм — 3,785411784.

В `src/quantities/definitions.js` галлон равен `0.0037854118` кубического метра, а пинта `0.000473176475`. Американский галлон равен 231 кубическому дюйму, американская жидкая пинта — 28,875 кубического дюйма (NIST Handbook 44, приложение C, «Units of Liquid Volume»); при дюйме ровно 25,4 мм это ровно 0,003785411784 и 0,000473176473 кубического метра. Определения отличаются от этого на 4e-9 в относительном выражении. Кварту, чашку, жидкую унцию и ложки мы не проверяли; вероятно, они определены из тех же чисел.

Дюйм, фут, миля, морская миля, фунт и короткая тонна из того же файла дали в наших прогонах точные значения.

Это связано с обращением 132, но это отдельный и меньший вопрос: сами записанные константы, а не арифметика с плавающей точкой. Разница намного меньше того, что нужно большинству применений; сообщаем, потому что значения точны по определению.
