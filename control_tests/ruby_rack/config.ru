app = proc do |env|
    [200, { "Content-Type" => "text/plain" }, ["Hello World!"]]
end
run app
