package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"text/template"

	_ "github.com/mattn/go-sqlite3"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "Hello world!")
}

var (
	lipsumTmpl   = template.Must(template.ParseFiles("tmpl/main.tmpl", "tmpl/lipsum.tmpl"))
	databaseTmpl = template.Must(template.ParseFiles("tmpl/main.tmpl", "tmpl/database.tmpl"))
)

func templateHandler(w http.ResponseWriter, r *http.Request) {
	lipsumTmpl.Execute(w, nil)
}

const query = "SELECT id, data FROM hello ORDER BY id ASC"

type Row struct {
	Id   int
	Data string
}

func databaseHandler(w http.ResponseWriter, r *http.Request) {
	db, err := sql.Open("sqlite3", "hello.db")
	if err != nil {
		serveError(w, err)
		return
	}
	defer db.Close()

	rows, err := db.Query(query)
	if err != nil {
		serveError(w, err)
		return
	}
	defer rows.Close()

	var tmplData []*Row
	for rows.Next() {
		var row Row
		err = rows.Scan(&row.Id, &row.Data)
		if err != nil {
			serveError(w, err)
			return
		}
		tmplData = append(tmplData, &row)
	}

	err = databaseTmpl.Execute(w, tmplData)
	if err != nil {
		serveError(w, err)
	}
}

func serveError(w http.ResponseWriter, err error) {
	http.Error(w, "Internal server error", 500)
	log.Println(err)
	return
}

func main() {
	http.HandleFunc("/", helloHandler)
	http.HandleFunc("/template", templateHandler)
	http.HandleFunc("/database", databaseHandler)
	http.ListenAndServe(":8080", nil)
}
