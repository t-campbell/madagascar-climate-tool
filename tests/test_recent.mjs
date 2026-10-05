import assert from "node:assert/strict";
import { rainfallDifference, baselineMonth, expectedFinalMonth } from "../site/recent.js";

assert.deepEqual(rainfallDifference(150, 100), { mm: 50, percent: 50 });
assert.deepEqual(rainfallDifference(0, 100), { mm: -100, percent: -100 });
assert.deepEqual(rainfallDifference(20, 0), { mm: 20, percent: null });
assert.equal(rainfallDifference(20, 0.9).percent, null);
assert.equal(baselineMonth("2025-12"), 11);
assert.equal(baselineMonth("2026-01"), 0);
assert.throws(() => baselineMonth("2026-13"));
assert.equal(expectedFinalMonth(new Date("2026-01-05T12:00:00Z")), "2025-11");
assert.equal(expectedFinalMonth(new Date("2026-01-28T12:00:00Z")), "2025-12");
console.log("recent rainfall comparison tests passed");
