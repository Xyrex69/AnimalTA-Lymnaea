import numpy as np
from AnimalTA.E_Post_tracking.b_Analyses import Functions_Analyses_Speed
import math


# Default movement threshold (cm/s) used whenever a project has none set
# (Vid.Analyses[0] == 0, which is AnimalTA's initial value). A small positive
# speed floor so that sub-pixel tracking jitter is not counted as "moving",
# which would otherwise make "average speed while moving" == "average speed"
# and "proportion of time moving" ~= 1.0. Tuned for slow animals such as
# Lymnaea; researchers can still override it per video in the speed-graph
# pop-up. Applied uniformly to existing and future projects so results are
# consistent across the pop-up and the exported Results files.
DEFAULT_MOV_THRESHOLD = 0.03


def effective_mov_threshold(value):
    """Return the movement threshold to actually use.

    A stored value of 0 (or a non-numeric/unset value) means "no threshold was
    chosen", so we fall back to DEFAULT_MOV_THRESHOLD. Any explicit positive
    value set by the user is used as-is.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    return v if v > 0 else DEFAULT_MOV_THRESHOLD


def _smooth_coos_for_dist(Coos, Vid):
    """Return a smoothed copy of Coos for distance/speed computation only.

    Applies a Savitzky-Golay filter (window = Vid.Dist_smooth_window seconds,
    polynomial order 2) independently to each coordinate column. Contiguous
    finite segments are smoothed separately so tracking gaps are not
    interpolated across. The original Coos array is never modified.

    Falls back to the original array if scipy is unavailable, the video is
    too short to smooth, or the attribute is missing (backward compatibility
    with project files saved before this patch).
    """
    try:
        from scipy.signal import savgol_filter
    except ImportError:
        return Coos

    win_s = float(getattr(Vid, "Dist_smooth_window", 2.5))
    fps = float(Vid.Frame_rate[1])
    win_fr = int(round(win_s * fps))
    if win_fr % 2 == 0:
        win_fr += 1
    poly = 2

    n = Coos.shape[0]
    if n < win_fr or win_fr < poly + 2:
        return Coos

    smoothed = Coos.astype(float).copy()
    for col in range(Coos.shape[1]):
        vals = smoothed[:, col]
        finite = np.isfinite(vals)
        if not np.any(finite):
            continue
        if np.all(finite):
            smoothed[:, col] = savgol_filter(vals, win_fr, poly, mode="interp")
            continue
        # Smooth each contiguous finite segment independently
        in_seg = False
        seg_start = 0
        for i in range(n + 1):
            cur = finite[i] if i < n else False
            if cur and not in_seg:
                seg_start = i
                in_seg = True
            elif not cur and in_seg:
                in_seg = False
                seg_len = i - seg_start
                w = win_fr if seg_len >= win_fr else (seg_len if seg_len % 2 == 1 else seg_len - 1)
                if w >= poly + 2:
                    smoothed[seg_start:i, col] = savgol_filter(
                        vals[seg_start:i], w, poly, mode="interp")
    return smoothed


def prepare_Dists(Coos, Scale):
    Dists = np.sqrt(np.diff(Coos[:, 0]) ** 2 + np.diff(Coos[:, 1]) ** 2) / float(Scale[0])
    Dists = np.append(np.nan, Dists)
    return(Dists)

def prepare_Speeds(Dists, Frame_rate):
    Speeds = Dists / (1 / Frame_rate)
    return(Speeds)

def prepare_State(Speeds, mov_threshold):
    mov_threshold = effective_mov_threshold(mov_threshold)
    State = np.zeros(len(Speeds))
    State[np.where(Speeds > mov_threshold)] = 1
    State[np.where(np.isnan(Speeds))] = np.nan
    return(State)

def prepare_Acceleration(Speeds, Frame_rate):
    Acc = np.diff(Speeds) / (1 / Frame_rate)
    Acc = np.append(np.nan, Acc)
    return(Acc)

def prepare_Orient(Coos):
    dx=np.diff(Coos[:, 1])
    dy=np.diff(Coos[:, 0])
    Orientation = np.arctan2(dx, dy)
    Orientation[(dx == 0) & (dy == 0)] = np.nan
    Orientation = np.append(np.nan, Orientation)
    Orientation = (Orientation * 180) / math.pi
    return(Orientation)

def prepare_Angles(Orient):
    Angles = np.diff(Orient)
    Angles = np.append(np.nan, Angles)
    Angles[np.where(Angles > 180)] = Angles[np.where(Angles > 180)] - 360
    Angles[np.where(Angles < -180)] = Angles[np.where(Angles < -180)] + 360
    Angles = np.abs(Angles)
    return(Angles)

def prepare_Angular_Speed(Angles, Frame_rate):
    return(Angles / (1 / Frame_rate))

def prepare_Meander(Angles, Dists):
    Meander = Angles / Dists
    Meander[np.where(Dists == 0)] = np.nan
    return(Meander)

def prepare_details(Coos, Area, Vid, first, Arenas, loading_frame=None):
    '''Function used to create a table with all important data related to the frame by frame trajectories.
    Coos=Coordintaes of the individual
    Area=Id of the arena of the individual
    Vid=Video
    first=first frame to look at'''

    All_explored_values_cum = None
    All_explored_values_bin = None

    Details = []
    if Vid.Details_options["Frame"]:
        Details.append(list(range(first, first + len(Coos))))
    if Vid.Details_options["Time"]:
        Details.append(list(map(lambda x: round(x / Vid.Frame_rate[1], 3), range(first, first + len(Coos)))))

    if Vid.Details_options["X-Y_Coordinates"]:
        Details.append(list(
            Coos[:, 0] / float(Vid.Scale[0])))  # We will save here the detailed informations (for each frame)
        Details.append(list(Coos[:, 1] / float(Vid.Scale[0])))

    # Moving threshold:
    # Smooth a copy of the coordinates for distance/speed only.
    # Coos itself is left untouched so heatmaps, trajectory display,
    # orientation, and exploration metrics all use the raw positions.
    Coos_sm = _smooth_coos_for_dist(Coos, Vid)
    Dists=prepare_Dists(Coos_sm, Vid.Scale)
    if Vid.Details_options["Distance"]:
        Details.append(Dists)

    Speeds=prepare_Speeds(Dists, Vid.Frame_rate[1])
    if Vid.Details_options["Speed"]:
        Details.append(Speeds)

    State=prepare_State(Speeds, Vid.Analyses[0])
    if Vid.Details_options["Moving"]:
        Details.append(State)

    if Vid.Details_options["Corrected_Moving"]:
        stops_e, moves_e, stops_m, moves_m, details_state = Functions_Analyses_Speed.separate_0s_1s_durations_nan(
            State, Vid.Frame_rate[1],
            Vid.Stops_Moves_options[1], return_details=True)
        Details.append(details_state)

    if Vid.Details_options["Acceleration"]:
        Acc = prepare_Acceleration(Speeds, Vid.Frame_rate[1])
        Details.append(Acc)

    # Traveled distance:
    Orientation=prepare_Orient(Coos)
    if Vid.Details_options["Orientation"]:
        Details.append(Orientation)

    Angles=prepare_Angles(Orientation)
    if Vid.Details_options["Angle_change"]:
        Details.append(Angles.copy())

    if Vid.Details_options["Angular_speed"]:
        Angular_speed = prepare_Angular_Speed(Angles.copy(), Vid.Frame_rate[1])
        Details.append(Angular_speed)

    Meanders = prepare_Meander(Angles.copy(), Dists)
    if Vid.Details_options["Meander"]:
        Details.append(Meanders)

    if Vid.Details_options["Distances_to_elem_interest"]:
        for Shape in Vid.Analyses[1][Area]:
            if Shape[0] == "Line":
                Dist_to = Functions_Analyses_Speed.details_line(Coos[:, 0],
                                                  Coos[:, 1], Shape,
                                                  float(Vid.Scale[0]))
                Details.append(Dist_to)

            if Shape[0] == "Point":
                Dist_to, Inside = Functions_Analyses_Speed.details_Point(Coos[:, 0],
                                                           Coos[:, 1], Shape,
                                                           float(Vid.Scale[0]))
                Details.append(Dist_to)

            elif Shape[0] == "All_borders":
                Dist_to, Inside = Functions_Analyses_Speed.details_All_borders(Coos[:, 0],
                                                                 Coos[:, 1], Shape,
                                                                 Arenas[Area],
                                                                 float(Vid.Scale[0]))
                Details.append(Dist_to)

            elif Shape[0] == "Borders":
                Dist_to, Inside = Functions_Analyses_Speed.details_Borders(Coos[:, 0],
                                                             Coos[:, 1], Shape,
                                                             float(Vid.Scale[0]))
                Details.append(Dist_to)

            elif Shape[0] == "Ellipse" or Shape[0] == "Rectangle" or Shape[
                0] == "Polygon":
                Dist_to, Inside = Functions_Analyses_Speed.details_shape(Coos[:, 0],
                                                           Coos[:, 1], Shape,
                                                           float(Vid.Scale[0]),
                                                           Vid, Arenas[Area])
                Details.append(Dist_to)

    if Vid.Details_options["Exploration_data_per_frame"] and Vid.Analyses[2][0] != 0:
        _, Cells_data = Functions_Analyses_Speed.calculate_exploration(Vid.Analyses[2], Vid,
                                                                       Coos, 0, len(Coos),
                                                                       Arenas[Area], return_cell=True)

        if Vid.Analyses[2][0] == 1:
            Cells_data = [f"X{x}-Y{y}" for x, y in Cells_data]
        elif Vid.Analyses[2][0] == 2:
            Cells_data = [f"D{x}-R{y}" for x, y in Cells_data]
        Details.append(Cells_data)

    elif (Vid.Details_options["Exploration_data_per_frame"] or Vid.Explored_complex) and Vid.Analyses[2][0] == 0:
        All_explored_values_cum, All_explored_values_bin = Functions_Analyses_Speed.calculate_explored(
            Vid.Analyses[2], Vid, Coos, Arenas[Area], loading_frame)
        if Vid.Details_options["Exploration_data_per_frame"]:
            Details.append(All_explored_values_bin)
            if Vid.Explored_complex:
                Details.append(All_explored_values_cum)

    return(Details, State, Dists, Speeds, Meanders, All_explored_values_cum, All_explored_values_bin)

