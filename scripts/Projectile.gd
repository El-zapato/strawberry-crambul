extends Area2D
# Proyectil del Personaje 2

const SPEED := 400.0

var direction := Vector2.RIGHT

func _process(delta: float) -> void:
	position += direction * SPEED * delta

func _on_body_entered(body: Node) -> void:
	if body.is_in_group("enemy"):
		body.queue_free()
	queue_free()

func _on_visible_on_screen_notifier_screen_exited() -> void:
	queue_free()
