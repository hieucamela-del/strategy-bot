from flask import Flask, render_template, jsonify, request, redirect, url_for
import os, json
from datetime import datetime
from app.settings import OUTPUT_DIR, INPUT_FINBOX, INPUT_ZALO, ACCOUNT_FILE, ENTRY_WINDOW_START, ENTRY_WINDOW_END, CLOSE_TIME, CONTRACTS_PER_ORDER
from app.scheduler_app import run_pipeline_once, run_close_positions

app = Flask(__name__, template_folder="templates")

FINBOX_OUT = os.path.join(OUTPUT_DIR, "finbox_signals.json")
ZALO_OUT = os.path.join(OUTPUT_DIR, "zalo_signals.json")
MATCH_OUT = os.path.join(OUTPUT_DIR, "actionable_signals.json")
ORDERS_OUT = os.path.join(OUTPUT_DIR, "orders.json")
POSITIONS_OUT = os.path.join(OUTPUT_DIR, "positions.json")
STATE_FILE = os.path.join(OUTPUT_DIR, "state.json")


def read_json(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else []


@app.route('/')
def index():
    fin = read_json(FINBOX_OUT, [])
    zalo = read_json(ZALO_OUT, [])
    matches = read_json(MATCH_OUT, [])
    orders = read_json(ORDERS_OUT, [])
    positions = read_json(POSITIONS_OUT, [])
    state = read_json(STATE_FILE, {})
    return render_template('index.html', finbox=fin, zalo=zalo, matches=matches, orders=orders, positions=positions, state=state,
                           entry_start=ENTRY_WINDOW_START, entry_end=ENTRY_WINDOW_END, close_time=CLOSE_TIME, contracts=CONTRACTS_PER_ORDER)


@app.route('/orders')
def orders_view():
    orders = read_json(ORDERS_OUT, [])
    return render_template('orders.html', orders=orders)


@app.route('/positions')
def positions_view():
    pos = read_json(POSITIONS_OUT, [])
    return render_template('positions.html', positions=pos)


@app.route('/action/run', methods=['POST'])
def action_run():
    # trigger pipeline manually
    run_pipeline_once()
    return redirect(url_for('index'))


@app.route('/action/close', methods=['POST'])
def action_close():
    run_close_positions()
    return redirect(url_for('index'))


@app.route('/config', methods=['GET','POST'])
def config_view():
    cfg_path = 'config.yaml'
    cfg = {}
    # load config if exists
    try:
        import yaml
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
    except Exception:
        cfg = {}

    if request.method == 'POST':
        # update allowed fields
        cfg['ENTRY_WINDOW_START'] = request.form.get('entry_start')
        cfg['ENTRY_WINDOW_END'] = request.form.get('entry_end')
        cfg['CLOSE_TIME'] = request.form.get('close_time')
        cfg['CONTRACTS_PER_ORDER'] = int(request.form.get('contracts') or 0)
        cfg['ALLOWED_DIRECTIONS'] = [d.strip().upper() for d in request.form.get('allowed','BUY,SELL').split(',')]
        # write back
        with open(cfg_path, 'w', encoding='utf-8') as f:
            yaml.dump(cfg, f, allow_unicode=True)
        return redirect(url_for('index'))

    return render_template('config.html', cfg=cfg)


if __name__ == '__main__':
    # run Flask app
    app.run(host='0.0.0.0', port=8000)
