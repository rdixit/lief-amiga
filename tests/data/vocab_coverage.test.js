/**
 * Vocabulary coverage and config correctness tests.
 *
 * Run:  node --test tests/data/vocab_coverage.test.js
 *   or: npm test
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');

const vocab = JSON.parse(readFileSync(resolve(ROOT, 'vocabulary.json'), 'utf8'));
const room  = JSON.parse(readFileSync(resolve(ROOT, 'data', 'meaning_room.json'), 'utf8'));

// Build a lookup map: symbol id -> symbol object
const symById = Object.fromEntries(
  Object.values(vocab.symbols).map(s => [s.id, s])
);

// Symbols that are valid grid items
const gridSymbols = Object.values(vocab.symbols).filter(s => s.allowed_for_grid);

// Full set of symbol IDs referenced by any anchor
const allAnchorSymbolIds = new Set(room.anchors.flatMap(a => a.symbol_ids));

// ─────────────────────────────────────────────────────────────
// 1. meaning_room.json schema
// ─────────────────────────────────────────────────────────────
describe('meaning_room.json schema', () => {

  it('has required top-level fields', () => {
    assert.ok(typeof room.image === 'string',              'image must be a string');
    assert.ok(Array.isArray(room.image_natural_size),      'image_natural_size must be an array');
    assert.equal(room.image_natural_size.length, 2,        'image_natural_size must have 2 elements');
    assert.ok(typeof room.default_glow_intensity === 'number', 'default_glow_intensity must be a number');
    assert.ok(Array.isArray(room.anchors),                 'anchors must be an array');
    assert.ok(room.anchors.length > 0,                     'anchors must not be empty');
  });

  it('default_glow_intensity is in [0, 1]', () => {
    const g = room.default_glow_intensity;
    assert.ok(g >= 0 && g <= 1, `default_glow_intensity ${g} is out of [0,1]`);
  });

  it('stress_glow_curve_default has 5 values in [0, 1]', () => {
    const curve = room.stress_glow_curve_default;
    assert.ok(Array.isArray(curve), 'stress_glow_curve_default must be an array');
    assert.equal(curve.length, 5, 'stress_glow_curve_default must have 5 values');
    curve.forEach((v, i) => {
      assert.ok(v >= 0 && v <= 1, `stress_glow_curve_default[${i}] = ${v} is out of [0,1]`);
    });
  });

  for (const anchor of room.anchors) {
    it(`anchor "${anchor.id}" has required fields`, () => {
      assert.ok(typeof anchor.id       === 'string',  `${anchor.id}: id must be a string`);
      assert.ok(typeof anchor.label    === 'string',  `${anchor.id}: label must be a string`);
      assert.ok(typeof anchor.hotspot  === 'object',  `${anchor.id}: hotspot must be an object`);
      assert.ok(Array.isArray(anchor.symbol_ids),     `${anchor.id}: symbol_ids must be an array`);
    });

    it(`anchor "${anchor.id}" hotspot stays within [0, 1]`, () => {
      const { x, y, w, h } = anchor.hotspot;
      assert.ok(x >= 0 && x <= 1, `${anchor.id}: hotspot.x=${x} out of bounds`);
      assert.ok(y >= 0 && y <= 1, `${anchor.id}: hotspot.y=${y} out of bounds`);
      assert.ok(w > 0  && w <= 1, `${anchor.id}: hotspot.w=${w} out of bounds`);
      assert.ok(h > 0  && h <= 1, `${anchor.id}: hotspot.h=${h} out of bounds`);
      assert.ok(x + w <= 1.001,   `${anchor.id}: hotspot x+w=${x + w} exceeds 1`);
      assert.ok(y + h <= 1.001,   `${anchor.id}: hotspot y+h=${y + h} exceeds 1`);
    });

    if (anchor.stress_glow_curve !== null) {
      it(`anchor "${anchor.id}" stress_glow_curve has 5 values in [0, 1]`, () => {
        const curve = anchor.stress_glow_curve;
        assert.ok(Array.isArray(curve), `${anchor.id}: stress_glow_curve must be an array`);
        assert.equal(curve.length, 5,   `${anchor.id}: stress_glow_curve must have 5 values`);
        curve.forEach((v, i) => {
          assert.ok(v >= 0 && v <= 1,   `${anchor.id}: stress_glow_curve[${i}]=${v} out of [0,1]`);
        });
      });
    }
  }
});

// ─────────────────────────────────────────────────────────────
// 2. Symbol resolution
// ─────────────────────────────────────────────────────────────
describe('symbol resolution', () => {

  for (const anchor of room.anchors) {
    it(`all symbol_ids in anchor "${anchor.id}" exist in vocabulary.json`, () => {
      const missing = anchor.symbol_ids.filter(id => !symById[id]);
      assert.deepEqual(
        missing, [],
        `${anchor.id}: unknown symbol_ids: ${missing.join(', ')}`
      );
    });

    it(`all symbol_ids in anchor "${anchor.id}" have allowed_for_grid: true`, () => {
      const notGrid = anchor.symbol_ids.filter(id => symById[id] && !symById[id].allowed_for_grid);
      assert.deepEqual(
        notGrid, [],
        `${anchor.id}: symbols not allowed for grid: ${notGrid.join(', ')}`
      );
    });

    it(`anchor "${anchor.id}" has no duplicate symbol_ids`, () => {
      const seen = new Set();
      const dupes = [];
      for (const id of anchor.symbol_ids) {
        if (seen.has(id)) dupes.push(id);
        seen.add(id);
      }
      assert.deepEqual(dupes, [], `${anchor.id}: duplicate symbol_ids: ${dupes.join(', ')}`);
    });
  }
});

// ─────────────────────────────────────────────────────────────
// 3. Tier coverage
// ─────────────────────────────────────────────────────────────
describe('tier coverage', () => {

  it('all tier-1 grid symbols are covered by at least one anchor', () => {
    const uncovered = gridSymbols
      .filter(s => s.priority_tier === 1 && !allAnchorSymbolIds.has(s.id))
      .map(s => s.id);
    assert.deepEqual(
      uncovered, [],
      `Tier-1 symbols missing from all anchors:\n  ${uncovered.join('\n  ')}`
    );
  });

  it('all tier-2 grid symbols are covered by at least one anchor', () => {
    const uncovered = gridSymbols
      .filter(s => s.priority_tier === 2 && !allAnchorSymbolIds.has(s.id))
      .map(s => s.id);
    assert.deepEqual(
      uncovered, [],
      `Tier-2 symbols missing from all anchors:\n  ${uncovered.join('\n  ')}`
    );
  });
});

// ─────────────────────────────────────────────────────────────
// 4. Stress glow integrity
// ─────────────────────────────────────────────────────────────
describe('stress glow integrity', () => {

  it('default_glow_intensity is a finite number in [0, 1]', () => {
    const g = room.default_glow_intensity;
    assert.ok(Number.isFinite(g),  'default_glow_intensity must be finite');
    assert.ok(g >= 0 && g <= 1,   `default_glow_intensity ${g} out of [0,1]`);
  });

  it('stress_glow_curve_default values are monotonically non-decreasing', () => {
    const curve = room.stress_glow_curve_default;
    for (let i = 1; i < curve.length; i++) {
      assert.ok(
        curve[i] >= curve[i - 1],
        `stress_glow_curve_default is not non-decreasing at index ${i}: ${curve[i - 1]} -> ${curve[i]}`
      );
    }
  });

  it('per-anchor stress_glow_curves are monotonically non-decreasing', () => {
    for (const anchor of room.anchors) {
      if (!Array.isArray(anchor.stress_glow_curve)) continue;
      const curve = anchor.stress_glow_curve;
      for (let i = 1; i < curve.length; i++) {
        assert.ok(
          curve[i] >= curve[i - 1],
          `${anchor.id}: stress_glow_curve not non-decreasing at index ${i}: ${curve[i - 1]} -> ${curve[i]}`
        );
      }
    }
  });
});
