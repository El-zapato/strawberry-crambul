extends Control

@onready var play_button: Button = $Letter/VBox/PlayButton
@onready var title: TextureRect = $Title
@onready var options_panel: PanelContainer = $OptionsPanel
@onready var music_button: Button = $OptionsPanel/VBox/MusicButton
@onready var sfx_button: Button = $OptionsPanel/VBox/SfxButton

var _time := 0.0
var _title_y := 0.0

func _ready() -> void:
	_refresh_reset_button()
	_title_y = title.position.y
	options_panel.visible = false
	_refresh_options()
	AudioManager.play_music("menu")
	# Para poder navegar el menú con teclado
	play_button.grab_focus()

func _process(delta: float) -> void:
	_time += delta
	title.position.y = _title_y + round(sin(_time * 1.5) * 2.0)

func _on_play_button_pressed() -> void:
	SceneManager.go_to_character_select()

func _on_quit_button_pressed() -> void:
	get_tree().quit()

func _on_options_button_pressed() -> void:
	options_panel.visible = true
	music_button.grab_focus()

func _on_close_options_pressed() -> void:
	options_panel.visible = false
	$Letter/VBox/OptionsButton.grab_focus()

func _on_music_button_pressed() -> void:
	AudioManager.set_music_on(not AudioManager.music_on)
	_refresh_options()

func _on_sfx_button_pressed() -> void:
	AudioManager.set_sfx_on(not AudioManager.sfx_on)
	_refresh_options()

func _refresh_options() -> void:
	music_button.text = "Música: " + ("Sí" if AudioManager.music_on else "No")
	sfx_button.text = "Sonido: " + ("Sí" if AudioManager.sfx_on else "No")

func _refresh_reset_button() -> void:
	# El botón es invisible hasta que todos los personajes han muerto;
	# entonces aparece discreto en la esquina diciendo "Nueva partida"
	var reset: Button = $HiddenReset
	if GameData.all_dead():
		reset.text = "Nueva partida"
		reset.modulate.a = 0.75
	else:
		reset.text = ""
		reset.modulate.a = 0.0

func _on_hidden_reset_pressed() -> void:
	GameData.new_game()
	_refresh_reset_button()
	$ResetLabel.visible = true
	await get_tree().create_timer(1.5).timeout
	$ResetLabel.visible = false
