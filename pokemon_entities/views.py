import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    db_pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lte=localtime(),
        disappeared_at__gt=localtime(),
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    if db_pokemon_entities:
        for pokemon_entity in db_pokemon_entities:
            if not pokemon_entity.pokemon.image:
                continue

            pokemon_image_url = request.build_absolute_uri(
                pokemon_entity.pokemon.image.url,
            )

            add_pokemon(
                folium_map, pokemon_entity.lat,
                pokemon_entity.lon,
                pokemon_image_url,
        )

    db_pokemons = Pokemon.objects.all()
    pokemons_on_page = []

    if db_pokemons:
        for pokemon in db_pokemons:
            if pokemon.image:
                pokemon_image_url = request.build_absolute_uri(
                    pokemon.image.url,
                )
            else:
                pokemon_image_url = None

            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': pokemon_image_url,
                'title_ru': pokemon.title,
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    db_pokemon = Pokemon.objects.get(id=pokemon_id)

    if not db_pokemon:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    if db_pokemon.image:
        pokemon_image = request.build_absolute_uri(
                db_pokemon.image.url,
            )
    else:
        pokemon_image = None

    pokemon = {
        'title_ru': db_pokemon.title,
        'img_url': pokemon_image,
        'entities': None,
    }

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    pokemon_entities = PokemonEntity.objects.filter(
        pokemon=db_pokemon,
        appeared_at__lte=localtime(),
        disappeared_at__gt=localtime(),
    )

    if pokemon_entities:
        for pokemon_entity in pokemon_entities:
            if not pokemon_entity.pokemon.image:
                continue

            pokemon_image_url = request.build_absolute_uri(
                pokemon_entity.pokemon.image.url,
            )

            add_pokemon(
                folium_map, pokemon_entity.lat,
                pokemon_entity.lon,
                pokemon_image_url,
            )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon
    })
