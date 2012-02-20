package main

import (
	"fmt"
	"net/http"
	"text/template"
)

func hello(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "Hello world!")
}

var hellosTemplate = template.Must(template.ParseFiles("tmpl/hellos.tmpl", "tmpl/lipsum.tmpl"))

func hellos(w http.ResponseWriter, r *http.Request) {
	hellosTemplate.Execute(w, nil)
}

func main() {
	http.HandleFunc("/", hello)
	http.HandleFunc("/hellos", hellos)
	http.ListenAndServe(":8080", nil)
}
