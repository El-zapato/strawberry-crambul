extends Area2D
# Farol de punto de control — el personaje reaparece aquí al perder una vida

@onready var sprite: Sprite2D = $Sprite2D

var active := false

func _on_body_entered(body: Node) -> void:
	if active or not body.is_in_group("player"):
		return
	active = true
	sprite.frame = 1
	AudioManager.play_sfx("checkpoint")
	body.respawn_point = global_position
