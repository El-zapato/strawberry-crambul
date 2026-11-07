extends Area2D
# Coleccionable oculto (fresa)

signal collected(id: String)

@export var collectible_id: String = "collectible1"

var _time := 0.0

@onready var sprite: Sprite2D = $Sprite2D

func _process(delta: float) -> void:
	_time += delta
	sprite.position.y = round(sin(_time * 3.0) * 2.0)

func _on_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		GameData.collect(collectible_id)
		AudioManager.play_sfx("collect")
		collected.emit(collectible_id)
		queue_free()
