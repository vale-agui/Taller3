import os
import json
import numpy as np
from django.core.management.base import BaseCommand
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

class Command(BaseCommand):
    help = "Recomienda una película basándose en un prompt comparando embeddings de descripción"

    def add_arguments(self, parser):
        parser.add_argument(
            '--prompt',
            type=str,
            help="Texto para generar el embedding y comparar con las películas",
            default="película de un pianista"
        )
        parser.add_argument(
            '--embeddings_file',
            type=str,
            help="Ruta al archivo JSON con los embeddings de las películas",
            default="movie_embeddings.py"
        )

    def handle(self, *args, **options):
        # Buscar y cargar el archivo de entorno openAI.env
        env_path = find_dotenv('openAI.env')
        if not env_path:
            self.stderr.write("No se encontró el archivo openAI.env.")
            return
        load_dotenv(env_path)
        
        # Verificar que la variable se llame exactamente 'openai_apikey'
        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write("API key no encontrada en el archivo de entorno. Asegúrate de que la variable se llame 'openai_apikey'.")
            return

        client = OpenAI(api_key=api_key)

        # Cargar el archivo JSON con las películas y sus embeddings
        embeddings_file = options['embeddings_file']
        if not os.path.exists(embeddings_file):
            self.stderr.write(f"No se encontró el archivo de embeddings '{embeddings_file}'. Verifica que el archivo exista en la ubicación correcta.")
            return

        with open(embeddings_file, 'r', encoding='utf-8') as file:
            movies = json.load(file)

        # Función para obtener el embedding de un texto usando OpenAI
        def get_embedding(text, model="text-embedding-3-small"):
            text = text.replace("\n", " ")
            response = client.embeddings.create(input=[text], model=model)
            return response.data[0].embedding

        # Función para calcular la similitud coseno
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Obtener el prompt y calcular su embedding
        prompt = options['prompt']
        self.stdout.write(f"Usando prompt: {prompt}")
        prompt_emb = get_embedding(prompt)

        # Comparar el embedding del prompt con cada película
        similarities = []
        for movie in movies:
            similarity = cosine_similarity(prompt_emb, movie['embedding'])
            similarities.append(similarity)

        similarities = np.array(similarities)
        idx = int(np.argmax(similarities))
        recommended_movie = movies[idx]['title']

        self.stdout.write(self.style.SUCCESS(f"Película recomendada: {recommended_movie}"))
