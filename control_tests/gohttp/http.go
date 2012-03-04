package main

import (
    "fmt"
    "http"
    "log"
)

func handler(w http.ResponseWriter, req *http.Request) {
    w.Header().Set("Content-Type", "text/plain")
    fmt.Fprint(w, "Hello World!")
}

func main() {
    http.HandleFunc("/", handler)
    log.Printf("About to listen on 12345. Go to http://localhost:12345/")
    err := http.ListenAndServe(":12345", nil)
    if err != nil {
        log.Fatal(err)
    }
}
