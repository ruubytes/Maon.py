DEFAULT_SETTINGS: dict[str, str | int | float] = {
    "audio_cache_max_size_mb": 51200,
    "audio_download_rate_bandwidth_limit": "3M",
    "audio_path_music": "./music/",
    "audio_path_sfx": "./sfx/",
    "audio_player_timeout": 5400,
    "audio_sfx_volume": .25,
    "audio_track_caching_duration_max": 4000
}

DEFAULT_CUSTOMIZATION: dict[str, str | list[str]] = {
    "prefix": [ 
        "m ", "M ", "Maon ", "maon ", "mAon ", "maOn ", "maoN ", "MAon ", "mAOn ", "maON ", "MAOn ", "mAON ", "MAON "
    ],
    "color_accent": "0xf8d386",
    "8ball_trigger": [
        "what", "wanna", "how", "may", "has", "have", "will", "should",
        "do", "does", "can", "am", "is", "are", "did", "could", "would",
        "why", "you", "u", "another", "anotha", "anutha", "was", "were"
    ],
    "8ball_reply": [
        "Uhh... I don't know.",
        "Yes.", "Mhm.", "Yah.", "Sure.",
        "No.", "I don't think so.", "Ah... no.", "Eeh... no.",
        "...maybe?", "Probably.", "Not sure."
    ],
    "8ball_reply_why": [
        "Because I can.", 
        "haha maon go beep boop", 
        "I don't know why, because I can't reason. :point_right::point_right:"
    ],
    "8ball_reply_default": [
        "Hm?", "What?", "?", "...?", "Huh?", "Nani?", ":eye::lips::eye:"
    ],
    "status_listening": [
        "Spotify",
        "botcasts"
    ],
    "status_watching": [
        "the server",
        "my console logs",
        "the invisible members"
    ],
    "status_playing": [
        "with fire",
        "with my tail"
    ]
}

CMDS_EMBED_MUSIC_STR: str = """
"""
CMDS_EMBED_MISC_STR: str = """
"""
CMDS_EMBED_MOD_STR: str = """
"""
CMDS_EMBED_ADMIN_STR: str = f""":flag_kp: ***Admin Commands:***
"""
