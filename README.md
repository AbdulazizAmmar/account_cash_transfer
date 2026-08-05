# Cash Management & Account Cash Transfer Module (`account_cash_transfer`)

**Version:** 19.0.1.0.0  
**License:** LGPL-3  
**Category:** Accounting/Cash Management  
**Odoo Target:** Odoo 19.0  

---

## 📖 Module Overview

The `account_cash_transfer` module provides a standalone custom application and workflow for managing cash and bank internal transfers. It automates double-entry accounting operations by generating and posting paired journal entries using the company's designated **Internal Transfer Account**. It also includes a real-time **Cash & Bank Dashboard** displaying live balances for all cash/bank journals and quick access to journal transactions.

---

## 📁 File Structure

```
account_cash_transfer/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── account_cash_transfer.py    # Main business model & transfer confirmation logic
│   ├── account_journal.py          # Dashboard extension: live balance calculation & shortcuts
│   └── account_move.py             # Extension linking move entries to cash transfer
├── security/
│   └── ir.model.access.csv         # Access control rules (User & Manager)
└── views/
    └── account_cash_transfer_views.xml  # Dashboard kanban, list, form, search views & menu structure
```

---

## 🗃️ Data Model Specifications

### 1. `account.cash.transfer` (Main Transfer Model)

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

### 2. `account.journal` (Dashboard Extension)

| Field Name | Type | Description |
|---|---|---|
| `current_cash_balance` | `Monetary` | Computed live balance (`debit - credit`) for the journal's default account |
| `cash_transfer_count` | `Integer` | Computed total count of transfers associated with the journal |

### 3. `account.move` (Extension)

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

5. **Auto-Posting & State Transition**:
   - Executes `moves.action_post()` to automatically post both journal entries.
   - Updates transfer state to `'confirmed'`.

---

## 🔒 Security & Access Rights

Defined in `security/ir.model.access.csv`:

* **Accounting User (`account.group_account_user`)**: Read, Write, Create (No Delete)
* **Accounting Manager (`account.group_account_manager`)**: Full CRUD (Read, Write, Create, Delete)

---

## 🖥️ Standalone Application & Menu Navigation

- **Main App Menu**: **Cash Management** (Standalone main application)
- **Sub-menus**:
  - 📊 **Dashboard**: Interactive Kanban view displaying each cash/bank journal with live balance, transaction counts, "View Transactions", and "+ New Transfer" shortcuts.
  - 🔄 **Transfers**: List and form views for managing all cash transfer records.

---

## 🚀 Future Roadmap

- [ ] **Reset to Draft / Cancel Action**: Action to cancel/reverse confirmed transfers.
- [ ] **Multi-Currency Rate Differentials**: Automatic gain/loss entry for cross-currency transfers.
- [ ] **PDF Voucher Receipt**: Printable authorization receipt for physical cash handling.
