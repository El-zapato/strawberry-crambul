extends Control

@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var voz_narrador: AudioStreamPlayer = $AudioStreamPlayer

func _ready() -> void:
	# Iniciamos la secuencia automáticamente al cargar la escena
	_reproducir_intro()

func _reproducir_intro() -> void:
	# 1. Reproducimos el audio y la animación al mismo tiempo
	voz_narrador.play()
	animation_player.play("escena1") # Asegúrate de que tu animación se llame "intro"
	
	# 2. Esperamos a que la animación visual termine
	await animation_player.animation_finished
	
	# 3. (Opcional) Si la voz dura más que la animación, esperamos a que termine
	# para que no se corte de golpe. Si la animación es más larga, pasará directo.
	if voz_narrador.playing:
		await voz_narrador.finished
	
	# 4. Guardamos que ya vio la intro y pasamos al menú
	GameData.intro_vista = true
	GameData.save_game()
	get_tree().change_scene_to_file("res://scenes/ui/Intro-juego.tscn")
