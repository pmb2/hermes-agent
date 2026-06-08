// Shared frame interval for render throttling and animations (~60fps).
export const FRAME_INTERVAL_MS = 16

// Keep clock-driven animations at full speed when terminal focus changes.
// We still pause entirely when there are no keepAlive subscribers.
export const BLURRED_FRAME_INTERVAL_MS = FRAME_INTERVAL_MS

// Terminal dimension bounds for WSL 131072x1 / bogus-size defense.
// Some hosts report absurd window sizes (e.g., 131072 columns by 1 row)
// that pass through `value || fallback` and `value ?? fallback` checks
// because 131072 is truthy and not nullish.  These bounds prevent frame
// allocation from exploding (131072*1 * 8 bytes per char → ~1 MB/frame
// for a single screen line before yoga layout even runs).
export const MAX_COLUMNS = 2000
export const MIN_COLUMNS = 1
export const MAX_ROWS = 1000
export const MIN_ROWS = 1
export const DEFAULT_COLUMNS = 80
export const DEFAULT_ROWS = 24
