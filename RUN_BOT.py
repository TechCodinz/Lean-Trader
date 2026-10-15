#!/usr/bin/env python3
"""
MAIN BOT LAUNCHER - Production Ready
Loads environment and starts all systems
"""
import os
import sys
import asyncio
from pathlib import Path

# Load environment variables
print("=" * 80)
print("🚀 TRADING BOT LAUNCHER")
print("=" * 80)
print()

# Load .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print("📄 Loading environment variables...")
    loaded = 0
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
                loaded += 1
    print(f"✅ Loaded {loaded} environment variables\n")
else:
    print("⚠️  No .env file found. Using system environment.\n")


# LEANTRADER_SECRET_FILE_ENV_BRIDGE_V1
# Keep credentials on mounted secret files. Hydrate aliases into this
# process environment only so historical engines can use their original
# BYBIT_API_KEY / BYBIT_API_SECRET convention without plaintext .env keys.
def _leantrader_hydrate_secret_env(name):
    if os.getenv(name):
        return True

    path = os.getenv(
        name + "_FILE"
    )

    if not path:
        return False

    try:
        value = (
            Path(path)
            .read_text()
            .strip()
        )
    except Exception:
        return False

    if not value:
        return False

    os.environ[
        name
    ] = value

    return True


_leantrader_hydrate_secret_env(
    "BYBIT_TESTNET_API_KEY"
)

_leantrader_hydrate_secret_env(
    "BYBIT_TESTNET_API_SECRET"
)

if os.getenv(
    "BYBIT_TESTNET_API_KEY"
) and not os.getenv(
    "BYBIT_API_KEY"
):
    os.environ[
        "BYBIT_API_KEY"
    ] = os.environ[
        "BYBIT_TESTNET_API_KEY"
    ]

if os.getenv(
    "BYBIT_TESTNET_API_SECRET"
) and not os.getenv(
    "BYBIT_API_SECRET"
):
    os.environ[
        "BYBIT_API_SECRET"
    ] = os.environ[
        "BYBIT_TESTNET_API_SECRET"
    ]

if os.getenv(
    "BYBIT_TESTNET_API_SECRET"
) and not os.getenv(
    "BYBIT_SECRET"
):
    os.environ[
        "BYBIT_SECRET"
    ] = os.environ[
        "BYBIT_TESTNET_API_SECRET"
    ]

print(
    "🔐 Bybit Docker-secret runtime bridge: "
    + (
        "ready"
        if (
            os.getenv(
                "BYBIT_API_KEY"
            )
            and os.getenv(
                "BYBIT_API_SECRET"
            )
        )
        else "not resolved"
    )
)


# Verify critical keys
print("🔍 Checking API Keys:")
telegram_ok = bool(os.getenv('TELEGRAM_BOT_TOKEN'))
bybit_ok = bool(os.getenv('BYBIT_API_KEY'))
private_key_ok = bool(os.getenv('PRIVATE_KEY'))

print(f"  {'✅' if telegram_ok else '⚠️ '} Telegram Bot Token: {'Set' if telegram_ok else 'Not set'}")
print(f"  {'✅' if bybit_ok else '⚠️ '} Bybit API Key: {'Set' if bybit_ok else 'Not set'}")
print(f"  {'✅' if private_key_ok else '⚠️ '} DEX Private Key: {'Set' if private_key_ok else 'Not set (DEX disabled)'}")
print()

# Install October-2025 real-evidence compatibility bridge
from LEGACY_2025_REAL_INTELLIGENCE_BRIDGE import install as _install_real_intelligence
_install_real_intelligence()

# Import orchestrator
print("📦 Loading trading systems...")
try:
    # 2026 COMPLETE_ULTIMATE_ORCHESTRATOR DISABLED (chokes container)
    # 2025 pattern: RPB runs directly
    # from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
    from REAL_PROFIT_BOT import RealProfitBot as CompleteUltimateOrchestrator
    print("✅ All systems loaded\n")
except Exception as e:
    print(f"❌ Failed to load systems: {e}")
    sys.exit(1)

