package controllers

import play.api._
import play.api.mvc._
import play.api.db.DB
import anorm._
import play.api.Play.current

object Application extends Controller {
  
  def hello = Action {
    Ok("Hello World!")
  }
  
  def hellos = Action {
    Ok(views.html.hellos())
  }
  
  def helloDb = Action {
    DB.withConnection { implicit c =>
      val rows = SQL("select id, data from hello order by id asc")().map { row =>
        (row[Long]("id"), row[String]("data"))
      }
      Ok(views.html.hellodb(rows))
    }
  }
}