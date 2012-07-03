Backbone.sync = (method, model, success, error) -> success()


class CouchModel extends Backbone.Model
  idAttribute: "_id"


class CouchCollection extends Backbone.Collection
  model: CouchModel

class StatusCollection extends CouchCollection
  comparator: (item) ->
    driver = item.get 'driver'
    if driver
      "#{driver} #{item.id}"
    else
      item.id


class StatusView extends Backbone.View
  tagName: 'li'

  render: =>
    @$el.html @model.id
    if @model.get 'driver'
      @$el.addClass 'driver'
    else
      @$el.addClass 'worker'
    return @


class StatusCollectionView extends Backbone.View

  initialize: =>

    @collection = new StatusCollection
    @collection.bind 'add', @appendItem
    @collection.bind 'reset', @render
    @render()


  render: () =>
    @$el.empty()
    @collection.forEach (item) =>
      @$el.append(item.view.$el)
    @

  appendItem: (item) =>
    view = new StatusView model: item
    item.view = view
    el = view.render().$el
    index = @collection.indexOf(item)
    log.info "index #{index}/#{@collection.length} for item #{item.id} driver #{item.get('driver')}"
    if index == @collection.length-1

      @$el.append(el)
    else
      view = @collection.at(index+1).view
      if view != undefined
        $(el).appendBefore(view.$el)
      else
        @$el.append(el)



status_demo = ->

  status_watch.collection.add([
    {'_id': 'fun', },
    {'_id': 'bee', 'driver': 'fun'},
    {'_id': 'fun2'},
    {'_id': 'bee2', 'driver': 'fun'},
    {'_id': 'bee3', 'driver': 'fun2'},
  ])
  return
