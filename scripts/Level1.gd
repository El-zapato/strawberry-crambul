extends Node2D
# Nivel 1 — Plataformas 2D lateral (entorno rural)
# Recorrido de plataformas con paraguas. Al final, en la zona elevada, se ve
# la casa de la carpintera pero el puente colgante ha desaparecido.

@export var character1_scene: PackedScene
@export var secret_scene: PackedScene
@export var ghost_scene: PackedScene
## Tamaño del nivel en pixeles (límites de la cámara)
@export var level_size := Vector2i(2400, 320)
## Cuánto se desplaza la cámara para mostrar la casa de la carpintera
@export var bridge_view_offset := 300.0

const INTRO_TEXT := "Entrega tu carta de confesión a la carpintera que vive en la colina."
const BRIDGE_TEXTS := [
	"A lo lejos se ve la casa de la carpintera...",
	"Pero el puente colgante... ha desaparecido.",
	"No hay forma de cruzar.",
]

var player: CharacterBody2D = null
var camera: Camera2D = null
var _bridge_seen := false

@onready var hud: CanvasLayer = $HUD
@onready var hidden_cover: TileMapLayer = $HiddenCover

func _ready() -> void:
	_spawn_player()
	_spawn_ghosts()

	# El coleccionable solo aparece si no fue recogido antes
	var collectible := get_node_or_null("Collectible")
	if collectible:
		if collectible.collectible_id in GameData.found_collectibles:
			collectible.queue_free()
		else:
			collectible.collected.connect(_on_collectible_collected)

	AudioManager.play_music("level1")
	hud.show_message(INTRO_TEXT, 4.0)

func _spawn_player() -> void:
	var scene := secret_scene if SceneManager.current_character == "secret" else character1_scene
	player = scene.instantiate()
	player.position = $PlayerStart.position
	add_child(player)

	camera = Camera2D.new()
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = level_size.x
	camera.limit_bottom = level_size.y
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 6.0
	camera.position.y = -16
	player.add_child(camera)

func _spawn_ghosts() -> void:
	# Los personajes que murieron antes aparecen como fantasmas en el nivel
	var spawns := $GhostSpawns.get_children()
	var i := 0
	for dead_id in GameData.dead_characters:
		if dead_id == player.character_id or ghost_scene == null or spawns.is_empty():
			continue
		var ghost: CharacterBody2D = ghost_scene.instantiate()
		ghost.character_id = dead_id
		ghost.position = spawns[i % spawns.size()].position
		add_child(ghost)
		i += 1

func _on_collectible_collected(_id: String) -> void:
	hud.show_message("Encontraste una fresa extraña... (%d/2)" % GameData.found_collectibles.size(), 3.0)

func _on_hidden_zone_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		create_tween().tween_property(hidden_cover, "modulate:a", 0.25, 0.3)

func _on_hidden_zone_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		create_tween().tween_property(hidden_cover, "modulate:a", 1.0, 0.3)

func _on_bridge_trigger_body_entered(body: Node) -> void:
	if _bridge_seen or not body.is_in_group("player"):
		return
	_bridge_seen = true
	# Escena 4: el camino bloqueado
	player.controls_enabled = false
	AudioManager.stop_music(1.5)
	AudioManager.play_sfx("bridge")
	var tween := create_tween().set_trans(Tween.TRANS_SINE)
	tween.tween_property(camera, "offset:x", bridge_view_offset, 2.0)
	await tween.finished
	for text in BRIDGE_TEXTS:
		await hud.show_message(text, 2.5)
	tween = create_tween().set_trans(Tween.TRANS_SINE)
	tween.tween_property(camera, "offset:x", 0.0, 1.5)
	await tween.finished
	player.controls_enabled = true
	AudioManager.play_music("level1", 2.0)
