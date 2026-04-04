# BakeryOS Frontend RBAC Authorization Audit Report

Date: 2026-04-04
Scope: React frontend authorization behavior for Manager, Cashier, Baker, Storekeeper.

## 1) Executive Summary

This audit reviewed role-based access control (RBAC) across:
- Sidebar menu visibility
- Page rendering/navigation control
- In-page action/button visibility

Primary finding:
- Sidebar role filtering is implemented, but page-level authorization is not centrally enforced.
- Because app navigation is driven by local state (`activeMenuItem`) and a global `navigate` event, roles can potentially render unauthorized pages by triggering that event or manipulating UI state.

Risk level: High (authorization bypass at frontend rendering layer).

Important note:
- Backend API authorization still exists and remains the real security boundary.
- Frontend gaps are still serious because they expose unauthorized UI flows and potentially sensitive data views.

---

## 2) Files Audited

Core authorization/navigation files:
- `Frontend/src/App.tsx`
- `Frontend/src/components/Sidebar.tsx`
- `Frontend/src/context/AuthContext.tsx`

Major feature modules reviewed for action-level guards:
- `Frontend/src/components/StockManagementScreen.tsx`
- `Frontend/src/components/WastageOverview.tsx`
- `Frontend/src/components/SalesSummary.tsx`
- `Frontend/src/components/DiscountManagement.tsx`
- `Frontend/src/components/UserManagement.tsx`
- `Frontend/src/components/StaffTable.tsx`
- `Frontend/src/components/BillingScreen.tsx`
- `Frontend/src/components/NotificationScreen.tsx`
- `Frontend/src/components/Dashboard.tsx`
- `Frontend/src/components/dashboard/ManagerDashboard.tsx`
- `Frontend/src/components/modal/ItemStockHistoryModal.tsx`
- `Frontend/src/components/modal/ingredient modal/IngredientStockHistoryModal.tsx`

---

## 3) Current Authorization Model

### 3.1 Sidebar Visibility (Implemented)
`Sidebar.tsx` defines a `menuItems` array with allowed `roles` and hides disallowed items.

Observed role map in sidebar:
- dashboard: Manager, Baker, Storekeeper
- billing: Manager, Cashier
- stock: Manager, Baker, Storekeeper, Cashier
- wastage: Manager, Baker, Storekeeper, Cashier
- saleshistory: Manager, Cashier
- discount: Manager, Cashier
- notification: all roles
- users: Manager only

Conclusion:
- Sidebar filtering logic is present and generally aligned with intended visibility behavior.

### 3.2 Page Rendering/Route Protection (Not Fully Implemented)
`App.tsx` renders pages using a `switch(activeMenuItem)` without validating role permissions at render time.
It also listens to a global event (`window.addEventListener('navigate', ...)`) and directly sets `activeMenuItem` from event payload.

Conclusion:
- There is no centralized page guard before rendering content.
- Any role with authenticated session can potentially render unauthorized modules in frontend if navigation state is changed outside sidebar controls.

### 3.3 Action-Level Guards (Partially Implemented)
Some components use role checks (`isManager`, `isCashier`, etc.), but coverage is inconsistent.

---

## 4) Detailed Role-by-Role Findings

## 4.1 Manager

### Route/Page Access
Current behavior:
- Manager can render all pages in `App.tsx` (expected).

Unexpected access:
- None for manager (manager is intended to have broad access).

### Sidebar Visibility
Current behavior:
- Manager sees all menu items.

### Action Visibility
Current behavior:
- Manager-only controls are correctly enforced in some modules (e.g., discount management mutation controls, manager dashboard summary export).

### Gaps
- No direct manager gap. Global app-level guard absence still applies system-wide.

---

## 4.2 Cashier

### Route/Page Access
Expected (from sidebar policy):
- Billing, Stock, Wastage, Sales History, Discount, Notification
- Not Dashboard, not Users

Current behavior:
- Sidebar hides Dashboard and Users.
- But page rendering in `App.tsx` does not enforce role checks.

Risk:
- Cashier can potentially render restricted pages (e.g., Users) if navigation state is altered.

