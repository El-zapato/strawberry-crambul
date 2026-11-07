extends Control
# Selección de personaje (como en la propuesta: tarjetas con "Jugar" y "Hoja")
# Los personajes muertos ya no se pueden elegir: solo se ve su cuerpo y su hoja.

const FRAME_IDLE := 0
const FRAME_DEAD := 5

# Nombre, habilidad y breve historia de cada personaje (para la "Hoja").
# El diseño y la personalidad definitivos están pendientes por el equipo.
const CHARACTERS := {
	"character1": {
		"name": "Personaje 1",
		"ability": "Vuelo temporal con su paraguas.",
		"story": "Lleva su carta de confesión bien guardada. Quiere ser el primero en llegar a la colina de la carpintera.",
		"sheet": "res://assets/sprites/characters/character1.png",
	},
	"character2": {
		"name": "Personaje 2",
		"ability": "Ataques a distancia.",
		"story": "No deja que nada ni nadie se interponga entre su carta y la carpintera.",
		"sheet": "res://assets/sprites/characters/character2.png",
	},
	"secret": {
		"name": "Carpintera",
		"ability": "???",
		"story": "Conoce los secretos del puente mejor que nadie.",
		"sheet": "res://assets/sprites/characters/character_secret.png",
	},
}

# Qué tarjeta corresponde a qué personaje; Card3 y Card4 están "Por definir"
const CARD_IDS := {"Card1": "character1", "Card2": "character2", "Card5": "secret"}

@onready var cards: HBoxContainer = $Cards
@onready var status_label: Label = $StatusLabel
@onready var sheet_panel: Control = $SheetPanel

func _ready() -> void:
	if GameData.all_dead():
		SceneManager.go_to_bad_ending()
		return
	AudioManager.play_music("menu")
	sheet_panel.visible = false
	_refresh_ui()

func _refresh_ui() -> void:
	# El personaje secreto solo aparece cuando se desbloquea
	cards.get_node("Card5").visible = GameData.secret_unlocked
	var first_focus: Button = null
	for card_name in CARD_IDS:
		var id: String = CARD_IDS[card_name]
		var card: Control = cards.get_node(card_name)
		var dead := GameData.is_dead(id)
		card.get_node("Portrait").texture = _portrait(id, dead)
		card.get_node("NameLabel").text = CHARACTERS[id]["name"]
		var play: Button = card.get_node("PlayButton")
		# Muerto: ya no se puede jugar, solo ver su hoja
		play.visible = not dead
		if not play.pressed.is_connected(_on_play_pressed):
			play.pressed.connect(_on_play_pressed.bind(id))
			card.get_node("SheetButton").pressed.connect(_on_sheet_pressed.bind(id))
		if first_focus == null and not dead and card.visible:
			first_focus = play

	# Mostrar coleccionables encontrados
	var col := GameData.found_collectibles.size()
	status_label.text = "Fresas encontradas: %d/2" % col
	if first_focus:
		first_focus.grab_focus()

func _portrait(id: String, dead: bool) -> AtlasTexture:
	var tex := AtlasTexture.new()
	tex.atlas = load(CHARACTERS[id]["sheet"])
	tex.region = Rect2((FRAME_DEAD if dead else FRAME_IDLE) * 24, 0, 24, 32)
	return tex

func _on_play_pressed(id: String) -> void:
	SceneManager.current_character = id
	if id == "character2":
		SceneManager.go_to_level2()
	else:
		SceneManager.go_to_level1()

func _on_sheet_pressed(id: String) -> void:
	var data: Dictionary = CHARACTERS[id]
	var dead := GameData.is_dead(id)
	sheet_panel.get_node("Sheet/Portrait").texture = _portrait(id, dead)
	sheet_panel.get_node("Sheet/Info/VBox/NameLabel").text = "Nombre: " + data["name"]
	sheet_panel.get_node("Sheet/Info/VBox/AbilityLabel").text = "Habilidad: " + data["ability"]
	sheet_panel.get_node("Sheet/Info/VBox/StoryLabel").text = \
		"Tuvo su oportunidad." if dead else "Breve historia: " + data["story"]
	sheet_panel.visible = true
	sheet_panel.get_node("Sheet/CloseButton").grab_focus()

func _on_close_sheet_pressed() -> void:
	sheet_panel.visible = false
	_refresh_ui()

func _on_back_button_pressed() -> void:
	SceneManager.go_to_main_menu()
