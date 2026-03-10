import tkinter as tk
from datetime import datetime
import sqlite3
import math
import re

# ── Database ──────────────────────────────────────────────────────────────────
conn = sqlite3.connect("calc_history.db")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression TEXT, result TEXT, timestamp TEXT)''')
conn.commit()

# ── State ─────────────────────────────────────────────────────────────────────
field_text  = ""
field_eval  = ""
calculated  = False
error_state = False

# ── Window ────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.title("Calculator")
window.resizable(False, False)
window.configure(bg="#111111")

W, H = 340, 680
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
window.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

# ── Color palette ─────────────────────────────────────────────────────────────
BG_SHELL   = "#1e1e1e"
BG_HIST    = "#141414"
BG_DISPLAY = "#0d0d0d"
BG_ERROR   = "#2a0808"

GRAY    = ("#f5f5f5", "#3a3a3c", "#636366", "#555558")
ORANGE  = ("#ffffff", "#ff9f0a", "#ffc05b", "#ffb830")
FUNC    = ("#000000", "#d1d1d6", "#a8a8ad", "#e5e5e5")
SPECIAL = ("#c8c8ff", "#2c2c54", "#3d3d80", "#3d3d80")

# ── Outer shell ───────────────────────────────────────────────────────────────
shell = tk.Frame(window, bg=BG_SHELL, bd=0)
shell.pack(fill="both", expand=True, padx=5, pady=5)
tk.Frame(shell, bg="#3a3a3a", height=1).pack(fill="x")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — HISTORY  (clickable to show all history)
# ══════════════════════════════════════════════════════════════════════════════
hist_outer = tk.Frame(shell, bg=BG_HIST)
hist_outer.pack(fill="x")

hist_rows_frame = tk.Frame(hist_outer, bg=BG_HIST)
hist_rows_frame.pack(fill="x", padx=8, pady=(0, 4))

NUM_HIST = 3
hist_labels = []
for i in range(NUM_HIST):
    row_f = tk.Frame(hist_rows_frame, bg=BG_HIST)
    row_f.pack(fill="x")
    expr_l = tk.Label(row_f, text="", font=("Helvetica Neue", 9),
                      fg="#444444", bg=BG_HIST, anchor="w")
    expr_l.pack(side="left")
    res_l  = tk.Label(row_f, text="", font=("Helvetica Neue", 10, "bold"),
                      fg="#666666", bg=BG_HIST, anchor="e")
    res_l.pack(side="right")
    tk.Frame(hist_rows_frame, bg="#222222", height=1).pack(fill="x")
    hist_labels.append((expr_l, res_l))

def refresh_history():
    cur.execute("SELECT expression, result FROM history ORDER BY id DESC LIMIT ?", (NUM_HIST,))
    rows = cur.fetchall()
    for i, (el, rl) in enumerate(hist_labels):
        if i < len(rows):
            expr, res = rows[i]
            color = "#aaaaaa" if i == 0 else "#555555"
            el.config(text=f"{expr} =", fg=color)
            rl.config(text=res, fg=color)
            # Add cursor and click handlers
            el.config(cursor="hand2")
            rl.config(cursor="hand2")
            el.bind("<Button-1>", lambda e, expr=expr, res=res: load_from_history(expr, res))
            rl.bind("<Button-1>", lambda e, expr=expr, res=res: load_from_history(expr, res))
        else:
            el.config(text="", fg="#444444", cursor="arrow")
            rl.config(text="", fg="#666666", cursor="arrow")
            el.unbind("<Button-1>")
            rl.unbind("<Button-1>")

refresh_history()

# Full history panel (hidden by default)
full_hist_frame = tk.Frame(shell, bg=BG_HIST)
full_hist_frame.pack(fill="x")
full_hist_frame.pack_forget()  # Hidden initially

# Listbox with scrollbar for full history - simpler approach
HIST_PANEL_HEIGHT = 200
hist_listbox = tk.Listbox(full_hist_frame, bg=BG_HIST, fg="#aaaaaa", 
                          font=("Helvetica Neue", 10), borderwidth=0,
                          highlightthickness=0, selectbackground="#333333")
hist_scrollbar = tk.Scrollbar(full_hist_frame, orient="vertical", command=hist_listbox.yview)
hist_listbox.configure(yscrollcommand=hist_scrollbar.set)
hist_scrollbar.pack(side="right", fill="y")
hist_listbox.pack(side="left", fill="x", expand=True)

full_hist_visible = False

# Arrow indicator variable
arrow_var = tk.StringVar(value="v")

def toggle_full_history():
    global full_hist_visible
    if full_hist_visible:
        # Hide full history
        full_hist_frame.pack_forget()
        arrow_var.set("v")
        full_hist_visible = False
    else:
        # Show full history
        refresh_full_history()
        full_hist_frame.pack(fill="x")
        arrow_var.set("^")
        full_hist_visible = True

def refresh_full_history():
    # Clear existing items
    hist_listbox.delete(0, tk.END)
    
    cur.execute("SELECT expression, result FROM history ORDER BY id DESC")
    rows = cur.fetchall()
    
    for idx, (expr, res) in enumerate(rows):
        display_text = f"{expr} = {res}"
        hist_listbox.insert(tk.END, display_text)
    
    # Bind click event to load from history
    hist_listbox.bind("<ButtonRelease-1>", lambda e: on_hist_listbox_select())

def load_from_history(expr, res):
    global field_text, field_eval, calculated, error_state
    
    # Close full history panel if open
    if full_hist_visible:
        toggle_full_history()
    
    # Load the expression for continuation as new calculation
    field_text = expr
    field_eval = expr
    calculated = False
    error_state = False
    update_display("", field_text)

def on_hist_listbox_select():
    """Handle selection from full history listbox."""
    selection = hist_listbox.curselection()
    if selection:
        # Get the selected text
        selected_text = hist_listbox.get(selection[0])
        # Extract expression (everything before " = ")
        if " = " in selected_text:
            expr = selected_text.split(" = ")[0]
            # Get result from database
            cur.execute("SELECT result FROM history WHERE expression = ? ORDER BY id DESC LIMIT 1", (expr,))
            row = cur.fetchone()
            if row:
                load_from_history(expr, row[0])

# Make HISTORY label clickable
hist_label = tk.Label(hist_outer, text="HISTORY", font=("Helvetica Neue", 8, "bold"),
             fg="#333333", bg=BG_HIST, anchor="w", cursor="hand2")
hist_label.pack(fill="x", padx=10, pady=(5, 1))
hist_label.bind("<Button-1>", lambda e: toggle_full_history())

# Arrow indicator
arrow_lbl = tk.Label(hist_outer, textvariable=arrow_var, font=("Helvetica Neue", 8),
                     fg="#333333", bg=BG_HIST, cursor="hand2")
arrow_lbl.pack(side="right", padx=10, pady=(5, 1))
arrow_lbl.bind("<Button-1>", lambda e: toggle_full_history())

tk.Frame(shell, bg="#2a2a2a", height=2).pack(fill="x")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DISPLAY (editable)
# ══════════════════════════════════════════════════════════════════════════════
display_frame = tk.Frame(shell, bg=BG_DISPLAY, height=100)
display_frame.pack(fill="x")
display_frame.pack_propagate(False)

expr_var   = tk.StringVar(value="")
result_var = tk.StringVar(value="")

# Small top label: shows "3+4 =" after calculation
expr_label = tk.Label(display_frame, textvariable=expr_var,
                      font=("Helvetica Neue", 13), fg="#555555", bg=BG_DISPLAY,
                      anchor="e", justify="right")
expr_label.place(relx=1.0, y=4, anchor="ne", x=-36)

# Big bottom Entry: the main input — shows cursor, user types here
result_entry = tk.Entry(display_frame, textvariable=result_var,
                        font=("Helvetica Neue", 30, "bold"), fg="#f0f0f0",
                        bg=BG_DISPLAY, insertbackground="white",
                        bd=0, highlightthickness=0,
                        justify="right", takefocus=True,
                        insertwidth=2)
result_entry.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-4, width=320)

# Alias so the rest of the code still works via expr_entry
expr_entry = result_entry

def _resize_result(text):
    l = len(str(text))
    if l <= 9:    result_entry.config(font=("Helvetica Neue", 30, "bold"))
    elif l <= 13: result_entry.config(font=("Helvetica Neue", 20, "bold"))
    elif l <= 18: result_entry.config(font=("Helvetica Neue", 14, "bold"))
    else:         result_entry.config(font=("Helvetica Neue", 11, "bold"))

def _set_error_look():
    display_frame.config(bg=BG_ERROR)
    result_entry.config(bg=BG_ERROR, fg="#cc3333")
    expr_label.config(bg=BG_ERROR)
    del_lbl.config(bg=BG_ERROR)

def _clear_error_look():
    display_frame.config(bg=BG_DISPLAY)
    result_entry.config(bg=BG_DISPLAY, fg="#f0f0f0")
    expr_label.config(bg=BG_DISPLAY)
    del_lbl.config(bg=BG_DISPLAY)

def update_display(expr="", result="", is_error=False, cursor_pos=None):
    # Remember cursor position before overwriting text
    try:
        saved_cursor = cursor_pos if cursor_pos is not None else result_entry.index(tk.INSERT)
    except Exception:
        saved_cursor = None

    expr_var.set(expr)
    _resize_result(result)
    result_var.set(result)
    if is_error:
        _set_error_look()
    else:
        _clear_error_look()

    # Restore cursor to saved position (clamped to text length)
    try:
        if saved_cursor is not None:
            text_len = len(result_entry.get())
            clamped = max(0, min(saved_cursor, text_len))
            result_entry.icursor(clamped)
        else:
            result_entry.icursor(tk.END)
    except Exception:
        pass
    result_entry.focus_set()

def delete():
    global field_text, field_eval, error_state
    if error_state:
        _reset_error()
        return
    if not field_text:
        return
    
    # Get cursor position
    new_cursor = None
    try:
        cursor_pos = expr_entry.index(tk.INSERT)
        if cursor_pos is None or cursor_pos == 0:
            return
        
        # Handle multi-character operators that need special cleanup
        # " mod " in display = "%" in eval (but with spaces: " % ")
        if field_text.endswith(" mod "):
            field_text = field_text[:-5]  # Remove " mod " (5 chars)
            field_eval = field_eval[:-3]  # Remove " % " (3 chars)
            update_display("", field_text if field_text else "", cursor_pos=len(field_text))
            return
        
        # Delete at cursor position (character before cursor)
        if cursor_pos > 0 and cursor_pos <= len(field_text):
            field_text = field_text[:cursor_pos-1] + field_text[cursor_pos:]
            field_eval = field_eval[:cursor_pos-1] + field_eval[cursor_pos:]
            new_cursor = cursor_pos - 1
    except Exception:
        # Fallback: delete from end
        field_text = field_text[:-1]
        new_cursor = len(field_text)
    
    # Handle implicit multiplication cleanup: "6(" -> eval "6*("
    while field_eval and field_eval[-1] == "*" and (not field_text or field_text[-1] != "*"):
        field_eval = field_eval[:-1]
    # Also clean up if field_eval is longer than field_text
    while field_eval and len(field_eval) > len(field_text):
        field_eval = field_eval[:-1]
    update_display("", field_text if field_text else "", cursor_pos=new_cursor)

del_lbl = tk.Label(display_frame, text="⌫", font=("Helvetica Neue", 17),
                   fg="#444444", bg=BG_DISPLAY, cursor="hand2")
del_lbl.place(relx=1.0, y=6, anchor="ne", x=-6)
del_lbl.bind("<Button-1>", lambda e: delete())

tk.Frame(shell, bg="#2a2a2a", height=2).pack(fill="x")

# ══════════════════════════════════════════════════════════════════════════════
# LOGIC
# ══════════════════════════════════════════════════════════════════════════════
def _reset_error():
    global field_text, field_eval, error_state, calculated
    field_text = ""; field_eval = ""; error_state = False; calculated = False
    update_display("", "")

def _clean_eval_expr(expr):
    """
    Normalise and validate an expression string for eval().
    Works on field_eval (which may still contain unicode operator chars
    if they leaked in through toggle_sign or other paths).
    """
    # ── 1. Normalise unicode / display chars to ASCII Python operators ─────────
    expr = expr.replace("\u2212", "-")   # − (unicode minus) → -
    expr = expr.replace("×", "*")
    expr = expr.replace("÷", "/")
    expr = expr.replace(" mod ", "%")
    expr = expr.replace("^", "**")

    # ── 2. Reject empty parens ────────────────────────────────────────────────
    if re.search(r'\(\s*\)', expr):
        raise ValueError("empty parentheses")

    # ── 3. Reject trailing binary operator  e.g. "6*"  "6/"  "6+"
    #       but ALLOW trailing minus/plus chains because they are unary:
    #       "6-" is invalid but "6---" would resolve when more is typed;
    #       at = time we only reject if last non-space char is * or /
    #       or a + that follows a digit/closing paren (i.e. binary +).
    stripped = expr.rstrip()
    if stripped and stripped[-1] in "*/":
        raise ValueError("trailing operator")
    # trailing + is binary only when something numeric precedes it
    if stripped and stripped[-1] == "+" and re.search(r'[\d)]\+$', stripped):
        raise ValueError("trailing binary +")

    # ── 4. Balance parentheses ────────────────────────────────────────────────
    o = expr.count("("); c = expr.count(")")
    if o > c:   expr += ")" * (o - c)
    elif c > o: expr = "(" * (c - o) + expr

    return expr

def _safe_eval(expr_str):
    expr_str = _clean_eval_expr(expr_str)
    safe = {
        "__builtins__": {},
        "abs": abs, "round": round,
        "sqrt": math.sqrt,
        "sin":  math.sin,  "cos":  math.cos,  "tan":  math.tan,
        "log":  math.log,  "log10": math.log10,
        "pi":   math.pi,   "e":    math.e,
    }
    result = eval(expr_str, safe)
    if isinstance(result, tuple):          # e.g. "()" produced a tuple
        raise ValueError("invalid expression")
    return result

def _fmt(v):
    if v == 0 or (isinstance(v, float) and v == 0.0):
        return "0"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    # Round to 10 sig figs and strip trailing zeros
    return str(round(v, 10)).rstrip("0").rstrip(".")

def add_to_field(display_char, eval_char=None):
    global field_text, field_eval, calculated, error_state
    if eval_char is None:
        eval_char = display_char
    display_char = str(display_char)
    eval_char    = str(eval_char)

    if error_state:
        _reset_error()
        if display_char not in "0123456789.(":
            return   # don't start with an operator after error

    if calculated:
        if display_char in "0123456789":
            field_text = display_char
            field_eval = eval_char
            update_display("", field_text, cursor_pos=len(field_text))
            calculated = False
            return
        elif display_char == ".":
            # Start new decimal number
            field_text = "0."
            field_eval = "0."
            update_display("", field_text, cursor_pos=len(field_text))
            calculated = False
            return
        elif display_char in "+−-×÷*/^" or display_char == " mod ":
            # continue from result with an operator
            field_text += display_char
            field_eval += eval_char
            update_display("", field_text, cursor_pos=len(field_text))
            calculated = False
            return

    # Get cursor position for insertion
    new_cursor = None
    try:
        cursor_pos = expr_entry.index(tk.INSERT)
        current_display = expr_entry.get()
        
        # If cursor is at end, append
        if cursor_pos is None or cursor_pos >= len(current_display):
            field_text += display_char
            field_eval += eval_char
            new_cursor = len(field_text)
        else:
            # Insert at cursor position in display text
            field_text = field_text[:cursor_pos] + display_char + field_text[cursor_pos:]
            field_eval = field_eval[:cursor_pos] + eval_char + field_eval[cursor_pos:]
            new_cursor = cursor_pos + len(display_char)
    except Exception:
        # Fallback to appending
        field_text += display_char
        field_eval += eval_char
        new_cursor = len(field_text)
    
    update_display("", field_text, cursor_pos=new_cursor)

def calculate():
    global field_text, field_eval, calculated, error_state
    if not field_eval:
        return
    try:
        result = _safe_eval(field_eval)
        result_str = _fmt(result)
        update_display(field_text + " =", result_str, is_error=False, cursor_pos=len(result_str))
        cur.execute(
            "INSERT INTO history (expression, result, timestamp) VALUES (?,?,?)",
            (field_text, result_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        refresh_history()
        field_text = result_str
        field_eval = result_str
        calculated  = True
        error_state = False
    except Exception:
        update_display(field_text, "Error", is_error=True)
        error_state = True
        field_text  = ""
        field_eval  = ""
        calculated  = False

def clear():
    global field_text, field_eval, calculated, error_state
    field_text = ""; field_eval = ""; calculated = False; error_state = False
    update_display("", "")

def brackets():
    global field_text, field_eval, error_state
    if error_state:
        _reset_error(); return
    open_ct  = field_text.count("(")
    close_ct = field_text.count(")")
    if not field_text:
        field_text += "("; field_eval += "("
        update_display("", field_text); return
    last = field_text[-1]
    if open_ct > close_ct and (last.isdigit() or last == ")"):
        field_text += ")"; field_eval += ")"
    elif last.isdigit() or last == ")":
        # implicit multiply: show "6(" → eval "6*("
        field_text += "("; field_eval += "*("
    else:
        field_text += "("; field_eval += "("
    update_display("", field_text)

def toggle_sign():
    global field_text, field_eval, error_state
    if error_state:
        _reset_error(); return
    if not field_text or field_text == "0":
        return
    # Find the last number in the expression to toggle its sign
    # Look for the last operator position
    ops = [i for i, c in enumerate(field_eval) if c in "+−-*/^" and i > 0]
    if ops:
        last_op_idx = ops[-1]
        # Toggle sign after the last operator
        num_part_eval = field_eval[last_op_idx+1:]
        num_part_text = field_text[last_op_idx+1:]
        if num_part_eval.startswith("-"):
            # Remove the minus
            field_eval = field_eval[:last_op_idx+1] + num_part_eval[1:]
            field_text = field_text[:last_op_idx+1] + num_part_text[1:]
        elif num_part_eval.startswith("\u2212"):
            field_eval = field_eval[:last_op_idx+1] + num_part_eval[1:]
            field_text = field_text[:last_op_idx+1] + num_part_text[1:]
        else:
            # Add the minus
            field_eval = field_eval[:last_op_idx+1] + "-" + num_part_eval
            field_text = field_text[:last_op_idx+1] + "−" + num_part_text
    else:
        # No operator, toggle the whole expression
        if field_text.startswith("-"):
            field_text = field_text[1:]
            field_eval = field_eval[1:]
        else:
            field_text = "-" + field_text
            field_eval = "-" + field_eval
    update_display("", field_text)

def percent():
    global field_text, field_eval, error_state
    if error_state:
        _reset_error(); return
    if not field_eval:
        return
    try:
        # Find the last top-level binary operator (include unicode minus)
        ops = [i for i, c in enumerate(field_eval) if c in "+−-*/" and i > 0]
        if ops:
            split      = ops[-1]
            left_expr  = field_eval[:split]
            right_expr = field_eval[split + 1:]
            op         = field_eval[split]
            left_val   = _safe_eval(left_expr)
            right_val  = _safe_eval(right_expr)
            pct_val    = left_val * right_val / 100
            pct_str    = _fmt(pct_val)
            left_disp  = field_text[:split]
            field_eval = left_expr + op + pct_str
            field_text = left_disp + op + pct_str
        else:
            val        = _safe_eval(field_eval) / 100
            field_text = _fmt(val)
            field_eval = field_text
        update_display("", field_text)
    except Exception:
        pass

def power():
    if error_state: _reset_error(); return
    add_to_field("^", "**")

def mod():
    if error_state: _reset_error(); return
    add_to_field(" mod ", "%")

def sqrt_fn():
    global field_text, field_eval, calculated, error_state
    if error_state: _reset_error(); return
    if not field_eval: return
    try:
        val        = _safe_eval(field_eval)
        result     = math.sqrt(val)
        result_str = _fmt(result)
        expr_shown = f"√({field_text})"
        update_display(expr_shown + " =", result_str, is_error=False)
        cur.execute(
            "INSERT INTO history (expression, result, timestamp) VALUES (?,?,?)",
            (expr_shown, result_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        refresh_history()
        field_text  = result_str
        field_eval  = result_str
        calculated  = True
        error_state = False
    except Exception:
        update_display(field_text, "Error", is_error=True)
        error_state = True
        field_text  = ""
        field_eval  = ""

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — BUTTON GRID
# ══════════════════════════════════════════════════════════════════════════════
btn_frame = tk.Frame(shell, bg=BG_SHELL)
btn_frame.pack(fill="both", expand=True, padx=3, pady=(3, 6))

for col in range(4):
    btn_frame.columnconfigure(col, weight=1)
for row in range(6):
    btn_frame.rowconfigure(row, weight=1)

def make_button(parent, text, cmd, row, col, style=GRAY, colspan=1):
    fg, bg, bg_press, top = style
    outer = tk.Frame(parent, bg="#111111", bd=0)
    outer.grid(row=row, column=col, columnspan=colspan,
               padx=2, pady=2, sticky="nsew")
    tk.Frame(outer, bg=top, height=1).pack(fill="x", side="top")
    if len(text) == 1:   fs = 17
    elif len(text) == 2: fs = 14
    elif len(text) == 3: fs = 12
    else:                fs = 10
    btn = tk.Label(outer, text=text, font=("Helvetica Neue", fs, "bold"),
                   fg=fg, bg=bg, cursor="hand2", relief="flat", bd=0, anchor="center")
    btn.pack(fill="both", expand=True)

    def on_enter(e):   btn.config(bg=bg_press)
    def on_leave(e):   btn.config(bg=bg)
    def on_press(e):   btn.config(bg=bg_press); cmd()
    def on_release(e): btn.config(bg=bg)

    btn.bind("<Enter>",    on_enter)
    btn.bind("<Leave>",    on_leave)
    btn.bind("<Button-1>", on_press)
    btn.bind("<ButtonRelease-1>", on_release)

# Row 0
make_button(btn_frame, "AC",  clear,                                  0, 0, FUNC)
make_button(btn_frame, "+/-", toggle_sign,                            0, 1, FUNC)
make_button(btn_frame, "()",  brackets,                               0, 2, FUNC)
make_button(btn_frame, "÷",   lambda: add_to_field("÷", "/"),         0, 3, ORANGE)

# Row 1
make_button(btn_frame, "7",   lambda: add_to_field("7"),              1, 0, GRAY)
make_button(btn_frame, "8",   lambda: add_to_field("8"),              1, 1, GRAY)
make_button(btn_frame, "9",   lambda: add_to_field("9"),              1, 2, GRAY)
make_button(btn_frame, "×",   lambda: add_to_field("×", "*"),         1, 3, ORANGE)

# Row 2
make_button(btn_frame, "4",   lambda: add_to_field("4"),              2, 0, GRAY)
make_button(btn_frame, "5",   lambda: add_to_field("5"),              2, 1, GRAY)
make_button(btn_frame, "6",   lambda: add_to_field("6"),              2, 2, GRAY)
make_button(btn_frame, "−",   lambda: add_to_field("−", "-"),         2, 3, ORANGE)

# Row 3
make_button(btn_frame, "1",   lambda: add_to_field("1"),              3, 0, GRAY)
make_button(btn_frame, "2",   lambda: add_to_field("2"),              3, 1, GRAY)
make_button(btn_frame, "3",   lambda: add_to_field("3"),              3, 2, GRAY)
make_button(btn_frame, "+",   lambda: add_to_field("+"),              3, 3, ORANGE)

# Row 4
make_button(btn_frame, "0",   lambda: add_to_field("0"),              4, 0, GRAY, colspan=2)
make_button(btn_frame, ".",   lambda: add_to_field("."),              4, 2, GRAY)
make_button(btn_frame, "=",   calculate,                              4, 3, ORANGE)

# Row 5
make_button(btn_frame, "%",   percent,                                5, 0, SPECIAL)
make_button(btn_frame, "nⁿ",  power,                                  5, 1, SPECIAL)
make_button(btn_frame, "mod", mod,                                    5, 2, SPECIAL)
make_button(btn_frame, "√",   sqrt_fn,                                5, 3, SPECIAL)

# ── Keyboard bindings ─────────────────────────────────────────────────────────
def copy_result(event=None):
    """Copy the current result/display value to clipboard."""
    val = result_var.get()
    if val and (val != "0" or field_text):
        window.clipboard_clear()
        window.clipboard_append(val if not field_text else field_text)
        window.update()

def paste_value(event=None):
    """Paste clipboard content into the field (digits and operators only)."""
    global error_state
    try:
        text = window.clipboard_get().strip()
    except Exception:
        return
    # Normalise pasted text — accept digits, operators, dot, parens
    # Handle both ASCII hyphen and unicode minus
    text = text.replace("\u2212", "-")
    allowed = re.sub(r'[^\d+\-*/^().%]', '', text)
    if not allowed:
        return
    if error_state:
        _reset_error()
    for ch in allowed:
        if ch.isdigit() or ch == ".":   add_to_field(ch)
        elif ch == "+":                 add_to_field("+")
        elif ch == "-":                  add_to_field("−", "-")
        elif ch == "*":                  add_to_field("×", "*")
        elif ch == "/":                  add_to_field("÷", "/")
        elif ch in ("(", ")"):          add_to_field(ch)
        elif ch == "%":                  percent()  # Use percent function, not modulo
        elif ch == "^":                  add_to_field("^", "**")

def on_key(event):
    k  = event.keysym
    ch = event.char
    
    # Let arrow keys, Home, End pass through to Entry for cursor movement
    if k in ("Left", "Right", "Home", "End"):
        expr_entry.focus_set()
        return  # Let the Entry handle these natively
    
    # Ctrl shortcuts
    if event.state & 0x4:   # Control key held
        if k.lower() == "c": copy_result(); return
        if k.lower() == "v": paste_value(); return
        if k.lower() == "a":
            expr_entry.selection_range(0, tk.END)
            return
    if ch.isdigit() or ch == ".": add_to_field(ch)
    elif ch == "+": add_to_field("+")
    elif ch == "-": add_to_field("−", "-")
    elif ch == "*": add_to_field("×", "*")
    elif ch == "/": add_to_field("÷", "/")
    elif ch == "%":  percent()  # Use percent, not modulo
    elif ch == "^": power()
    elif ch in ("(", ")"): add_to_field(ch)
    elif k in ("Return", "equal"): calculate()
    elif k == "BackSpace": delete()
    elif k == "Escape":    clear()

# Make Entry focusable and show cursor always
def on_entry_click(event):
    expr_entry.focus_set()

expr_entry.bind("<Button-1>", on_entry_click)
expr_entry.bind("<Button-3>", on_entry_click)  # Right click

# Route Entry keypresses through our logic to prevent direct editing conflicts
def on_entry_key(event):
    k  = event.keysym
    ch = event.char
    # Allow arrow keys, Home, End to move cursor natively
    if k in ("Left", "Right", "Home", "End"):
        return  # let Entry handle it
    # Block all other default Entry behaviour — route through our handlers
    if event.state & 0x4:  # Ctrl held
        if k.lower() == "c": copy_result(); return "break"
        if k.lower() == "v": paste_value(); return "break"
        if k.lower() == "a":
            expr_entry.selection_range(0, tk.END)
            return "break"
        return "break"
    if ch.isdigit() or ch == ".": add_to_field(ch); return "break"
    elif ch == "+": add_to_field("+"); return "break"
    elif ch == "-": add_to_field("−", "-"); return "break"
    elif ch == "*": add_to_field("×", "*"); return "break"
    elif ch == "/": add_to_field("÷", "/"); return "break"
    elif ch == "%": percent(); return "break"
    elif ch == "^": power(); return "break"
    elif ch in ("(", ")"): add_to_field(ch); return "break"
    elif k in ("Return", "equal"): calculate(); return "break"
    elif k == "BackSpace": delete(); return "break"
    elif k == "Escape": clear(); return "break"
    return "break"  # block anything else

expr_entry.bind("<Key>", on_entry_key)

# Also focus Entry when clicking anywhere in display frame
def on_display_click(event):
    expr_entry.focus_set()

display_frame.bind("<Button-1>", on_display_click)

# Ensure cursor is visible when starting
def show_cursor():
    result_entry.icursor(tk.END)
    result_entry.focus_set()

# Call after window is created
window.after(100, show_cursor)

window.bind("<Key>", on_key)
window.bind("<Control-c>", copy_result)
window.bind("<Control-v>", paste_value)
expr_entry.focus_set()  # Focus Entry to show cursor
window.mainloop()
