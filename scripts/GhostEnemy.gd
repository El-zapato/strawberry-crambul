extends CharacterBody2D
# Enemigo fantasma — el personaje caído, semitransparente, persigue al jugador
# Funciona tanto en niveles de plataformas como top-down

const SPEED := 80.0
const DETECT_RANGE := 360.0
const HIT_COOLDOWN := 1.5

const SPRITES := {
	"character1": "res://assets/sprites/characters/character1.png",
	"character2": "res://assets/sprites/characters/character2.png",
	"secret": "res://assets/sprites/characters/character_secret.png",
}

## Personaje muerto que representa este fantasma
@export var character_id := "character1"
## Si es true, el fantasma flota hacia el jugador en 8 direcciones (top-down).
## Si es false, flota atravesando el escenario (plataformas).
@export var top_down_mode := false

var player: Node2D = null
var _hit_cooldown := 0.0
var _time := 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hit_area: Area2D = $HitArea

func _ready() -> void:
	add_to_group("enemy")
	if SPRITES.has(character_id):
		sprite.texture = load(SPRITES[character_id])
	sprite.modulate = Color(0.6, 0.4, 1.0, 0.6)
	if top_down_mode:
		# El Nivel 2 sigue diseñado a 320x180 (se ve con zoom 2), así que el
		# fantasma se reduce a la mitad para conservar su tamaño y velocidad
		scale = Vector2(0.5, 0.5)
	else:
		# En plataformas el fantasma atraviesa paredes y suelo
		collision_mask = 0
	await get_tree().process_frame
	player = get_tree().get_first_node_in_group("player")

func _physics_process(delta: float) -> void:
	_time += delta
	_hit_cooldown = max(_hit_cooldown - delta, 0.0)
	sprite.offset.y = round(sin(_time * 2.0) * 4.0)
	if player == null:
		return

	var to_player := player.global_position - global_position
	if top_down_mode or to_player.length() < DETECT_RANGE:
		velocity = to_player.normalized() * SPEED * scale.x
		sprite.flip_h = to_player.x < 0
	else:
		velocity = Vector2.ZERO
	move_and_slide()

	if _hit_cooldown > 0.0:
		return
	for body in hit_area.get_overlapping_bodies():
		if body.is_in_group("player"):
			body.take_damage()
			_hit_cooldown = HIT_COOLDOWN
