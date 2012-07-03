Backbone.sync = (method, model, success, error) -> success()


class CouchModel extends Backbone.Model
  idAttribute: "_id"


class CouchCollection extends Backbone.Collection
  model: CouchModel


class StatusView extends Backbone.View
  tagName: 'li'

  render: =>
    @$el.html @model.id
    @


class StatusCollectionView extends Backbone.View

  initialize: =>

    @collection = new CouchCollection
    @collection.bind 'add', @appendItem
    @render()

  appendItem: (item) =>
    view = new StatusView model: item
    @$el.append(view.render().$el)


status_demo = ->
  status_watch.collection.add({'_id': 'fun'})
  return
