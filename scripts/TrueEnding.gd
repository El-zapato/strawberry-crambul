extends Control
# Final Verdadero — todos los coleccionables + personaje secreto completó el juego

func _ready() -> void:
	$BackButton.grab_focus()
	AudioManager.play_music("true_ending")

func _on_back_button_pressed() -> void:
	SceneManager.go_to_main_menu()
