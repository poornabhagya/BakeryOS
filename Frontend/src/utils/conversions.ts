/**
 * Conversion functions to transform API responses (with string decimals)
 * to UI types (with numeric values)
 */

import { ApiUser, ApiProduct, ApiSale, ApiSaleItem, UiUser, UiProduct, UiSale, ApiSaleDetail, UiSaleDetail } from './apiTypes';
import { toNumber } from './numericUtils';

/**
 * Convert API User response to UI User format
 * Maps full_name → name, avatar_color → avatarColor
 */
export function convertApiUserToUi(apiUser: ApiUser): UiUser {
  const { full_name, avatar_color, ...rest } = apiUser;
  return {
    ...rest,
    name: full_name,
    avatarColor: avatar_color,
  } as UiUser;
}

/**
 * Convert API Product response to UI Product format
 * Converts string decimal prices to numbers
 */
export function convertApiProductToUi(apiProduct: ApiProduct): UiProduct {
  const { selling_price, cost_price, current_stock, profit_margin, ...rest } = apiProduct;
  return {
    ...rest,
    selling_price: toNumber(selling_price),
    cost_price: toNumber(cost_price),
    current_stock: toNumber(current_stock),
    profitMargin: profit_margin,
  } as UiProduct;
}

/**
 * Convert API Sale response to UI Sale format
 * Converts string decimal amounts to numbers
 */
export function convertApiSaleToUi(apiSale: ApiSale): UiSale {
  const { subtotal, discount_amount, total_amount, ...rest } = apiSale;
  return {
    ...rest,
    subtotal: toNumber(subtotal),
    discount_amount: toNumber(discount_amount),
    total_amount: toNumber(total_amount),
  } as UiSale;
}

/**
 * Convert API SaleItem response to UI SaleItem format
 * Converts string decimal quantities to numbers
 */
export function convertApiSaleItemToUi(apiSaleItem: ApiSaleItem) {
  const { quantity, unit_price, subtotal, ...rest } = apiSaleItem;
  return {
    ...rest,
    quantity: toNumber(quantity),
    unit_price: toNumber(unit_price),
    subtotal: toNumber(subtotal),
  };
}

/**
 * Convert API SaleDetail response to UI SaleDetail format
 * Includes conversion of sale data and all items
 */
export function convertApiSaleDetailToUi(apiSaleDetail: ApiSaleDetail): UiSaleDetail {
  const { subtotal, discount_amount, total_amount, items, ...rest } = apiSaleDetail;
  return {
    ...rest,
    subtotal: toNumber(subtotal),
    discount_amount: toNumber(discount_amount),
    total_amount: toNumber(total_amount),
    items: items.map(convertApiSaleItemToUi),
  } as UiSaleDetail;
}

function formatNumberForUnit(value: number): string {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(2).replace(/\.0+$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
}

/**
 * Smart quantity display formatter for ingredient quantities.
 * Expects database values in base units:
 * - weight: grams (g)
 * - volume: milliliters (ml)
 * - count: nos
 */
export function formatQuantityForDisplay(quantity: number | string, trackingType: string): string {
  const qty = toNumber(quantity);
  const safeQty = Number.isFinite(qty) ? qty : 0;
  const type = (trackingType || '').toLowerCase();

  if (type === 'weight') {
    if (safeQty >= 1000) {
      return `${formatNumberForUnit(safeQty / 1000)} kg`;
    }
    return `${formatNumberForUnit(safeQty)} g`;
  }

  if (type === 'volume') {
    if (safeQty >= 1000) {
      return `${formatNumberForUnit(safeQty / 1000)} L`;
    }
    return `${formatNumberForUnit(safeQty)} ml`;
  }

  if (type === 'count') {
    return `${formatNumberForUnit(safeQty)} nos`;
  }

  return formatNumberForUnit(safeQty);
}

