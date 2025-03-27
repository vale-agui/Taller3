import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Visualiza los embeddings de una película seleccionada al azar"

    def handle(self, *args, **kwargs):
        # Seleccionar una película al azar
        movie = Movie.objects.order_by('?').first()
        if not movie:
            self.stderr.write("No hay películas en la base de datos.")
            return

        try:
            # Convertir el embedding almacenado (binario) a un array de float32
            embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)
        except Exception as e:
            self.stderr.write(f"Error al leer el embedding para {movie.title}: {e}")
            return

        # Mostrar la información de la película y su embedding
        self.stdout.write(f"Película seleccionada: {movie.title}")
        self.stdout.write("Embedding completo:")
        self.stdout.write(str(embedding_vector))
        self.stdout.write("Primeros 10 valores del embedding:")
        self.stdout.write(str(embedding_vector[:10]))
