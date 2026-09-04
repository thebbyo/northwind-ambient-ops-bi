import crypto from 'crypto';

/**
 * Converts a UTC ISO string to America/Chicago date representation (YYYY-MM-DD).
 * Handles daylight saving time (CDT is UTC-5, CST is UTC-6).
 */
export function toChicagoDate(utcIsoString) {
  if (!utcIsoString) return null;
  const date = new Date(utcIsoString);
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Chicago',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  const parts = formatter.formatToParts(date);
  const year = parts.find(p => p.type === 'year').value;
  const month = parts.find(p => p.type === 'month').value;
  const day = parts.find(p => p.type === 'day').value;
  return `${year}-${month}-${day}`;
}

/**
 * Validates if an instant belongs to Q2 FY26 in America/Chicago (2026-04-01 through 2026-06-30).
 */
export function isWithinQ2Chicago(utcIsoString) {
  const chicagoDate = toChicagoDate(utcIsoString);
  if (!chicagoDate) return false;
  return chicagoDate >= '2026-04-01' && chicagoDate <= '2026-06-30';
}

/**
 * Deduplicates raw note ingestion records to the latest version per note_id.
 */
export function deduplicateNotes(notes) {
  const map = new Map();
  for (const note of notes) {
    const existing = map.get(note.note_id);
    if (!existing || new Date(note.ingested_at_utc) > new Date(existing.ingested_at_utc)) {
      map.set(note.note_id, note);
    }
  }
  return Array.from(map.values());
}

/**
 * Resolves the SLA target in minutes based on product line, priority, and encounter date.
 */
export function getEffectiveSlaTarget(productLine, priority, encounterDateStr, slaConfigs) {
  const targetDate = encounterDateStr.slice(0, 10);
  const matched = slaConfigs.find(s => 
    s.product_line === productLine &&
    s.priority === priority &&
    s.effective_from <= targetDate &&
    (!s.effective_to || s.effective_to >= targetDate)
  );
  return matched ? matched.target_minutes : null;
}

/**
 * Deterministically recalculates the weighted composite score for an audit.
 */
export function calculateCompositeScore(scores, rubricVersion, rubricWeights) {
  const weights = rubricWeights[rubricVersion];
  if (!weights) throw new Error(`Unknown rubric version: ${rubricVersion}`);

  const raw = (
    scores.accuracy * weights.accuracy +
    scores.completeness * weights.completeness +
    scores.formatting * weights.formatting +
    scores.terminology * weights.terminology +
    scores.hpi * weights.hpi +
    scores.ros * weights.ros +
    scores.plan * weights.plan
  );

  return Math.round(raw * 10000) / 10000;
}

/**
 * Generates an idempotent execution key for the stranded escalation recovery worker.
 */
export function generateIdempotencyKey(escalationId, attemptNumber) {
  if (!escalationId || attemptNumber == null) {
    throw new Error('escalationId and attemptNumber are required');
  }
  return crypto.createHash('sha256').update(`${escalationId}:${attemptNumber}`).digest('hex');
}
