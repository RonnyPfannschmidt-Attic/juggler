from = (from, data) ->
   data.from = from
   return data


module.exports =
  rewrites: [
    from "/", to: "/html/index.html"
    ]