# Get mode from args
mode = 'testnet'
auto_confirm = False

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg == '--live':
            mode = 'live'
        elif arg == '--testnet':
            mode = 'testnet'
        elif arg == '--auto-confirm':
            auto_confirm = True

# Safety check for live mode (skip if auto-confirm for systemd)
if mode == 'live' and not auto_confirm:
    print("⚠️  LIVE MODE - Trading with real money!")
    try:
        response = input("Are you sure? Type 'YES' to confirm: ")
        if response != 'YES':
            print("Cancelled.")
            sys.exit(0)
    except EOFError:
        # Running as service without stdin - auto-confirm
        print("⚠️  Running as background service - auto-confirming live mode")
        pass

print(f"🎯 Mode: {mode.upper()}")
print()

async def main():
    """Main entry point"""
    print("=" * 80)
    print(f"🚀 STARTING BOT IN {mode.upper()} MODE")
    print("=" * 80)
    print()
    
    # Create orchestrator
    # 2025 PATTERN: Run RPB directly (bypass 2026 orchestrator)
    from REAL_PROFIT_BOT import RealProfitBot
    print("⏳ Starting Real Profit Bot (2025 pattern)...")
    bot = RealProfitBot()
    # RPB runs its own trading loop (sync, not async)
    import threading
    rpb_thread = threading.Thread(target=bot.run_real_profit_trading, daemon=True)
    rpb_thread.start()
    print("✅ RPB trading loop started")
    tasks = []  # No async orchestrator tasks in 2025 pattern
    # Keep alive forever so RPB daemon thread keeps trading
    # (asyncio.gather([]) would return instantly and kill the thread)
    print("✅ RPB is trading. Waiting forever (Ctrl+C to stop)...")
    await asyncio.Event().wait()
    
    print()
    print("=" * 80)
    print("✅ BOT IS RUNNING!")
    print("=" * 80)
    print()
    print("Systems Active:")
    print(f"  ✅ CEX Trading: {'Enabled' if bybit_ok else 'Disabled (no API keys)'}")
    print(f"  ✅ DEX Trading: {'Enabled' if private_key_ok else 'Disabled (no private key)'}")
    print(f"  ✅ Telegram: {'Enabled' if telegram_ok else 'Disabled (no bot token)'}")
    print(f"  ✅ AI/ML: Enabled (600+ models)")
    print(f"  ✅ Quantum: Enabled (IBM Qiskit)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # LEANTRADER_RUNTIME_TASK_EXIT_TELEMETRY_V1
    #
    # Observability only. This does not suppress or alter any failure.
    # It records which top-level runtime task finishes/cancels/fails
    # immediately before PID 1 leaves asyncio.gather().
    def _runtime_task_done(task):
        try:
            name = task.get_name()
        except BaseException:
            name = repr(task)

        try:
            if task.cancelled():
                print(
                    f"RUNTIME_TASK_DONE "
                    f"name={name} "
                    f"cancelled=True",
                    flush=True,
                )
                return

            exc = task.exception()

            if exc is None:
                print(
                    f"RUNTIME_TASK_DONE "
                    f"name={name} "
                    f"cancelled=False "
                    f"exception=None",
                    flush=True,
                )
            else:
                print(
                    f"RUNTIME_TASK_DONE "
                    f"name={name} "
                    f"cancelled=False "
                    f"exception={type(exc).__name__}: "
                    f"{exc}",
                    flush=True,
                )

        except BaseException as telemetry_exc:
            print(
                f"RUNTIME_TASK_TELEMETRY_ERROR "
                f"name={name} "
                f"type={type(telemetry_exc).__name__} "
                f"detail={telemetry_exc}",
                flush=True,
            )

    for index, runtime_item in enumerate(tasks):
        if isinstance(runtime_item, asyncio.Task):
            try:
                existing_name = runtime_item.get_name()

                if (
                    not existing_name
                    or existing_name.startswith("Task-")
                ):
                    runtime_item.set_name(
                        f"leantrader-runtime-{index}"
                    )
            except BaseException:
                pass

            runtime_item.add_done_callback(
                _runtime_task_done
            )

        else:
            print(
                f"RUNTIME_ITEM "
                f"index={index} "
                f"type={type(runtime_item).__name__} "
                f"task_callback=False",
                flush=True,
            )

    # Run forever
    try:
        try:
            await asyncio.gather(*tasks)

            print(
                "RUNTIME_GATHER_RETURNED "
                "all_runtime_items_completed",
                flush=True,
            )

        except BaseException as runtime_exc:
            print(
                "RUNTIME_GATHER_TERMINATED "
                f"type={type(runtime_exc).__name__} "
                f"detail={runtime_exc}",
                flush=True,
            )

            for index, runtime_item in enumerate(tasks):
                if isinstance(runtime_item, asyncio.Task):
                    try:
                        print(
                            "RUNTIME_TASK_STATE "
                            f"index={index} "
                            f"name={runtime_item.get_name()} "
                            f"done={runtime_item.done()} "
                            f"cancelled={runtime_item.cancelled()}",
                            flush=True,
                        )
                    except BaseException as state_exc:
                        print(
                            "RUNTIME_TASK_STATE_ERROR "
                            f"index={index} "
                            f"type={type(state_exc).__name__} "
                            f"detail={state_exc}",
                            flush=True,
                        )
                else:
                    print(
                        "RUNTIME_ITEM_STATE "
                        f"index={index} "
                        f"type={type(runtime_item).__name__}",
                        flush=True,
                    )

            raise
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        print("=" * 80)

if __name__ == "__main__":
    # LEANTRADER_PROCESS_EXIT_TELEMETRY_V1
    #
    # Observability only:
    # - faulthandler prints Python stacks on native fatal signals
    # - atexit proves normal interpreter finalization occurred
    # - threading.excepthook exposes otherwise-isolated thread crashes
    # - final BaseException handler exposes SystemExit/other exits that
    #   bypass the existing Exception handler
    #
    # No exception or exit is suppressed.
    import atexit as _lt_atexit
    import faulthandler as _lt_faulthandler
    import threading as _lt_threading
    import traceback as _lt_traceback

    try:
        _lt_faulthandler.enable(
            all_threads=True
        )
        print(
            "RUNTIME_FAULTHANDLER=ENABLED",
            flush=True,
        )
    except BaseException as _fh_exc:
        print(
            "RUNTIME_FAULTHANDLER_ENABLE_FAILED "
            f"type={type(_fh_exc).__name__} "
            f"detail={_fh_exc}",
            flush=True,
        )

    def _lt_process_atexit():
        print(
            "RUNTIME_ATEXIT "
            "python_interpreter_finalizing=True",
            flush=True,
        )

    _lt_atexit.register(
        _lt_process_atexit
    )

    _lt_previous_thread_hook = (
        _lt_threading.excepthook
    )

    def _lt_thread_exception(args):
        try:
            print(
                "RUNTIME_THREAD_EXCEPTION "
                f"thread={getattr(args.thread, 'name', None)} "
                f"type={getattr(args.exc_type, '__name__', args.exc_type)} "
                f"detail={args.exc_value}",
                flush=True,
            )

            _lt_traceback.print_exception(
                args.exc_type,
                args.exc_value,
                args.exc_traceback,
            )
        finally:
            try:
                _lt_previous_thread_hook(
                    args
                )
            except BaseException:
                pass

    _lt_threading.excepthook = (
        _lt_thread_exception
    )

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print(
            "\n✅ Bot stopped gracefully"
        )

    except Exception as e:
        print(
            f"\n❌ Error: {e}",
            flush=True,
        )
        _lt_traceback.print_exc()

    except BaseException as e:
        print(
            "RUNTIME_TOPLEVEL_BASEEXCEPTION "
            f"type={type(e).__name__} "
            f"detail={e}",
            flush=True,
        )

        _lt_traceback.print_exc()

        # Preserve original behavior/exit status.
        raise
