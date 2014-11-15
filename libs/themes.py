themes = {
	"light_theme" : {
			"navbar" : "navbar-default",
			"button" : "btn-default"
				},
	"dark_theme" : {
		"navbar" : "navbar-inverse",
		"button" : "btn-inverse"
			}
		}
def get_theme(theme_name):
	theme = themes["light_theme"]
	if theme_name == "dark":
		theme = themes["dark_theme"]
	return theme
