// Pure comparison helpers shared by rendering and boundary tests.
export function rainfallDifference(actual, normal) {
  return { mm: actual - normal, percent: normal >= 1 ? 100 * (actual - normal) / normal : null };
}

export function expectedFinalMonth(now = new Date()) {
  // A complete Final month normally follows in week three; allow through day 27.
  const offset = now.getUTCDate() >= 28 ? 1 : 2;
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - offset, 1)).toISOString().slice(0, 7);
}

export function baselineMonth(period) {
  const match = /^(\d{4})-(\d{2})$/.exec(period);
  if (!match || Number(match[2]) < 1 || Number(match[2]) > 12) throw new Error("invalid rainfall period");
  return Number(match[2]) - 1;
}