### Sidebar Visibility
Current behavior:
- Matches configured menu roles.

### Action Visibility (High-impact checks)
- Stock page:
  - Cashier sees Export PDF/Export Excel buttons.
  - This conflicts with the comment that cashier is "view only".
- Stock history modals:
  - "Waste" action is visible broadly.
- Wastage page:
  - Cashier can see export buttons and reason-management buttons.
- Users page:
  - If accessed through state bypass, Add/Edit/Delete controls are visible.

### Vulnerabilities
- High: can potentially open unauthorized Users page UI.
- Medium: can access export and waste/reason controls that likely exceed cashier privileges.

---

## 4.3 Baker

### Route/Page Access
Expected (from sidebar policy):
- Dashboard, Stock, Wastage, Notification

Current behavior:
- Sidebar matches this.
- No app-level render guard means potential rendering of disallowed modules if state is manipulated.

### Sidebar Visibility
Current behavior:
- Correct per sidebar role map.

### Action Visibility
- Stock page:
  - Baker can edit/delete products.
  - Baker can add product categories/items.
  - Baker can export stock PDF/Excel.
- Wastage page:
  - Baker can export and manage wastage reasons.

Potential mismatch:
- Depending on your role requirements, baker may be over-privileged in product management and reason administration.

### Vulnerabilities
- High: no centralized page guard.
- Medium: potential over-permission in stock and wastage actions.

---

## 4.4 Storekeeper

### Route/Page Access
Expected (from sidebar policy):
- Dashboard, Stock, Wastage, Notification

Current behavior:
- Sidebar matches this.
- App-level guard missing, same potential bypass.

### Sidebar Visibility
Current behavior:
- Correct per sidebar role map.

### Action Visibility
- Stock page:
  - Storekeeper can edit/delete ingredients and add category/item in ingredient context (likely intended).
  - Storekeeper can export stock PDF/Excel.
- Wastage page:
  - Storekeeper can export and manage reasons (may be too broad depending on policy).

### Vulnerabilities
- High: no centralized page guard.
- Medium: reason-management permissions may be broader than intended.

---

## 5) Vulnerability Register (Prioritized)

### V-01: Missing centralized page-level RBAC guard
Severity: High

Symptoms:
- `App.tsx` does not validate role before rendering each page.
- `navigate` event can switch active page key directly.

Impact:
- Unauthorized frontend modules can be rendered.

Recommendation:
- Add a central permission map and enforce it in both:
  - navigation handler
  - renderContent path

---

### V-02: User Management not explicitly role-protected at component entry
Severity: High

Symptoms:
- `UserManagement.tsx` does not check role; it assumes page access is already protected.

Impact:
- If page is rendered by bypassing menu, full user admin UI appears.

Recommendation:
- Add hard guard at component top:
  - if role is not Manager, render "Access Denied" and do not mount action controls.

---

### V-03: Cashier view-only policy not reflected in Stock action toolbar
Severity: Medium

Symptoms:
- Export buttons visible to all stock roles.

Impact:
- Cashier can perform reporting actions beyond view-only intent.

Recommendation:
- Gate stock exports with capability checks (e.g., Manager only, or Manager+Storekeeper if required).

---

### V-04: Wastage reason administration visible too broadly
Severity: Medium

Symptoms:
- Add/View Wastage Reason buttons are visible in `WastageOverview` without role guard.

Impact:
- Non-manager roles may alter reason taxonomy in UI flows.

Recommendation:
- Restrict reason-management controls to Manager (or Manager+Storekeeper, based on requirement doc).

---

### V-05: Scattered role checks with inconsistent patterns
Severity: Medium

Symptoms:
- Different components use different ad-hoc checks.

Impact:
- Easy to miss controls during feature additions.

Recommendation:
- Introduce centralized frontend authorization utilities and capability flags.

---

## 6) Recommended Target Architecture

### 6.1 Single Source of Truth for Page Access
Create a central map in a shared module (example: `src/auth/permissions.ts`):

