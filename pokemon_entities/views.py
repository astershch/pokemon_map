import folium
import json

from django.shortcuts import get_object_or_404
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
    pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lte=localtime(),
        disappeared_at__gt=localtime(),
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

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

    pokemons = Pokemon.objects.all()
    pokemons_on_page = []

    for pokemon in pokemons:
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
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    if pokemon.image:
        pokemon_image = request.build_absolute_uri(
                pokemon.image.url,
            )
    else:
        pokemon_image = DEFAULT_IMAGE_URL

    pokemon_serialized = {
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': pokemon_image,
        'entities': None,
    }

    if pokemon.previous_evolution:
        pokemon_serialized['previous_evolution'] = {
            'title_ru': pokemon.previous_evolution.title,
            'img_url': request.build_absolute_uri(
                pokemon.previous_evolution.image.url,
            ),
            'pokemon_id': pokemon.previous_evolution.id,
        }

    next_evolution = pokemon.prev_evolutions.filter(
        previous_evolution__id=pokemon.id,
    ).first()

    if next_evolution:
        pokemon_serialized['next_evolution'] = {
            'title_ru': next_evolution.title,
            'img_url': request.build_absolute_uri(
                next_evolution.image.url,
            ),
            'pokemon_id': next_evolution.id,
        }

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    current_time = localtime()

    pokemon_entities = pokemon.pokemon_entities.filter(
        appeared_at__lte=current_time,
        disappeared_at__gt=current_time,
    )

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
        'map': folium_map._repr_html_(), 'pokemon': pokemon_serialized
    })
