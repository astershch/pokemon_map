from django.db import models  # noqa F401

# your models here
class Pokemon(models.Model):
    title = models.CharField('Имя', max_length=200)
    title_en = models.CharField(
        'Имя анг.',
        max_length=200,
        blank=True,
    )
    title_jp = models.CharField(
        'Имя яп.',
        max_length=200,
        blank=True,
    )
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='images', null=True, blank=True)
    previous_evolution = models.ForeignKey(
        'self',
        related_name='prev_evolution',
        verbose_name='В кого эволюционирует',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title

class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        related_name='pokemon',
        verbose_name='Покемон',
        on_delete=models.CASCADE,
    )
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    appeared_at = models.DateTimeField('Появится', default=None)
    disappeared_at = models.DateTimeField('Исчезнет', default=None)
    level = models.IntegerField(
        'Уровень',
        default=0,
        null=True,
        blank=True,
    )
    health = models.IntegerField(
        'Здоровье',
        default=0,
        null=True,
        blank=True,
    )
    strength = models.IntegerField(
        'Сила',
        default=0,
        null=True,
        blank=True,
    )
    defence = models.IntegerField(
        'Защита',
        default=0,
        null=True,
        blank=True,
    )
    stamina = models.IntegerField(
        'Выносливость',
        default=0,
        null=True,
        blank=True,
    )
