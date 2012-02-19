package main

import (
    "os"
    "path"
//    "github.com/kuroneko/sqlite3" /* git://github.com/kuroneko/gosqlite3.git */
    "web" /* git://github.com/hoisie/web.go.git */
    "mustache" /* git://github.com/hoisie/mustache.go */
)

func hello() string { return "Hello world!" }
func hellos() string {
    filename := path.Join(path.Join(os.Getenv("PWD"), "tmpl"), "hellos.mustache")
    output := mustache.RenderFile(filename);
    return output
}
//func hellodb() string {
//
//}

func main() {
    web.Get("/", hello)
    web.Get("/hellos", hellos)
//    web.Get("/hellodb", hellodb)
    web.Run("localhost:80")
}
