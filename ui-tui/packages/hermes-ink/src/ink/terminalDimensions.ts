import {
  DEFAULT_COLUMNS,
  DEFAULT_ROWS,
  MAX_COLUMNS,
  MAX_ROWS,
  MIN_COLUMNS,
  MIN_ROWS
} from './constants.js'

/**
 * Sanitize a single terminal dimension (columns or rows).
 *
 * Returns the clamped integer value when `value` is a finite number within
 * [min, max]; otherwise returns the fallback default.
 *
 * This exists because `value || fallback` and `value ?? fallback` both pass
 * absurd values like 131072 (a common WSL bug) through:
 *   - `||` treats 131072 as truthy → passes through
 *   - `??` treats 131072 as not nullish → passes through
 */
export function sanitizeDimension(
  value: unknown,
  min: number,
  max: number,
  fallback: number
): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return fallback
  }
  if (value < min || value > max) {
    return fallback
  }
  // Floor fractional values (e.g., 80.9 → 80)
  return Math.floor(value)
}

/** Sanitize a {columns, rows} pair. Returns a new object. */
export function sanitizeTerminalSize(
  columns: unknown,
  rows: unknown
): { columns: number; rows: number } {
  return {
    columns: sanitizeDimension(columns, MIN_COLUMNS, MAX_COLUMNS, DEFAULT_COLUMNS),
    rows: sanitizeDimension(rows, MIN_ROWS, MAX_ROWS, DEFAULT_ROWS)
  }
}
