import test from 'node:test';
import assert from 'node:assert/strict';
import {
  toChicagoDate,
  isWithinQ2Chicago,
  deduplicateNotes,
  getEffectiveSlaTarget,
  calculateCompositeScore,
  generateIdempotencyKey
} from '../src/logic.js';

test('Timezone boundary: UTC vs America/Chicago business date', () => {
  // 2026-04-01 02:00:00 UTC is March 31, 2026 21:00:00 CDT (NOT in Q2 yet!)
  assert.equal(toChicagoDate('2026-04-01T02:00:00Z'), '2026-03-31');
  assert.equal(isWithinQ2Chicago('2026-04-01T02:00:00Z'), false);

  // 2026-04-01 05:00:00 UTC is exactly April 1, 2026 00:00:00 CDT (Q2 starts!)
  assert.equal(toChicagoDate('2026-04-01T05:00:00Z'), '2026-04-01');
  assert.equal(isWithinQ2Chicago('2026-04-01T05:00:00Z'), true);

  // 2026-07-01 04:59:59 UTC is June 30, 2026 23:59:59 CDT (Still in Q2!)
  assert.equal(toChicagoDate('2026-07-01T04:59:59Z'), '2026-06-30');
  assert.equal(isWithinQ2Chicago('2026-07-01T04:59:59Z'), true);

  // 2026-07-01 05:00:00 UTC is July 1, 2026 00:00:00 CDT (Q3 starts, outside Q2!)
  assert.equal(toChicagoDate('2026-07-01T05:00:00Z'), '2026-07-01');
  assert.equal(isWithinQ2Chicago('2026-07-01T05:00:00Z'), false);
});

test('Deduplication: Note re-ingestions resolve to latest ingested_at_utc', () => {
  const rawNotes = [
    { note_id: 'NT-001', ingestion_id: 'IG-001-1', ingested_at_utc: '2026-04-05T10:00:00Z', val: 'old' },
    { note_id: 'NT-002', ingestion_id: 'IG-002-1', ingested_at_utc: '2026-04-05T11:00:00Z', val: 'unique' },
    { note_id: 'NT-001', ingestion_id: 'IG-001-2', ingested_at_utc: '2026-04-06T14:30:00Z', val: 'newest' }
  ];

  const deduped = deduplicateNotes(rawNotes);
  assert.equal(deduped.length, 2);
  const nt1 = deduped.find(n => n.note_id === 'NT-001');
  assert.equal(nt1.ingestion_id, 'IG-001-2');
  assert.equal(nt1.val, 'newest');
});

test('Effective-dated SLA lookup: Pre-May 15 vs Post-May 15 targets', () => {
  const slaConfigs = [
    { product_line: 'AMBIENT_ASSIST', priority: 'STANDARD', target_minutes: 45, effective_from: '2025-01-01', effective_to: '2026-05-14' },
    { product_line: 'AMBIENT_ASSIST', priority: 'STANDARD', target_minutes: 30, effective_from: '2026-05-15', effective_to: null }
  ];

  // On May 14, 2026 -> should resolve to 45 min
  const preCutover = getEffectiveSlaTarget('AMBIENT_ASSIST', 'STANDARD', '2026-05-14T23:59:59Z', slaConfigs);
  assert.equal(preCutover, 45);

  // On May 15, 2026 -> should resolve to 30 min
  const postCutover = getEffectiveSlaTarget('AMBIENT_ASSIST', 'STANDARD', '2026-05-15T00:00:00Z', slaConfigs);
  assert.equal(postCutover, 30);
});

test('Composite score recalculation: Detects discrepancy against rubric weights', () => {
  const rubricWeights = {
    v2: {
      accuracy: 0.35,
      completeness: 0.25,
      formatting: 0.05,
      terminology: 0.10,
      hpi: 0.10,
      ros: 0.05,
      plan: 0.10
    }
  };

  // Case AU-10829 sub-scores:
  const scores = {
    accuracy: 0.8906,
    completeness: 0.9738,
    formatting: 0.9196,
    terminology: 0.9476,
    hpi: 0.8870,
    ros: 0.9378,
    plan: 0.9311
  };

  const trueCalculated = calculateCompositeScore(scores, 'v2', rubricWeights);
  assert.equal(trueCalculated, 0.9246);
  // Stored score was falsely recorded as 0.7890 FAIL
  const discrepancy = Math.abs(trueCalculated - 0.7890);
  assert.ok(discrepancy > 0.13, 'Discrepancy must exceed 13% for AU-10829');
});

test('Idempotency Key: Deterministic and unique across attempts', () => {
  const key1 = generateIdempotencyKey('ES-50001', 1);
  const key2 = generateIdempotencyKey('ES-50001', 1);
  const key3 = generateIdempotencyKey('ES-50001', 2);

  // Identical inputs yield identical keys (safe to retry)
  assert.equal(key1, key2);
  // Different attempts yield different keys
  assert.notEqual(key1, key3);
});
