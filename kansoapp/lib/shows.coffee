{render} = require "duality/templates"

exports.root = (doc, req) ->
    title: "Main"
    content: render("base.html", req, {})

exports.http_404 = (doc, req) ->
   status: 404
   title: "not found"
   content: render("404.html", req, path: req.path)
