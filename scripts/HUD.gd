extends CanvasLayer
# HUD — 3 corazones + cuadro de mensajes de historia

signal lives_depleted

const HEART_FULL := preload("res://assets/sprites/ui/heart_full.png")
const HEART_EMPTY := preload("res://assets/sprites/ui/heart_empty.png")

@onready var message_panel: PanelContainer = $MessagePanel
@onready var message_label: Label = $MessagePanel/MessageLabel

var _message_id := 0

func _ready() -> void:
	add_to_group("hud")
	message_panel.visible = false

func update_lives(current: int) -> void:
	for i in range(1, 4):
		var heart: TextureRect = get_node_or_null("Hearts/Heart%d" % i)
		if heart:
			heart.texture = HEART_FULL if i <= current else HEART_EMPTY
	if current <= 0:
		emit_signal("lives_depleted")

## Muestra un mensaje en la parte inferior. Se puede esperar con `await`.
func show_message(text: String, duration := 3.0) -> void:
	_message_id += 1
	var id := _message_id
	message_label.text = text
	message_panel.visible = true
	await get_tree().create_timer(duration).timeout
	# Si llegó otro mensaje mientras tanto, no lo ocultamos
	if id == _message_id:
		message_panel.visible = false
