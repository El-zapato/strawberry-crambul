extends Node
# Autoload — Persistencia global
# Gestiona muertes, coleccionables y estado del juego guardado en disco

const SAVE_PATH := "user://save.json"

var dead_characters: Array[String] = []
var found_collectibles: Array[String] = []
var secret_unlocked: bool = false

func _ready() -> void:
	load_game()

func kill_character(id: String) -> void:
	if id not in dead_characters:
		dead_characters.append(id)
	save_game()

func is_dead(id: String) -> bool:
	return id in dead_characters

func collect(id: String) -> void:
	if id not in found_collectibles:
		found_collectibles.append(id)
	_check_secret_unlock()
	save_game()

func all_dead() -> bool:
	# Ajustar la lista según los personajes disponibles
	var playable := ["character1", "character2"]
	for c in playable:
		if c not in dead_characters:
			return false
	return true

func _check_secret_unlock() -> void:
	# Desbloquear personaje secreto cuando se recogen todos los coleccionables
	if found_collectibles.size() >= 2:
		secret_unlocked = true

func new_game() -> void:
	dead_characters.clear()
	found_collectibles.clear()
	secret_unlocked = false
	save_game()

func save_game() -> void:
	var data := {
		"dead_characters": dead_characters,
		"found_collectibles": found_collectibles,
		"secret_unlocked": secret_unlocked,
	}
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data))
		file.close()

func load_game() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return
	var text := file.get_as_text()
	file.close()
	var parsed = JSON.parse_string(text)
	if parsed == null:
		return
	# assign() convierte el Array del JSON al Array[String] tipado
	dead_characters.assign(parsed.get("dead_characters", []))
	found_collectibles.assign(parsed.get("found_collectibles", []))
	secret_unlocked = parsed.get("secret_unlocked", false)
