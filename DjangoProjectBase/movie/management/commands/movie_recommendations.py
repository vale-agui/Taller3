import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

class Command(BaseCommand):
    help = "Recomienda una película basada en la palabra clave proporcionada"

    def add_arguments(self, parser):
        parser.add_argument(
            '--prompt',
            type=str,
            help="Texto para generar el embedding y recomendar películas",
            default="película de un pianista"
        )

    def handle(self, *args, **options):
        # Cargar las variables de entorno desde openAI.env
        env_path = find_dotenv('openAI.env')
        if not env_path:
            self.stderr.write("No se encontró el archivo openAI.env.")
            return
        load_dotenv(env_path)

        # Verificar la API key
        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write("API key no encontrada en openAI.env. Asegúrate de que la variable se llame 'openai_apikey'.")
            return

        client = OpenAI(api_key=api_key)

        # Función para obtener el embedding de un texto usando OpenAI
        def get_embedding(text, model="text-embedding-3-small"):
            text = text.replace("\n", " ")
            response = client.embeddings.create(input=[text], model=model)
            return np.array(response.data[0].embedding, dtype=np.float32)

        # Función para calcular la similitud coseno
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Obtener el prompt proporcionado o usar el valor por defecto
        prompt = options.get('prompt')
        self.stdout.write(f"Usando prompt: {prompt}")
        prompt_embedding = get_embedding(prompt)

        # Obtener todas las películas de la base de datos
        movies = Movie.objects.all()
        if not movies.exists():
            self.stderr.write("No hay películas en la base de datos.")
            return

        best_similarity = -1
        recommended_movie = None

        # Comparar el embedding del prompt con el embedding de cada película
        for movie in movies:
            try:
                # Convertir el embedding almacenado (binario) a un array de float32
                movie_embedding = np.frombuffer(movie.emb, dtype=np.float32)
                similarity = cosine_similarity(prompt_embedding, movie_embedding)
            except Exception as e:
                self.stderr.write(f"Error al procesar el embedding para '{movie.title}': {e}")
                continue

            if similarity > best_similarity:
                best_similarity = similarity
                recommended_movie = movie

        if recommended_movie:
            self.stdout.write(self.style.SUCCESS(
                f"Película recomendada: {recommended_movie.title} (similitud: {best_similarity:.4f})"
            ))
        else:
            self.stdout.write("No se encontró una película recomendada.")
