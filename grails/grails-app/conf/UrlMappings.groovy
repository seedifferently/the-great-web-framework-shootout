class UrlMappings {

	static mappings = {
		"/"(controller: "hello", action: "string")
		"/string"(controller: "hello", action: "string")
		"/template"(controller: "hello", action: "template")
		"/sql"(controller: "hello", action: "sql")
	}
}
