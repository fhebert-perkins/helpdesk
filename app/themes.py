def get_theme(theme_name):
	theme = {
			"navbar" : "navbar-default",
			"button" : "btn-default"
			}
	dark_theme = {
		"navbar" : "navbar-inverse",
		"button" : "btn-inverse"
		}
	if theme_name == "dark":
		theme = dark_theme
	return theme
