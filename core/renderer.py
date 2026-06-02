"""
Message rendering — formats agent stream messages to stdout.
"""

import json
from core.pricing import fmt_money


def truncate(text, n=200) -> str:
    text = str(text).replace("\n", " ")
    return text if len(text) <= n else text[:n] + f"...({len(text) - n} more chars)"


def render_message(msg, tracker):
    cls_name = type(msg).__name__

    if cls_name == "SystemMessage":
        data = getattr(msg, "data", {})
        if data.get("subtype") == "init":
            print(f"\nsession started")
            print(f"  session: {data.get('session_id', '?')[:8]}")
            print(f"  model:   {data.get('model', '?')}")
            print(f"  cwd:     {data.get('cwd', '?')}")
        return

    if cls_name == "AssistantMessage":
        tracker.turns += 1
        content = getattr(msg, "content", [])

        for block in content:
            block_type = type(block).__name__

            if block_type == "ThinkingBlock":
                thinking = getattr(block, "thinking", "")
                tracker.thinking_total_chars += len(thinking)
                print(f"\n[thinking] {len(thinking):,} chars")

            elif block_type == "TextBlock":
                text = getattr(block, "text", "")
                print(f"\n[claude]\n{text}")

            elif block_type == "ToolUseBlock":
                tool_name  = getattr(block, "name", "?")
                tool_input = getattr(block, "input", {})

                if tool_name == "Write":
                    path = tool_input.get("file_path", tool_input.get("path", "?"))
                    body = tool_input.get("content", "")
                    lines = body.count("\n") + 1 if body else 0
                    print(f"\n[write] {path}  ({lines} lines)")
                    tracker.files_written.append(path)
                    tracker.tool_calls.append(("Write", path))

                elif tool_name == "Bash":
                    cmd = tool_input.get("command", "?")
                    print(f"\n[bash] {truncate(cmd, 200)}")
                    tracker.bash_commands.append(cmd)
                    tracker.tool_calls.append(("Bash", truncate(cmd, 80)))

                elif tool_name == "Read":
                    path = tool_input.get("file_path", tool_input.get("path", "?"))
                    print(f"\n[read] {path}")
                    tracker.tool_calls.append(("Read", path))

                else:
                    print(f"\n[{tool_name}] {truncate(json.dumps(tool_input), 200)}")
                    tracker.tool_calls.append((tool_name, truncate(json.dumps(tool_input), 80)))

        usage = getattr(msg, "usage", {}) or {}
        if isinstance(usage, dict):
            bd = tracker.record_usage(usage)
            if bd is not None:
                print(f"  turn {tracker.turns}: in={bd['input_tok']:,} out={bd['output_tok']:,} "
                      f"cache(W/R)={bd['cache_write_tok']:,}/{bd['cache_read_tok']:,} "
                      f"cost={fmt_money(bd['total'])}")

        err = getattr(msg, "error", None)
        if err:
            tracker.last_error = err
            print(f"\n[error] {err}")
        return

    if cls_name == "UserMessage":
        for block in getattr(msg, "content", []):
            if type(block).__name__ == "ToolResultBlock":
                is_error       = getattr(block, "is_error", False)
                result_content = getattr(block, "content", "")
                if isinstance(result_content, list):
                    result_text = "\n".join(
                        c["text"] if isinstance(c, dict) and "text" in c else str(c)
                        for c in result_content
                    )
                else:
                    result_text = str(result_content)

                print(f"\n[{'tool error' if is_error else 'tool result'}]")
                lines = result_text.split("\n")
                for line in lines[:15]:
                    print(f"  {line[:200]}")
                if len(lines) > 15:
                    print(f"  ...({len(lines) - 15} more lines)")
                if is_error:
                    tracker.last_error = result_text[:500]
        return

    if cls_name == "ResultMessage":
        is_error    = getattr(msg, "is_error", False)
        duration_ms = getattr(msg, "duration_ms", 0) or 0
        stop_reason = getattr(msg, "stop_reason", "?")
        result_text = getattr(msg, "result", "") or ""
        denials     = getattr(msg, "permission_denials", []) or []

        tracker.sdk_reported_cost = getattr(msg, "total_cost_usd", 0) or 0
        if denials:
            tracker.permission_denials = denials

        print(f"\nsession {'error' if is_error else 'done'} — {stop_reason} ({duration_ms / 1000:.1f}s)")
        if result_text:
            print(f"  result: {truncate(result_text, 300)}")
        return
