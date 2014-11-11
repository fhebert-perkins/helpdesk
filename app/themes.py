def get_theme(theme_name):
	theme = {
			"navbar" : "navbar-default",
			"button" : "button-default"
			}
	if theme_name == "dark":
		theme['navbar'] =  "navbar-inverse"
		theme['button'] =  "button-inverse"

	return theme
