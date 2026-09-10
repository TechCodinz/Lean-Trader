"""Adapter between the API's signal-publishing call and ``signals_publisher``.

``leantrader.api.app`` has always imported ``publish_signal`` from here, but the
module was never present in this tree: the implementation lives in the
repository-root ``signals_publisher`` module, which takes a single signal dict,
while the API calls with keyword arguments and expects a boolean.

This module bridges the two. ``signals_publisher`` is imported lazily so that
importing the API package does not depend on the repository root being on
``sys.path``; when it cannot be reached, publishing degrades to ``False``
rather than raising, which is the outcome the API already handles.
"""

from typing import Any, Dict, List, Optional


def _publisher():
    """Return ``signals_publisher.publish_signal``, or ``None`` if unavailable."""
    try:
        from signals_publisher import publish_signal as _impl
    except Exception:
        return None
    return _impl


def build_signal(
    *,
    symbol: str,
    side: str,
    confidence: float,
    rationale: Optional[List[str]] = None,
    chart_path: str = "",
    signal_id: str = "",
    chat_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Map the API's keyword form onto the dict ``signals_publisher`` expects.

    ``rationale`` becomes ``context``, which is the first key the publisher
    checks when rendering the reasoning bullets. Remaining keys are carried
    through untouched; the publisher defaults anything it does not receive.
    """
    try:
        score = float(confidence)
    except (TypeError, ValueError):
        score = 0.0

    signal: Dict[str, Any] = {
        "symbol": str(symbol or ""),
        "side": str(side or ""),
        "confidence": score,
        "context": list(rationale or []),
    }

    if chart_path:
        signal["chart_path"] = str(chart_path)
    if signal_id:
        signal["signal_id"] = str(signal_id)
    if chat_id:
        signal["chat_id"] = str(chat_id)

    return signal


def publish_signal(
    *,
    symbol: str,
    side: str,
    confidence: float,
    rationale: Optional[List[str]] = None,
    chart_path: str = "",
    signal_id: str = "",
    chat_id: Optional[str] = None,
) -> bool:
    """Publish one signal. Returns whether the publisher accepted it.

    A signal the publisher deliberately drops -- below the confidence floor, or
    inside the de-duplication window -- reports ``False`` here, the same as a
    delivery failure. The publisher's own result carries ``skipped_reason`` for
    callers that need to tell those apart.
    """
    impl = _publisher()
    if impl is None:
        return False

    result = impl(
        build_signal(
            symbol=symbol,
            side=side,
            confidence=confidence,
            rationale=rationale,
            chart_path=chart_path,
            signal_id=signal_id,
            chat_id=chat_id,
        )
    )

    if isinstance(result, dict):
        return bool(result.get("ok"))
    return bool(result)
