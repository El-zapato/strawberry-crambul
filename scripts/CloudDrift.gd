extends Control
## Mueve una capa de nubes (TextureRect en modo mosaico) lentamente y hace loop.

@export var drift_speed := 12.0         # pixeles por segundo
@export var loop_width := 640.0        # ancho del dibujo que se repite

func _process(delta: float) -> void:
	position.x += drift_speed * delta
	# El rect mide el doble de loop_width, así que al recorrer uno vuelve al inicio
	if position.x >= 0.0:
		position.x -= loop_width
