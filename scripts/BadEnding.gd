extends Control
# Final Malo — todos los personajes están muertos

func _ready() -> void:
	$NewGameButton.grab_focus()
	AudioManager.play_music("bad_ending")

func _on_back_button_pressed() -> void:
	SceneManager.go_to_main_menu()

func _on_new_game_button_pressed() -> void:
	# Reinicia todo (muertes y coleccionables) para intentar el final verdadero
	GameData.new_game()
	SceneManager.go_to_main_menu()
