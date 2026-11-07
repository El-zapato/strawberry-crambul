extends Area2D
# Letrero — muestra un texto de ayuda cuando el jugador se acerca

@export_multiline var text := ""

@onready var label: Label = $Label

func _ready() -> void:
	label.text = text
	label.visible = false

func _on_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		label.visible = true

func _on_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		label.visible = false
