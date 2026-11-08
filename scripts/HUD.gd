extends CanvasLayer
# HUD — 3 corazones + cuadro de mensajes de historia

signal lives_depleted

const HEART_FULL := preload("res://assets/sprites/ui/heart_full.png")
const HEART_EMPTY := preload("res://assets/sprites/ui/heart_empty.png")

@onready var message_panel: PanelContainer = $MessagePanel
@onready var message_label: Label = $MessagePanel/MessageLabel
@onready var pause_panel: Control = $PausePanel

var _message_id := 0

func _ready() -> void:
	add_to_group("hud")
	message_panel.visible = false
	pause_panel.visible = false
	# El HUD sigue recibiendo teclas con el juego en pausa (para quitarla)
	process_mode = Node.PROCESS_MODE_ALWAYS

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if pause_panel.visible:
			_on_continue_pressed()
		else:
			_pause()

func _pause() -> void:
	# No se puede pausar mientras el personaje está muriendo
	var player := get_tree().get_first_node_in_group("player")
	if player and player.get("dying"):
		return
	get_tree().paused = true
	pause_panel.visible = true
	$PausePanel/Panel/VBox/ContinueButton.grab_focus()

func _on_continue_pressed() -> void:
	pause_panel.visible = false
	get_tree().paused = false

func _on_menu_pressed() -> void:
	# Los corazones ya están guardados; al volver se empieza desde el inicio del nivel
	SceneManager.go_to_main_menu()

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
	await get_tree().create_timer(duration, false).timeout
	# Si llegó otro mensaje mientras tanto, no lo ocultamos
	if id == _message_id:
		message_panel.visible = false
