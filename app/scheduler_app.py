from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
import json

from app.finbox_agent import FinboxAgent
from app.zalo_agent import ZaloAgent
from app.matcher_agent import MatcherAgent
from app.risk_executor import RiskExecutor
from app.settings import INPUT_FINBOX, INPUT_ZALO, OUTPUT_DIR, ALLOWED_DIRECTIONS, SCORE_THRESHOLD, ENTRY_WINDOW_START, CLOSE_TIME

FINBOX_OUT = os.path.join(OUTPUT_DIR, "finbox_signals.json")
ZALO_OUT = os.path.join(OUTPUT_DIR, "zalo_signals.json")
MATCH_OUT = os.path.join(OUTPUT_DIR, "actionable_signals.json")
ORDERS_OUT = os.path.join(OUTPUT_DIR, "orders.json")
POSITIONS_OUT = os.path.join(OUTPUT_DIR, "positions.json")

sched = BlockingScheduler()


def run_pipeline_once():
    try:
        print(f"[{datetime.now()}] Running pipeline...")
        finbox = FinboxAgent(INPUT_FINBOX, FINBOX_OUT)
        finbox_signals = finbox.run()
        print(f"Finbox signals: {len(finbox_signals)}")

        zalo = ZaloAgent(INPUT_ZALO, ZALO_OUT)
        zalo_signals = zalo.run()
        print(f"Zalo signals: {len(zalo_signals)}")

        matcher = MatcherAgent(FINBOX_OUT, ZALO_OUT, MATCH_OUT, ALLOWED_DIRECTIONS, SCORE_THRESHOLD)
        matches = matcher.run()
        print(f"Actionable signals: {len(matches)}")

        executor = RiskExecutor(MATCH_OUT, "data/account.json", ORDERS_OUT, POSITIONS_OUT)
        orders, positions = executor.execute_matches()
        print(f"Orders executed: {len(orders)}")
    except Exception as e:
        print("Error running pipeline:", e)


def run_close_positions():
    try:
        print(f"[{datetime.now()}] Closing positions...")
        executor = RiskExecutor(MATCH_OUT, "data/account.json", ORDERS_OUT, POSITIONS_OUT)
        closed = executor.close_all_open_positions()
        print(f"Closed {len(closed)} positions")
    except Exception as e:
        print("Error closing positions:", e)


def schedule_jobs():
    # schedule entry job at ENTRY_WINDOW_START daily
    if ENTRY_WINDOW_START:
        try:
            hh, mm = ENTRY_WINDOW_START.split(":")
            trigger = CronTrigger(hour=int(hh), minute=int(mm))
            sched.add_job(run_pipeline_once, trigger, id="entry_job", replace_existing=True)
            print(f"Scheduled entry job at {ENTRY_WINDOW_START}")
        except Exception as e:
            print("Invalid ENTRY_WINDOW_START config:", e)

    # schedule close job at CLOSE_TIME daily
    if CLOSE_TIME:
        try:
            hh, mm = CLOSE_TIME.split(":")
            trigger = CronTrigger(hour=int(hh), minute=int(mm))
            sched.add_job(run_close_positions, trigger, id="close_job", replace_existing=True)
            print(f"Scheduled close job at {CLOSE_TIME}")
        except Exception as e:
            print("Invalid CLOSE_TIME config:", e)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    schedule_jobs()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped")
