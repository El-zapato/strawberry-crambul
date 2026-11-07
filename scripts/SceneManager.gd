extends Node
# Autoload — Transiciones de escena

# ID del personaje que murió (para mostrar en DeathScreen)
var last_dead_character := ""
# ID del personaje elegido en la selección ("character1", "character2" o "secret")
var current_character := "character1"

func go_to(path: String) -> void:
	get_tree().change_scene_to_file(path)

func go_to_main_menu() -> void:
	go_to("res://scenes/ui/MainMenu.tscn")

func go_to_character_select() -> void:
	go_to("res://scenes/ui/CharacterSelect.tscn")

func go_to_level1() -> void:
	go_to("res://scenes/levels/Level1.tscn")

func go_to_level2() -> void:
	go_to("res://scenes/levels/Level2.tscn")

func go_to_death_screen(character_id: String = "") -> void:
	last_dead_character = character_id
	go_to("res://scenes/ui/DeathScreen.tscn")

func go_to_bad_ending() -> void:
	go_to("res://scenes/ui/BadEnding.tscn")

func go_to_true_ending() -> void:
	go_to("res://scenes/ui/TrueEnding.tscn")
