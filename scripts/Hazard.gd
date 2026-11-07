extends Area2D
# Trampa ambiental (pinchos) — quita una vida al tocarla

func _on_body_entered(body: Node) -> void:
	if body.is_in_group("player") and body.has_method("take_damage"):
		body.take_damage()
