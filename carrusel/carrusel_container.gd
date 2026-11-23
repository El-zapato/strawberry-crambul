@tool
extends Node2D
class_name CarouselContainer

@export var spacing: float = 20.0

@export var wraparound_enabled: bool = false
@export var wraparound_radius: float = 300.0
@export var wraparound_height: float = 50.0

@export_range(0.0, 1.0) var opacity_strenght: float = 0.35
@export_range(0.0, 1.0) var scale_strenght: float = 0.25
@export_range(0.01, 0.99, 0.01) var scale_min: float = 0.1

@export var smoothing_speed: float = 6.5
@export var selected_index: int = 0
@export var follow_button_focus: bool = false

@export var position_offset_node: Control = null

func _process(delta: float) -> void:
	# Validación inicial
	if !position_offset_node or position_offset_node.get_child_count() == 0:
		return
	
	# Evitar que el índice se salga de los límites
	selected_index = clamp(selected_index, 0, position_offset_node.get_child_count() - 1)
	
	# Recorremos cada hijo del nodo contenedor
	for i in position_offset_node.get_children():
		if wraparound_enabled:
			# Lógica para el efecto de carrusel curvo (Wraparound)
			var max_index_range = max(1, (position_offset_node.get_child_count() - 1) / 2.0)
			var angle = clamp((i.get_index() - selected_index) / max_index_range, -1.0, 1.0) * PI
			var x = sin(angle) * wraparound_radius
			var y = cos(angle) * wraparound_height
			var target_pos = Vector2(x, y - wraparound_height) - i.size / 2.0
			i.position = lerp(i.position, target_pos, smoothing_speed * delta)
		else:
			# Lógica para el efecto de carrusel plano (lineal)
			var position_x = 0.0
			if i.get_index() > 0:
				var prev_node = position_offset_node.get_child(i.get_index() - 1)
				position_x = prev_node.position.x + prev_node.size.x + spacing
			i.position = Vector2(position_x, -i.size.y / 2.0)
			
		# Escalado y opacidad
		i.pivot_offset = i.size / 2.0
		
		# CORREGIDO: get_insex -> get_index
		var target_scale = 1.0 - (scale_strenght * abs(i.get_index() - selected_index))
		target_scale = clamp(target_scale, scale_min, 1.0)
		i.scale = lerp(i.scale, Vector2.ONE * target_scale, smoothing_speed * delta)
		
		var target_opacity = 1.0 - (opacity_strenght * abs(i.get_index() - selected_index))
		target_opacity = clamp(target_opacity, 0.0, 1.0)
		i.modulate.a = lerp(i.modulate.a, target_opacity, smoothing_speed * delta)
		
		# Profundidad (Z-Index)
		if i.get_index() == selected_index:
			i.z_index = 1
		else:
			i.z_index = -abs(i.get_index() - selected_index)
			
		# Cambiar selección con el foco del teclado/mando
		if follow_button_focus and i.has_focus():
			selected_index = i.get_index()
			
	# Centrar todo el contenedor en la pantalla
	if wraparound_enabled:
		position_offset_node.position.x = lerp(position_offset_node.position.x, 0.0, smoothing_speed * delta)
	else:
		# CORREGIDO: get_children(selected_index) -> get_child(selected_index)
		var selected_node = position_offset_node.get_child(selected_index)
		var target_offset_x = -(selected_node.position.x + selected_node.size.x / 2.0)
		position_offset_node.position.x = lerp(position_offset_node.position.x, target_offset_x, smoothing_speed * delta)
