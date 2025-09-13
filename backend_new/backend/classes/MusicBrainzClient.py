from typing import Optional, List
from .Recording import Recording
from .RecordingQuery import RecordingQuery
import musicbrainzngs as mb

class MusicBrainzClient:
    def __init__(self):
        mb.set_useragent("MusicChatbot", "0.1", "test@tets.com")
        mb.set_rate_limit(1.0) 

    @staticmethod
    def _artist_credit_to_str(ac_list) -> str:
        parts = []
        for item in ac_list or []:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("name") or item.get("artist", {}).get("name", ""))
        return " ".join(p for p in parts if p).replace("  ", " ").strip()

    @staticmethod
    def _year_from_date(date_str: Optional[str]) -> Optional[int]:
        if not date_str:
            return None
        try:
            return int(date_str[:4])
        except Exception:
            return None

    @staticmethod
    def _to_decade(year: Optional[int]) -> Optional[int]:
        return (year // 10) * 10 if year is not None else None

    @staticmethod
    def _earliest_date_from_releases(rels: Optional[list]) -> Optional[str]:
        if not rels:
            return None
        dates = [r.get("date") for r in rels if r.get("date")]
        return min(dates) if dates else None  # works for YYYY and YYYY-MM-DD


    # --- inside MusicBrainzClient ---
    def search_recordings(
        self,
        query: str | RecordingQuery,
        limit: int = 10,
        enrich_missing_dates: bool = False,
        enrich_genres: bool = False,
    ) -> List[Recording]:
        """
        Dates:
        1) earliest 'date' from 'release-list' (search payload)
        2) else 'first-release-date'
        3) else (if enrich_missing_dates) lookup recording to infer

        Genres (if enrich_genres=True):
        recording -> release-group -> artist (pick highest 'count' item).
        """
        lucene_query = query.to_lucene() if isinstance(query, RecordingQuery) else query
        res = mb.search_recordings(query=lucene_query, limit=limit)

        out: List[Recording] = []
        for r in res.get("recording-list", []):
            first_date = self._earliest_date_from_releases(r.get("release-list")) or r.get("first-release-date")
            year = self._year_from_date(first_date)
            out.append(Recording(
                mbid=r.get("id", ""),
                title=r.get("title", ""),
                artist=self._artist_credit_to_str(r.get("artist-credit")),
                first_release_date=first_date,
                decade=self._to_decade(year),
                duration_ms=int(r["length"]) if "length" in r else None,
                genre=None,  # filled during enrichment
            ))

        if enrich_missing_dates or enrich_genres:
            for rec in out:
                self._enrich_recording_cascade(rec, need_date=enrich_missing_dates, need_genre=enrich_genres)

        return out


    # --- inside MusicBrainzClient ---

    def _pick_top_name(self, items: list[dict]) -> Optional[str]:
        """Pick the name with highest 'count' (if present), else the first."""
        if not items:
            return None
        def cnt(x):
            try:
                return int(x.get("count", 0))
            except Exception:
                return 0
        return max(items, key=cnt).get("name")


    def _enrich_recording_cascade(self, rec: Recording, need_date: bool, need_genre: bool) -> None:
        """
        One recording lookup (with correct includes), then (if needed)
        Release -> Release Group -> Artist lookups for genre.
        Respects the global 1 req/sec rate limit configured in __init__.
        """
        try:
            # 1) Recording lookup: releases (for dates + RG ids) and artist-credits for artist ids.
            includes = []
            if need_date or need_genre:
                includes.extend(["releases", "artist-credits"])
            if need_genre:
                includes.append("tags")  # <-- 'genres' is NOT a valid include

            data = mb.get_recording_by_id(rec.mbid, includes=includes)
            recording = data.get("recording", {})

            # ---- Date enrichment from recording -> releases
            if need_date and not rec.first_release_date:
                rels = recording.get("release-list", []) or []
                earliest = self._earliest_date_from_releases(rels)
                if earliest:
                    rec.first_release_date = earliest
                    rec.decade = self._to_decade(self._year_from_date(earliest))

            if not need_genre or rec.genre:
                return

            # ---- Genre enrichment cascade

            # (a) Recording-level tags
            rec.genre = self._pick_top_name(recording.get("tag-list") or [])

            # (b) Release-level (first linked release)
            rgid = None
            if not rec.genre:
                rels = recording.get("release-list") or []
                if rels:
                    first_release_id = rels[0].get("id")
                    if first_release_id:
                        try:
                            # Ask the release for its own tags, and include release-group linkage.
                            rdata = mb.get_release_by_id(first_release_id, includes=["tags", "release-groups"])
                            release = rdata.get("release", {})
                            # try release tags directly
                            rec.genre = self._pick_top_name(release.get("tag-list") or [])
                            # capture RG id for next step
                            rg = release.get("release-group") or {}
                            rgid = rg.get("id")
                        except Exception as e:
                            print(f"[release error] {e}")

            # (c) Release-group level (if still no genre)
            if not rec.genre and rgid:
                try:
                    rg_data = mb.get_release_group_by_id(rgid, includes=["tags"])
                    rg = rg_data.get("release-group", {})
                    rec.genre = self._pick_top_name(rg.get("tag-list") or [])
                except Exception as e:
                    print(f"[genre error] {e}")

            # (d) Artist level (first credited artist) — often the most populated
            if not rec.genre:
                ac = recording.get("artist-credit") or []
                first_artist = None
                for el in ac:
                    if isinstance(el, dict) and "artist" in el:
                        first_artist = el["artist"].get("id")
                        if first_artist:
                            break
                if first_artist:
                    try:
                        a_data = mb.get_artist_by_id(first_artist, includes=["tags"])
                        artist = a_data.get("artist", {})
                        rec.genre = self._pick_top_name(artist.get("tag-list") or [])
                    except Exception as e:
                        print(f"[artist error] {e}")

        except Exception as e:
            # swallow enrichment failures; base search results still returned
            print(f"[enrich error] {e}")



    def _enrich_recording(self, rec: Recording, need_date: bool, need_genre: bool) -> None:
        """Single lookup to enrich date and/or genres."""
        try:
            includes = []
            if need_date:
                includes.append("releases")
            if need_genre:
                includes.append("tags")  # <-- remove "genres"
            if not includes:
                return

            data = mb.get_recording_by_id(rec.mbid, includes=includes)
            recording = data.get("recording", {})

            # Date enrichment
            if need_date and not rec.first_release_date:
                rels = recording.get("release-list", []) or []
                earliest = self._earliest_date_from_releases(rels)
                if earliest:
                    rec.first_release_date = earliest
                    rec.decade = self._to_decade(self._year_from_date(earliest))

            # Genre enrichment (from tags only)
            if need_genre and not rec.genre:
                tags = recording.get("tag-list") or []
                if tags:
                    def tcount(t):
                        try:
                            return int(t.get("count", 0))
                        except Exception:
                            return 0
                    best_tag = max(tags, key=tcount)
                    rec.genre = best_tag.get("name")

        except Exception as e:
            print(f"[enrich error] {e}")
