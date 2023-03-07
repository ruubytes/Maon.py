from __future__ import annotations
import logbook
from discord import Interaction
from discord import Message
from discord.ext.commands import Context
from json import dumps
from logging import Logger
from time import time
from utils import send_response
from yt_dlp.YoutubeDL import YoutubeDL

from yt_dlp import DownloadError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from audio import Audio

log: Logger = logbook.getLogger("track")


class Track():
    def __init__(
            self, 
            title: str, 
            url: str, 
            track_type: str, 
            *, 
            format: tuple[str, str] = ("", ""),
            guild_id: int = 0,
            url_original: str = "",
            video_id: str = ""
        ) -> None:
        self.title: str = title
        self.url: str = url
        self.track_type: str = track_type
        self.format: tuple[str, str] = format
        self.guild_id: int = guild_id
        self.url_original: str = url_original
        self.video_id: str = video_id
        self.time_stamp: float = time()

    
    def __repr__(self) -> str:
        return dumps(self, default=vars, indent=4, ensure_ascii=False)


async def create_local_track(audio: Audio, cim: Context | Interaction | Message, url: str, track_type: str = "music") -> None | Track:
    log.info(f"{cim.guild}: Creating local track from {url}")
    if "/.Cached Tracks/" in url:
        title: str = url[url.rfind("/") + 1 : -16]
    else:
        title: str = url[url.rfind("/") + 1:] if "/" in url else url
        title = title[:title.rfind(".")]
    return Track(title, url, track_type)


async def create_stream_track(audio: Audio, cim: Context | Interaction | Message, url: str) -> None | Track:
    if not cim.guild: return
    log.info(f"{cim.guild}: Creating stream track from {url}")
    if url.startswith(("https://www.youtube.com/", "https://youtu.be/", "https://m.youtube.com/", "https://youtube.com/")):
        id: str | None = await _get_yt_video_id(url)
        if not id: return None
        url_local: str | None = audio.cached_tracks.get(id)
        if url_local:
            log.info(f"Found {id} in my cached tracks.")
            return await create_local_track(audio, cim, url_local, "music")
        
        log.info(f"{id} not found in cached tracks, downloading meta data...")
        url = f"https://www.youtube.com/watch?v={id}"   # Sanitize url

        video_info: dict | None = await _get_yt_video_info(audio, cim, url)
        if not video_info: return None
        protocol: str | None = video_info.get("protocol")
        if not protocol: return None
        log.info(f"Stream track protocol:\n{protocol}")

        if protocol == "m3u8_native":
            log.info(f"Stream track is a live stream.")
            title: str = video_info.get("title")[:-17]   # type: ignore
            url_original: str = url
            url_stream: str = video_info.get("url")      # type: ignore
            return Track(title, url_stream, "live", url_original=url_original)
        else:
            log.info(f"Stream track is a normal stream.")
            format: tuple[str, str] | None = await _get_yt_video_best_audio_format(video_info)
            if not format: 
                await send_response(cim, "I could not find a suitable audio format to stream.")
                return None
            title: str = video_info["title"]
            url_original: str = url
            url_stream: str = format[1]
            track: Track = Track(title, url_stream, "stream", url_original=url_original, format=format, guild_id=cim.guild.id, video_id=id)
            await audio.download_q.put(track)
            return track
    elif url.startswith("https://open.spotify.com/"):
        await send_response(cim, "Spotify not implemented yet.")
        return None
    return None


async def _get_yt_video_id(url: str) -> str | None:
    """Get the 11 chars long video id from a Youtube link."""
    if url.find("?v=") > 0:
        return url[url.find("?v=") + 3 : url.find("?v=") + 14] 
    elif url.find("&v=") > 0:
        return url[url.find("&v=") + 3 : url.find("&v=") + 14]
    elif url.find(".be/") > 0:
        return url[url.find(".be/") + 4 : url.find(".be/") + 15]
    elif url.find("/shorts/") > 0:
        return url[url.find("/shorts/") + 8 : url.find("/shorts/") + 19]
    else:
        return None


async def _get_yt_video_info(audio: Audio, cim: Context | Interaction | Message, url) -> dict | None:
    options: dict[str, str | bool | int | Logger] = {
        "no_warnings": False,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        "logger": logbook.getLogger("yt-dlp"),
        "age_limit": 21
    }
    try:
        video_info: dict | None = await audio.maon.loop.run_in_executor(
            None, lambda: YoutubeDL(options).extract_info(url, download=False)
        )
    except DownloadError as e:
        log.error(f"{cim.guild.name}: {e.__str__()[28:]}")  # type: ignore
        if "looks truncated" in e.__str__():
            await send_response(cim, "The link looks incomplete, paste it again, please.")
        elif "to confirm your age" in e.__str__():
            await send_response(cim, "The video is age gated and I couldn't proxy my way around it.")
        elif "HTTP Error 403" in e.__str__():
            await send_response(cim, "I received a `forbidden` error, I was locked out from downloading the meta data...\nYou could try again in a few seconds, though!")
        elif "Private video." in e.__str__():
            await send_response(cim, "The video has been privated and I can't view it.")
        else:
            await send_response(cim, "I could not download the video's meta data... maybe try again in a few seconds.")
        return None
    return video_info


async def _get_yt_video_best_audio_format(video_info: dict) -> tuple[str, str] | None:
    formats: dict[str, str] = {}
    for f in video_info.get("formats", [video_info]):
        formats[f.get("format_id")] = f.get("url")  # type: ignore

    log.info(f"Found formats: {formats.keys()}")
    if "251" in formats: return ("251", formats["251"])
    elif "140" in formats: return ("140", formats["140"])
    elif "250" in formats: return ("250", formats["250"])
    elif "249" in formats: return ("249", formats["249"])
    else: return None
