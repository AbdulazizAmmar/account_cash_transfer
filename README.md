# Account Cash Transfer Module (`account_cash_transfer`)

**Version:** 19.0.1.0.0  
**License:** LGPL-3  
**Category:** Accounting  
**Odoo Target:** Odoo 19.0  

---

## 📖 Module Overview

The `account_cash_transfer` module provides a dedicated workflow for moving funds internally between cash and bank journals. It automates the double-entry accounting operations by generating paired journal entries using the company's designated **Internal Transfer Account**.

---

## 📁 File Structure

```
account_cash_transfer/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── account_cash_transfer.py    # Main business model & logic
│   └── account_move.py             # Extension linking move to cash transfer
├── security/
│   └── ir.model.access.csv         # Access control rules (User & Manager)
└── views/
    └── account_cash_transfer_views.xml  # Sequence, views, action, menu
```

---

## 🗃️ Data Model Specifications

### 1. `account.cash.transfer` (Main Model)

| Field Name | Type | Description | Attributes |
|---|---|---|---|
| `name` | `Char` | Auto-generated reference number (e.g. `CT/2026/0001`) | Readonly, Default: `'New'` |
| `amount` | `Monetary` | Transfer amount | Required, Tracked |
| `currency_id` | `Many2one` | Currency (defaults to company currency) | Required |
| `from_journal_id` | `Many2one` | Source journal (`account.journal`) | Domain: Cash/Bank, Required, Tracked |
| `to_journal_id` | `Many2one` | Destination journal (`account.journal`) | Domain: Cash/Bank, Required, Tracked |
| `note` | `Text` | Additional details / internal notes | Readonly when confirmed |
| `date` | `Date` | Transfer date | Default: Today, Required |
| `user_id` | `Many2one` | Responsible user (`res.users`) | Readonly, Default: Current User |
| `state` | `Selection` | Record status (`draft`, `confirmed`) | Default: `'draft'`, Required, Tracked |
| `move_ids` | `One2many` | Related journal entries (`account.move`) | Readonly |
| `company_id` | `Many2one` | Company reference (`res.company`) | Required, Default: Current Company |

### 2. `account.move` (Extension)

| Field Name | Type | Description |
|---|---|---|
| `cash_transfer_id` | `Many2one` | Inverse relation pointing to `account.cash.transfer` |

---

## ⚙️ Business Logic & Accounting Workflow

### Confirmation Workflow (`action_confirm`)

When a user clicks the **Confirm** button in `draft` state:

1. **Validation Checks**:
   - `from_journal_id` and `to_journal_id` must be different.
   - `amount` must be strictly positive (`> 0`).
   - Company must have an `Internal Transfer Account` (`company_id.transfer_account_id`).
   - Both journals must have a valid `default_account_id`.

2. **Dynamic Label Generation**:
   ```python
   label = f"Cash transfer from {from_journal_id.name} to {to_journal_id.name} by {user_id.name} at {date}"
   ```

3. **Journal Entry 1 (Outflow from Source Journal)**:
   - **Journal**: `from_journal_id`
   - **Credit**: `from_journal_id.default_account_id` (Amount: `amount`)
   - **Debit**: `company_id.transfer_account_id` (Amount: `amount`)

4. **Journal Entry 2 (Inflow to Destination Journal)**:
   - **Journal**: `to_journal_id`
   - **Debit**: `to_journal_id.default_account_id` (Amount: `amount`)
   - **Credit**: `company_id.transfer_account_id` (Amount: `amount`)

5. **State Transition**: Updates state to `'confirmed'`.

---

## 🔒 Security & Access Rights

Defined in `security/ir.model.access.csv`:

* **Accounting User (`account.group_account_user`)**: Read, Write, Create (No Delete)
* **Accounting Manager (`account.group_account_manager`)**: Full CRUD (Read, Write, Create, Delete)

---

## 🖥️ User Interface Details

- **Menu Path**: `Accounting` → `Cash Transfers`
- **List View**: Highlights draft vs confirmed transfers, provides column totals.
- **Form View**:
  - Header status bar with dynamic action button (`Confirm`).
  - Organized layout into Transfer Details, Other Information, Notes, and generated Journal Entries tab.
  - Full chatter integration for log tracking and activities.
- **Search View**: Includes custom filters (`Draft`, `Confirmed`, `Today`) and group-by rules (`Status`, `From Journal`, `To Journal`, `Date`, `User`).

---

## 🚀 Next Steps / Future Roadmap

If you plan to extend this module further, consider the following enhancements:

- [ ] **Reset to Draft / Cancel Action**: Add an action to cancel a transfer and reverse/cancel the associated `account.move` records.
- [ ] **Post Entries Automatically**: Currently moves are created in draft state. Option to auto-post moves (`move.action_post()`) on confirmation.
- [ ] **Multi-Currency Support**: Support currency exchange rate differences if transferring between journals with different currencies.
- [ ] **Print/PDF Report**: Add a printable voucher/receipt report for cash transfer authorization.
