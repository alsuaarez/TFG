"""
Veremos esto niño,esta clase hace justo lo que tiene que hacer y lo hace
bien.(tampoco es que sea grande buajjaja) Me gusta mucho y joder, basnte buena idea que la distancia se mida desde los pies del jugador (las esquinas
inferiores del bbox) en lugar del centro, es mucho más realista para saber quién tiene el
control del balón diria.

Un par de tips para que quede perfecto: el `max_player_ball_distance` es un candidato
ideal para sacarlo a un archivo de configuración, así lo podemos ajustar fácilmente sin
tocar esta lógica. Y si como idea ->, podríamos darle un
poco de "inercia" a la posesión: si un jugador ya tenía el balón en el frame anterior,
que tenga prioridad para mantenerlo a no ser que otro jugador esté muchísimo más cerca.
dale una vuelta...

"""
import sys 
sys.path.append('../')
from utils import get_center_of_bbox, measure_distance

class PlayerBallAssigner():
    def __init__(self):
        self.max_player_ball_distance = 70
    
    def assign_ball_to_player(self,players,ball_bbox):
        ball_position = get_center_of_bbox(ball_bbox)

        miniumum_distance = 99999
        assigned_player=-1

        for player_id, player in players.items():
            player_bbox = player['bbox']

            distance_left = measure_distance((player_bbox[0],player_bbox[-1]),ball_position)
            distance_right = measure_distance((player_bbox[2],player_bbox[-1]),ball_position)
            distance = min(distance_left,distance_right)

            if distance < self.max_player_ball_distance:
                if distance < miniumum_distance:
                    miniumum_distance = distance
                    assigned_player = player_id

        return assigned_player
