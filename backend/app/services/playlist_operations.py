import copy

def execute_playlist_operations(current_playlist, operations, rag_chain):
    """
    Executes playlist operations like replace, add, exclude, remove, clear.
    Handles cases where range might be invalid or incomplete.
    """
    playlist = copy.deepcopy(current_playlist)

    for op in operations.get("operations", []):
        action = op.get("action")

        # Validate action
        if action not in ["replace", "add", "exclude", "remove", "clear"]:
            continue

        # === 1. REPLACE ===
        if action == "replace":
            start, end = normalize_range(op.get("range", []))
            filters = op.get("filters", {})
            count = (end - start) + 1
            query = build_query(filters)
            rag_result = rag_chain.recommend_songs(query, top_k=count)
            new_songs = convert_rag_to_struct(rag_result)
            playlist[start - 1:end] = new_songs

        # === 2. ADD ===
        elif action == "add":
            filters = op.get("filters", {})
            count = op.get("count", 1)
            position = op.get("position", "end")
            query = build_query(filters)
            rag_result = rag_chain.recommend_songs(query, top_k=count)
            new_songs = convert_rag_to_struct(rag_result)

            if position == "start":
                playlist = new_songs + playlist
            elif position == "end":
                playlist.extend(new_songs)
            else:
                try:
                    index = int(position) - 1
                    playlist[index:index] = new_songs
                except:
                    playlist.extend(new_songs)

        # === 3. EXCLUDE ===
        elif action == "exclude":
            filters = op.get("filters", {})
            playlist = [
                s for s in playlist
                if not song_matches_filters(s, filters)
            ]

        # === 4. REMOVE (by position) ===
        elif action == "remove":
            start, end = normalize_range(op.get("range", []))
            playlist = [
                s for i, s in enumerate(playlist, start=1)
                if not (start <= i <= end)
            ]

        # === 5. CLEAR ===
        elif action == "clear":
            playlist = []

    return playlist


def normalize_range(song_range):
    """Ensure range is always a (start, end) tuple."""
    if isinstance(song_range, list):
        if len(song_range) == 2:
            return song_range[0], song_range[1]
        elif len(song_range) == 1:
            return song_range[0], song_range[0]
    return 1, 1


def build_query(filters):
    """Convert filter dict to text query."""
    parts = []
    for key, val in filters.items():
        if isinstance(val, list):
            parts.append(f"{key}: {', '.join(val)}")
        else:
            parts.append(f"{key}: {val}")
    return " ".join(parts)


def convert_rag_to_struct(rag_result: str):
    """Convert rag_chain output string into list of song dicts."""
    structured = []
    for line in rag_result.splitlines():
        if " – " in line:
            try:
                _, rest = line.split(". ", 1)
                artist, title_decade = rest.split(" – ", 1)
                title, decade = title_decade.rsplit("(", 1)
                structured.append({
                    "artist": artist.strip(),
                    "title": title.strip(),
                    "decade": decade.replace(")", "").strip(),
                    "genre": "unknown",
                    "mood": "unknown"
                })
            except ValueError:
                continue
    return structured


def song_matches_filters(song, filters):
    """Check if a song dict matches given filters."""
    for key, value in filters.items():
        song_value = song.get(key)
        if isinstance(value, list):
            if song_value in value:
                return True
        else:
            if song_value == value:
                return True
    return False
