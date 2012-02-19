class HelloController < ApplicationController
    def hello
        render :text => "Hello World!"
    end
    def hellos
    end
    def hellodb
        @data = Hello.all
    end
end
