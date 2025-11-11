"""
Continuemos por acá,mmm diria que  la lógica que has montado aquí para asignar los equipos esta bien. Lo de
usar K-Means en dos pasos (primero para sacar el color de la camiseta y luego para agrupar
esos colores en dos equipos) es un enfoque curioso, que decente. Y el truco de usar las esquinas de la
imagen para identificar el clúster del césped y así saber cuál es el del jugador, esta muy biien.

He visto el apaño para el `player_id == 91`. Es una solución rápida que funciona,pero es una CUTRADA,
Si en el futuro nos da problemas(te los va a dar), podríamos investigar por qué falla
la asignación con ese jugador en concreto. A veces, pasar la imagen a un espacio de color
como HSV(means:modelo de color), que es más robusto a cambios de iluminación, puede hacer que nuestro querido
clustering sea más estable. Podríamos probarlo si vemos que falla con más jugadores. Pero vamos, que la
idea general de la clase es esta guay para tu tfg.
NO se me ocurre aca pero podrías desarrollar algo la logica para sacar nuevas métricas...(aunque esto va a depender de la calidad de la imagen,
otros modelso que puedas usar, benchmarks etc...
"""
from sklearn.cluster import KMeans

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}
        self.player_team_dict = {}
    
    def get_clustering_model(self,image):
        # Reshape the image to 2D array
        image_2d = image.reshape(-1,3)

        # Preform K-means with 2 clusters
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=1)
        kmeans.fit(image_2d)

        return kmeans

    def get_player_color(self,frame,bbox):
        image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]

        top_half_image = image[0:int(image.shape[0]/2),:]

        # Get Clustering model
        kmeans = self.get_clustering_model(top_half_image)

        # Get the cluster labels forr each pixel
        labels = kmeans.labels_

        # Reshape the labels to the image shape
        clustered_image = labels.reshape(top_half_image.shape[0],top_half_image.shape[1])

        # Get the player cluster
        corner_clusters = [clustered_image[0,0],clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]]
        non_player_cluster = max(set(corner_clusters),key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster

        player_color = kmeans.cluster_centers_[player_cluster]

        return player_color


    def assign_team_color(self,frame, player_detections):
        
        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection["bbox"]
            player_color =  self.get_player_color(frame,bbox)
            player_colors.append(player_color)
        
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=10)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]


    def get_player_team(self,frame,player_bbox,player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]

        player_color = self.get_player_color(frame,player_bbox)

        team_id = self.kmeans.predict(player_color.reshape(1,-1))[0]
        team_id+=1

        if player_id ==91:
            team_id=1

        self.player_team_dict[player_id] = team_id

        return team_id
