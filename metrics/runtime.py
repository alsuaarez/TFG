from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
import pandas as pd
import pickle

# Funcion para obtener la clase de los jugadores
def _get_player_class(tracks: Dict[str, Any]) -> Optional[str]:
    for c in ("players", "player"):
        if c in tracks:
            return c
    return None

# Funcion para convertir el frame a un diccionario
def _frame_as_dict(frame_entry) -> Dict[Any, Dict[str, Any]]:
    if isinstance(frame_entry, dict):
        return frame_entry
    if isinstance(frame_entry, list):
        out = {}
        for it in frame_entry:
            if isinstance(it, dict):
                tid = it.get("track_id") or it.get("id")
                if tid is not None:
                    out[tid] = it
        return out
    return {}

# Funcion para cargar los tracks desde un pkl
def load_tracks_from_pkl(input_pkl: str | Path = "tracks_final.pkl") -> Dict[str, Any]:
    input_path = Path(input_pkl)
    with open(input_path, 'rb') as f:
        tracks = pickle.load(f)
    return tracks

# Funcion para procesar los tracks de los jugadores desde un pkl y guardarlos en un csv
def tracks_to_df_min(tracks: Dict[str, Any]) -> pd.DataFrame:
    player_class = _get_player_class(tracks)
    if not player_class:
        return pd.DataFrame()

    player_frames = tracks[player_class]
    rows = []

    for f, frame_data in enumerate(player_frames):
        frame_dict = _frame_as_dict(frame_data)
        
        # Poseedor de balón
        owner = None
        for tid, info in frame_dict.items():
            if info.get("has_ball"):
                owner = tid
                break
                
        # Rellenar filas para cada jugador
        for tid, info in frame_dict.items():
            rows.append({
                "frame": f,
                "track_id": tid,
                "team": info.get("team"),
                "speed": info.get("speed"),        
                "distance": info.get("distance"), 
                "pos_x_jug": info.get("position_transformed")[0] if info.get("position_transformed") is not None else None,
                "pos_y_jug": info.get("position_transformed")[1] if info.get("position_transformed") is not None else None,
                "ball_owner_id": owner,
                "has_ball": bool(info.get("has_ball", False)),
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["frame"] = pd.to_numeric(df["frame"], errors="coerce").astype("Int64")
    df["has_ball"] = df["has_ball"].astype("boolean")
    return df

# Funcion para procesar los tracks del balón desde un pkl y guardarlos en un csv
def ball_tracks_to_df(tracks: Dict[str, Any]) -> pd.DataFrame:
    if "ball" not in tracks:
        return pd.DataFrame()

    ball_frames = tracks["ball"]
    rows = []

    for f, frame_data in enumerate(ball_frames):
        frame_dict = _frame_as_dict(frame_data)
        
        # Extraemos la información del balón
        for tid, info in frame_dict.items():
            pos_trans = info.get("position_transformed")
            rows.append({
                "frame": f,
                "pos_x_bal": pos_trans[0] if pos_trans is not None else None,
                "pos_y_bal": pos_trans[1] if pos_trans is not None else None
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["frame"] = pd.to_numeric(df["frame"], errors="coerce").astype("Int64")
    return df

def save_df_min(df: pd.DataFrame, out_csv: str | Path) -> Path:
    out = Path(out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out

# Funcion para procesar los tracks desde un pkl y guardarlos en dos csv
def process_tracks_from_pkl(input_pkl: str | Path = "tracks_final.pkl",
                            out_csv_players: str | Path = "data/df_min_from_pkl.csv",
                            out_csv_ball: str | Path = "data/df_ball_tracks.csv") -> tuple[pd.DataFrame, pd.DataFrame]:

    tracks = load_tracks_from_pkl(input_pkl)
    df_players = tracks_to_df_min(tracks)
    df_ball = ball_tracks_to_df(tracks)
    
    if not df_players.empty:
        out_p = save_df_min(df_players, out_csv_players)
        print(f"CSV de jugadores guardado en {out_p} ({len(df_players)} filas)")
    else:
        print("No se encontraron jugadores validos o faltan datos.")

    if not df_ball.empty:
        out_b = save_df_min(df_ball, out_csv_ball)
        print(f"CSV del balón guardado en {out_b} ({len(df_ball)} filas)")
    else:
        print("No se encontraron datos del balón.")

    return df_players, df_ball

if __name__ == "__main__":
    process_tracks_from_pkl()