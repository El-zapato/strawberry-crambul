extends CharacterBody2D
# Personaje 2 — Disparos
# Movimiento top-down 8 direcciones + disparo hacia cursor

const SPEED := 160.0

var lives := 3
var hud: Node = null

@export var projectile_scene: PackedScene

func _ready() -> void:
	add_to_group("player")
	lives = GameData.get_lives("character2")
	hud = get_tree().get_first_node_in_group("hud")
	if hud:
		hud.update_lives(lives)

func _physics_process(_delta: float) -> void:
	var direction := Vector2(
		Input.get_axis("move_left", "move_right"),
		Input.get_axis("move_up", "move_down")
	).normalized()
	velocity = direction * SPEED
	move_and_slide()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton \
			and event.button_index == MOUSE_BUTTON_LEFT \
			and event.pressed:
		_shoot()

func _shoot() -> void:
	if projectile_scene == null:
		return
	var proj: Node2D = projectile_scene.instantiate()
	get_parent().add_child(proj)
	proj.global_position = global_position
	proj.direction = (get_global_mouse_position() - global_position).normalized()

func take_damage() -> void:
	lives -= 1
	AudioManager.play_sfx("hurt" if lives > 0 else "death")
	if lives > 0:
		GameData.set_lives("character2", lives)
	if hud:
		hud.update_lives(lives)
	if lives <= 0:
		_die()

func _die() -> void:
	GameData.kill_character("character2")
	SceneManager.go_to_death_screen("character2")
