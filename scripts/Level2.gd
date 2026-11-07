extends Node2D
# Nivel 2 — Top-down shooter

@export var ghost_scene: PackedScene
@export var collectible_scene: PackedScene

func _ready() -> void:
	AudioManager.play_music("level1")
	# El fantasma es el personaje que murió en el otro nivel
	if GameData.is_dead("character1") and ghost_scene:
		var ghost: CharacterBody2D = ghost_scene.instantiate()
		ghost.character_id = "character1"
		ghost.top_down_mode = true
		add_child(ghost)
		ghost.global_position = Vector2(400, 150)

	if "collectible2" not in GameData.found_collectibles and collectible_scene:
		var col = collectible_scene.instantiate()
		add_child(col)
		col.global_position = Vector2(700, 80)
		col.collectible_id = "collectible2"

func _on_end_zone_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		# Comprobar condición de final verdadero
		if GameData.secret_unlocked and GameData.found_collectibles.size() >= 2:
			SceneManager.go_to_true_ending()
		else:
			SceneManager.go_to_main_menu()
