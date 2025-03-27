import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Recorre las películas, asigna la imagen correspondiente de la carpeta media/movie/images/ y actualiza la base de datos con la ruta de la imagen"

    def handle(self, *args, **kwargs):
        # Ruta de la carpeta donde se encuentran las imágenes
        images_folder = 'media/movie/images/'
        if not os.path.exists(images_folder):
            self.stderr.write(f"La carpeta de imágenes '{images_folder}' no existe.")
            return

        # Obtenemos todas las películas de la base de datos
        movies = Movie.objects.all()
        self.stdout.write(f"Se encontraron {movies.count()} películas.")

        updated_count = 0

        for movie in movies:
            # Suponemos que el nombre del archivo es "m_<titulo>.png"
            # Si el título contiene espacios, se usan tal cual o se podría limpiar.
            image_filename = f"m_{movie.title}.png"
            image_full_path = os.path.join(images_folder, image_filename)

            if os.path.exists(image_full_path):
                # La ruta relativa que se guardará en la base de datos, respecto a media/
                relative_path = os.path.join('movie/images', image_filename)
                movie.image = relative_path
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Imagen asignada para: {movie.title}"))
            else:
                self.stderr.write(f"No se encontró imagen para la película: {movie.title}")

        self.stdout.write(self.style.SUCCESS(f"Proceso finalizado. Imágenes actualizadas para {updated_count} películas."))
