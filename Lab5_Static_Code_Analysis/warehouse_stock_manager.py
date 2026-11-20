"""Warehouse stock manager.

Receives and issues stock per SKU, flags SKUs that need reordering, saves
stock levels to a JSON file and lets a supervisor adjust a SKU's quantity
with a simple arithmetic formula.

Author: Pramay Dubey (SRN: PES2UG24CS361)
Lab 5: Static Code Analysis
"""

import ast
import hashlib
import hmac
import json
import logging
import operator
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Module-level stock store: SKU -> units on hand
warehouse_stock = {}
AUDIT_FILE = "warehouse_audit.log"
# The supervisor password is read from this environment variable at run time
# instead of being hard-coded in the source.
SUPERVISOR_ENV_VAR = "WH_SUPERVISOR_PASSWORD"

# Operators a supervisor formula is allowed to use
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
}


def _valid_sku(sku):
    """Return True if ``sku`` is a non-empty string."""
    return isinstance(sku, str) and bool(sku.strip())


def _valid_qty(qty):
    """Return True if ``qty`` is a positive whole number."""
    return isinstance(qty, int) and not isinstance(qty, bool) and qty > 0


def add_stock(sku="default", qty=0, history=None):
    """Receive ``qty`` units of ``sku``. Returns True on success."""
    if history is None:
        history = []
    if not _valid_sku(sku):
        logger.warning("Rejected receipt: invalid SKU %r", sku)
        return False
    if not _valid_qty(qty):
        logger.warning("Rejected receipt for %s: invalid quantity %r",
                       sku, qty)
        return False
    warehouse_stock[sku] = warehouse_stock.get(sku, 0) + qty
    history.append(f"{datetime.now()}: Received {qty} units of {sku}")
    logger.info("Received %d units of %s", qty, sku)
    return True


def remove_stock(sku, qty):
    """Issue ``qty`` units of ``sku``. Returns True on success.

    The request is rejected if the SKU is unknown or if it asks for more
    units than are on hand.
    """
    if not _valid_qty(qty):
        logger.warning("Rejected issue for %s: invalid quantity %r", sku, qty)
        return False
    try:
        on_hand = warehouse_stock[sku]
    except KeyError:
        logger.warning("Rejected issue: SKU %s not in stock", sku)
        return False
    if qty > on_hand:
        logger.warning("Rejected issue of %d units of %s: only %d on hand",
                       qty, sku, on_hand)
        return False
    warehouse_stock[sku] = on_hand - qty
    if warehouse_stock[sku] == 0:
        del warehouse_stock[sku]
    logger.info("Issued %d units of %s", qty, sku)
    return True


def get_stock(sku):
    """Return the units on hand for ``sku`` (0 if it is not stocked)."""
    return warehouse_stock.get(sku, 0)


def sku_checksum(sku):
    """Return a short fingerprint printed on bin labels.

    MD5 is kept so existing labels stay valid; it is only a label checksum,
    not a security control, so it is marked ``usedforsecurity=False``.
    """
    return hashlib.md5(sku.encode(), usedforsecurity=False).hexdigest()[:6]


def load_stock(file="warehouse.json"):
    """Replace the current stock with the contents of a JSON file."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.warning("%s not found; keeping current stock", file)
        return
    except json.JSONDecodeError as err:
        logger.error("Could not parse %s: %s", file, err)
        return
    warehouse_stock.clear()
    warehouse_stock.update(data)


def save_stock(file="warehouse.json"):
    """Write the current stock levels to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(warehouse_stock, f, indent=2)


def print_report():
    """Print every SKU with its units on hand and label checksum."""
    print("Warehouse Stock Report")
    for sku, qty in warehouse_stock.items():
        print(f"{sku} -> {qty} units  [chk: {sku_checksum(sku)}]")


def check_reorder(threshold=10):
    """Return the SKUs whose stock is below ``threshold``."""
    return [sku for sku, qty in warehouse_stock.items() if qty < threshold]


def _eval_node(node, current):
    """Evaluate one node of a parsed supervisor formula."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, current)
    if isinstance(node, ast.Name) and node.id == "current":
        return current
    if (isinstance(node, ast.Constant) and isinstance(node.value, int)
            and not isinstance(node.value, bool)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        left = _eval_node(node.left, current)
        right = _eval_node(node.right, current)
        return _ALLOWED_OPS[type(node.op)](left, right)
    raise ValueError("formula may only use 'current', whole numbers "
                     "and + - * //")


def evaluate_formula(formula, current):
    """Safely evaluate a formula such as ``"current * 2"``.

    Only the name ``current``, integer literals and the operators
    ``+ - * //`` are accepted; anything else raises ValueError.
    """
    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError as err:
        raise ValueError(f"invalid formula: {formula!r}") from err
    return _eval_node(tree, current)


def apply_adjustment(sku, formula, password):
    """Set ``sku`` to the result of ``formula`` (supervisor only).

    Returns True if the adjustment was applied.
    """
    expected = os.environ.get(SUPERVISOR_ENV_VAR)
    if not expected:
        logger.error("Adjustments disabled: %s is not set", SUPERVISOR_ENV_VAR)
        return False
    if not hmac.compare_digest(str(password), expected):
        logger.warning("Rejected adjustment of %s: wrong password", sku)
        return False
    current = warehouse_stock.get(sku, 0)
    try:
        new_qty = evaluate_formula(formula, current)
    except (ValueError, ZeroDivisionError) as err:
        logger.warning("Rejected adjustment of %s: %s", sku, err)
        return False
    if new_qty < 0:
        logger.warning("Rejected adjustment of %s: result %d is negative",
                       sku, new_qty)
        return False
    warehouse_stock[sku] = new_qty
    with open(AUDIT_FILE, "a", encoding="utf-8") as audit:
        audit.write(f"adjusted {sku} from {current} to {new_qty} using "
                    f"formula {formula!r} at {datetime.now()}\n")
    logger.info("Adjusted %s from %d to %d", sku, current, new_qty)
    return True


def main():
    """Run the built-in demo."""
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    add_stock("WID-001", 40)
    add_stock("WID-002", -4)        # rejected: negative quantity
    add_stock(404, 15)              # rejected: SKU must be a string
    remove_stock("WID-001", 12)
    remove_stock("GHOST-9", 1)      # rejected: unknown SKU
    remove_stock("WID-001", 500)    # rejected: more than on hand
    print("WID-002 stock:", get_stock("WID-002"))
    print("Needs reorder:", check_reorder())
    # The supervisor's password is taken from the environment for the demo.
    supervisor_password = os.environ.get(SUPERVISOR_ENV_VAR, "")
    apply_adjustment("WID-002", "current + 25", supervisor_password)
    apply_adjustment("WID-002", "__import__('os').getcwd()",
                     supervisor_password)  # rejected: not arithmetic
    save_stock()
    load_stock()
    print_report()
    print("stock audit complete")


if __name__ == "__main__":
    main()
