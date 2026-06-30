#!/usr/bin/env python3
import json
import re
import sys

BANNED = [
    re.compile(r'[ᄀ-ᇿ㄰-㆏가-힯]'),  # Korean
    re.compile(r'[぀-ゟ゠-ヿ]'),               # Japanese kana
    re.compile(r'[Ѐ-ӿ]'),                             # Cyrillic
]

FENCE = re.compile(r'```[\s\S]*?```', re.MULTILINE)
INLINE_CODE = re.compile(r'`[^`\n]+`')


def strip_code(text: str) -> str:
    text = FENCE.sub('', text)
    text = INLINE_CODE.sub('', text)
    return text


def has_banned_script(text: str) -> bool:
    return any(p.search(text) for p in BANNED)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get('stop_hook_active', False):
        sys.exit(0)

    message = payload.get('last_assistant_message', '') or ''
    natural = strip_code(message)

    if not has_banned_script(natural):
        sys.exit(0)

    print(json.dumps({
        'continue': True,
        'stop_hook_active': True,
        'decision': 'block',
        'reason': 'Detected banned script outside code blocks.',
        'hookSpecificOutput': {
            'hookEventName': 'Stop',
            'additionalContext': (
                '你的上一条回复在非代码内容中包含不允许的文字脚本。'
                '请完整重写上一条回复。'
                '只允许使用简体中文、英文、数字、常见标点。'
                '代码、命令、路径、报错原文可保留原样。'
                '不要使用韩文、日文假名或西里尔字母。'
            ),
        },
    }))


if __name__ == '__main__':
    main()