```ts
export type MenuPage =
  | 'dashboard'
  | 'billing'
  | 'stock'
  | 'wastage'
  | 'saleshistory'
  | 'discount'
  | 'notification'
  | 'users';

export type Role = 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper';

export const PAGE_ACCESS: Record<Role, MenuPage[]> = {
  Manager: ['dashboard', 'billing', 'stock', 'wastage', 'saleshistory', 'discount', 'notification', 'users'],
  Cashier: ['billing', 'stock', 'wastage', 'saleshistory', 'discount', 'notification'],
  Baker: ['dashboard', 'stock', 'wastage', 'notification'],
  Storekeeper: ['dashboard', 'stock', 'wastage', 'notification'],
};

export function canAccessPage(role: Role, page: MenuPage) {
  return PAGE_ACCESS[role]?.includes(page);
}
```

Use this in `App.tsx`:
- when handling `navigate` events
- before rendering content
- when defaulting initial page after login

### 6.2 Capability-based Action Guards
In same module, add capabilities:

```ts
export const ROLE_CAPABILITIES = {
  Manager: {
    manageUsers: true,
    exportStock: true,
    manageWastageReasons: true,
    runExpiryCheck: true,
  },
  Cashier: {
    manageUsers: false,
    exportStock: false,
    manageWastageReasons: false,
    runExpiryCheck: false,
  },
  Baker: {
    manageUsers: false,
    exportStock: false,
    manageWastageReasons: false,
    runExpiryCheck: false,
  },
  Storekeeper: {
    manageUsers: false,
    exportStock: true,
    manageWastageReasons: false,
    runExpiryCheck: false,
  },
} as const;
```

Then use these flags instead of scattered custom checks.

### 6.3 Component Entry Guards for Sensitive Modules
Add top-of-component guards for:
- UserManagement
- DiscountManagement (if Manager-only in your final policy)
- Manager dashboard export controls (already done)

### 6.4 Backend Enforcement Reminder
Keep backend permission classes as final authority.
Frontend should hide controls and block navigation for UX consistency, but API permissions must remain strict.

---

## 7) Role Compliance Snapshot (Current State)

Legend:
- OK = behavior aligns with observed sidebar policy
- GAP = potential mismatch or vulnerability

Manager:
- Sidebar menus: OK
- Page access: OK
- Action controls: Mostly OK

Cashier:
- Sidebar menus: OK
- Page access guard: GAP (global)
- Users management visibility if bypassed: GAP (high)
- Stock exports while "view-only": GAP
- Wastage reason management visibility: GAP

Baker:
- Sidebar menus: OK
- Page access guard: GAP (global)
- Product management scope in stock: Potential GAP (depends on requirements)
- Wastage reason management visibility: Potential GAP

Storekeeper:
- Sidebar menus: OK
- Page access guard: GAP (global)
- Wastage reason management visibility: Potential GAP

---

## 8) Implementation Plan

Phase 1 (Critical)
1. Add centralized page guard in `App.tsx`.
2. Add entry guard to `UserManagement.tsx`.

Phase 2 (Policy hardening)
3. Introduce role capability map.
4. Gate stock export buttons by capability.
5. Gate wastage reason controls by capability.

Phase 3 (Quality)
6. Add RBAC unit tests for permission utility.
7. Add smoke tests for each role menu/action visibility.

---

## 9) QA Checklist for Re-Validation

For each role (Manager, Cashier, Baker, Storekeeper):
- Verify sidebar shows only allowed menu items.
- Attempt forced navigation to each page key; disallowed pages should redirect or deny.
- Validate action buttons against role policy:
  - User management (add/edit/delete)
  - Discount management (add/edit/delete/toggle)
  - Stock exports (PDF/Excel)
  - Wastage reason management
  - Expiry check execution
- Confirm backend returns 403 for any forbidden API mutation attempted manually.

---

## 10) Final Audit Conclusion

The system has a solid start with sidebar role filtering, but authorization is not fully enforced at the page rendering layer. The most critical issue is the missing centralized page guard in `App.tsx`. Implementing a shared RBAC policy (page access + capabilities) and applying component-level entry guards for sensitive modules will close the primary loopholes and make frontend behavior align strictly with role requirements.
