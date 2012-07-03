class JugglerLogger
  constructor: (el) ->
    @el = el

  add_element: (level, message) =>
    ul = $("<ul>")
    ul.addClass(level)
    ul.html(message)
    @el.append(ul)

  @levels: ['debug','info', 'warn', 'error']

  @add_log_level_method: (level) =>
      @::[level] = (message) -> @add_element(level, message)

  for level in @levels
    @add_log_level_method(level)
