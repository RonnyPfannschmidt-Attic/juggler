{render} = require "duality/templates"

exports.root = (doc, req) ->
    title: "Main"
    content: render("base.html", req, {})
