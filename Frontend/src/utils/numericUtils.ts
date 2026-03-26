/**
 * Numeric Utility Functions
 * 
 * Handles safe conversion of backend Decimal fields to JavaScript numbers
 * Backend uses DecimalField which serializes to JSON strings: "450.50"
 * This ensures proper number operations without string concatenation
 */

/**
 * Safely parse a value that might be a string number or actual number
 * @param value - The value to parse (could be string "450.50" or number 450.50)
 * @returns Parsed number, or 0 if parsing fails
 */
export const toNumber = (value: unknown): number => {
  if (value === null || value === undefined) return 0;
  
  const num = Number(value);
  return isNaN(num) ? 0 : num;
};

/**
 * Parse a decimal field from backend that comes as string
 * @param value - The decimal value as string or number
 * @param defaultValue - Default value if parsing fails (default: 0)
 * @returns Parsed decimal number
 */
export const parseDecimal = (value: unknown, defaultValue: number = 0): number => {
  if (value === null || value === undefined) return defaultValue;
  
  const num = parseFloat(String(value));
  return isNaN(num) ? defaultValue : num;
};

/**
 * Ensure an object's numeric fields are proper numbers, not strings
 * Useful for transforming API responses before using them in calculations
 */
export const normalizeNumericFields = <T extends Record<string, any>>(
  obj: T,
  numericFields: (keyof T)[]
): T => {
  const normalized = { ...obj };
  
  numericFields.forEach(field => {
    if (field in normalized) {
      (normalized[field] as any) = toNumber(normalized[field]);
    }
  });
  
  return normalized;
};

/**
 * Sum an array of numeric values that might be strings
 * Safe for use in reduce operations with API data
 */
export const sumNumeric = (values: (string | number | null | undefined)[]): number => {
  return values.reduce<number>((sum, val) => sum + toNumber(val), 0);
};

/**
 * Format a number as currency for display
 * @param value - The numeric value
 * @param currency - Currency symbol (default: "Rs.")
 * @returns Formatted string
 */
export const formatCurrency = (value: unknown, currency: string = 'Rs.'): string => {
  const num = toNumber(value);
  return `${currency} ${num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

/**
 * Multiply two numbers that might come from backend as strings
 * @param a - First number (might be string)
 * @param b - Second number (might be string)
 * @returns Product of a and b
 */
export const multiplyNumeric = (a: unknown, b: unknown): number => {
  return toNumber(a) * toNumber(b);
};

/**
 * Add two numbers that might come from backend as strings
 * @param a - First number (might be string)
 * @param b - Second number (might be string)
 * @returns Sum of a and b
 */
export const addNumeric = (a: unknown, b: unknown): number => {
  return toNumber(a) + toNumber(b);
};

/**
 * Subtract two numbers that might come from backend as strings
 * @param a - First number (might be string)
 * @param b - Second number (might be string)
 * @returns Difference of a and b
 */
export const subtractNumeric = (a: unknown, b: unknown): number => {
  return toNumber(a) - toNumber(b);
};
