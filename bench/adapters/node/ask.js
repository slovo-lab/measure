// Puts one question to a JavaScript library and prints its answer as JSON.
//
// Started by bench/node_client.py with the request on standard input:
//   {"library": "mathjs" | "js-quantities", "op": "convert" | "add", ...}
// The program does no arithmetic of its own: it builds the library's
// quantities, calls the library's own conversion or addition, and reports
// the number and the unit the library gives back.
//
// Written by Claude (AI).
'use strict';

function mathjs(request) {
  const math = require('mathjs');
  if (request.op === 'convert') {
    const result = math.unit(request.value, request.unit).to(request.to_unit);
    return { value: result.toNumber(request.to_unit), unit: result.formatUnits() };
  }
  let total = math.unit(request.terms[0].value, request.terms[0].unit);
  for (const term of request.terms.slice(1)) {
    total = math.add(total, math.unit(term.value, term.unit));
  }
  const result = request.want_unit ? total.to(request.want_unit) : total;
  return { value: result.toNumber(request.want_unit || undefined), unit: result.formatUnits() };
}

function jsQuantities(request) {
  const Qty = require('js-quantities');
  if (request.op === 'convert') {
    const result = Qty(request.value, request.unit).to(request.to_unit);
    return { value: result.scalar, unit: result.units() };
  }
  let total = Qty(request.terms[0].value, request.terms[0].unit);
  for (const term of request.terms.slice(1)) {
    total = total.add(Qty(term.value, term.unit));
  }
  const result = request.want_unit ? total.to(request.want_unit) : total;
  return { value: result.scalar, unit: result.units() };
}

function version(name) {
  // Some packages do not let their package.json be required; read the file.
  const fs = require('fs');
  const path = require('path');
  let folder = path.dirname(require.resolve(name));
  for (;;) {
    const file = path.join(folder, 'package.json');
    if (fs.existsSync(file)) {
      const found = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (found.name === name) return found.version;
    }
    const parent = path.dirname(folder);
    if (parent === folder) throw new Error('no package.json found for ' + name);
    folder = parent;
  }
}

let text = '';
process.stdin.on('data', (chunk) => { text += chunk; });
process.stdin.on('end', () => {
  let reply;
  try {
    const request = JSON.parse(text);
    if (request.op === 'version') {
      reply = { ok: true, version: version(request.library), node: process.version };
    } else if (request.library === 'mathjs') {
      reply = Object.assign({ ok: true }, mathjs(request));
    } else if (request.library === 'js-quantities') {
      reply = Object.assign({ ok: true }, jsQuantities(request));
    } else {
      reply = { ok: false, error: 'unknown library ' + request.library, kind: 'adapter' };
    }
  } catch (error) {
    reply = { ok: false, error: String(error && error.message ? error.message : error) };
  }
  process.stdout.write(JSON.stringify(reply));
});
